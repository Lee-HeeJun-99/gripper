"""Isolated native SOFA trials; completion and equilibrium are distinct states."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import resource
import subprocess
import time
from baseline_regression import ROOT, SOFA, states
from native_scene import generate


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_trial(out, k=None, connectors=None, dt=0.0005, duration=3., load=0.0001, n=11, timeout=60):
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError('refusing stale run directory: '+str(out))
    if dt <= 0 or duration <= 0 or load <= 0 or n < 3 or (k is not None and k < 0):
        raise ValueError('invalid configuration')
    steps = round(duration/dt)
    if abs(steps*dt-duration)>1e-10:
        raise ValueError('duration must be an integer number of steps')
    generate(out/'scene.scn', dt, load, k, connectors, n)
    diag = ROOT/'build/diagnostics/libReGripDiagnostics.so'
    plugin = ROOT/'build/plugin/bin/libSofaTangentialV110.so'
    command = [str(SOFA/'bin/runSofa-26.06.00'), '--noautoload', '--tmp', '-g', 'batch', '-a',
               '-n', str(steps), '--hideProgressBar', '-l', str(diag)]
    if k is not None:
        command += ['-l', str(plugin)]
    command += [str(out/'scene.scn')]
    config = dict(k=k, connectors=connectors, dt=dt, duration=duration, load=load, n=n, timeout=timeout,
                  length_mm=30, layer_thickness_mm=.4, young_modulus=250, poisson_ratio=.32,
                  total_mass=2e-5, force_units='model force units; not calibrated to physical PET', seed=11)
    (out/'config.json').write_text(json.dumps(config, indent=2))
    report = dict(config=config, status='crash', failure_reason='', exit_code=None,
                  plugin_sha256=sha(plugin) if k is not None else None,
                  diagnostics_sha256=sha(diag), scene_sha256=sha(out/'scene.scn'),
                  sofa_version='26.06.00', equilibrium_validated=False, effective_stiffness=None)
    report['git_commit']=subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],capture_output=True,text=True).stdout.strip()
    report['working_tree_dirty']=bool(subprocess.run(['git','-C',str(ROOT),'status','--porcelain'],capture_output=True,text=True).stdout)
    start = time.monotonic()
    with (out/'sofa.log').open('w') as log:
        def limits():
            resource.setrlimit(resource.RLIMIT_AS, (4*1024**3,4*1024**3))
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True, preexec_fn=limits)
        try:
            report['exit_code'] = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            report.update(status='timeout', failure_reason='wall time limit')
    report['runtime_s']=time.monotonic()-start
    (out/'command.json').write_text(json.dumps(command, indent=2))
    log=(out/'sofa.log').read_text()
    try:
        if report['status']=='timeout':
            raise ValueError('timeout')
        if report['exit_code'] != 0 or '[ERROR]' in log or 'SIGABRT' in log:
            raise ValueError('SOFA error or abnormal exit')
        if f'{steps} iterations done' not in log:
            raise ValueError('missing completion marker')
        if k is not None and any(marker not in log for marker in ('REGRIP_ADD_FORCE','REGRIP_BUILD_STIFFNESS')):
            raise ValueError('native ForceField force/matrix path was not exercised')
        rigid, points=states(out/'rigid.txt'), states(out/'interface.txt')
        if len(rigid)!=steps+1 or len(points)!=steps+1:
            raise ValueError('incomplete state output')
        rows=[]
        for r,p in zip(rigid[1:],points[1:]):
            x,v,pts,residual=r['X'],r['V'],p['X'],r.get('R',[])
            if len(x)!=14*n or len(v)!=12*n or len(pts)!=6*n or len(residual)!=12*n:
                raise ValueError('invalid state size or missing residual')
            if abs(r['time']-p['time'])>1e-12:
                raise ValueError('state time mismatch')
            if not all(math.isfinite(a) for a in x+v+pts+residual):
                report['status']='diverged'
                raise ValueError('nonfinite state')
            tip=-.5*((x[7*(n-1)+2]+.2)+(x[7*(2*n-1)+2]-.2))
            if abs(tip)>1 or max(abs(a) for a in v)>1e5:
                report['status']='diverged'
                raise ValueError('displacement/velocity safety bound')
            angle=max(2*math.asin(min(1,math.sqrt(sum(x[7*i+j]**2 for j in (3,4,5))))) for i in range(2*n))
            offplane=max(abs(x[7*i+j]) for i in range(2*n) for j in (3,5))
            if angle>.005 or offplane>1e-8:
                report['status']='invalid_physics'
                raise ValueError('outside validated small-angle planar domain')
            selected=connectors if connectors is not None else list(range(1,n))
            slips=[x[7*(n+i)]-x[7*i]-.4*(x[7*(n+i)+4]+x[7*i+4]) for i in selected]
            # All-node interface slip is a design objective, including unconnected nodes.
            sx=max(abs(pts[3*(n+i)]-pts[3*i]) for i in range(1,n))
            free_nodes=[i for i in range(2*n) if i not in (0,n)]
            residual_force=max(abs(residual[6*i+j]) for i in free_nodes for j in range(3))
            residual_torque=max(abs(residual[6*i+j]) for i in free_nodes for j in range(3,6))
            relative_residual=max(residual_force/(load/2),residual_torque/(load*30/2))
            row=dict(time_s=r['time'],tip_deflection_mm=tip,
                     tip_velocity_z_mm_s=.5*(v[6*(n-1)+2]+v[6*(2*n-1)+2]),
                     max_x_slip_mm=sx,max_connector_shear_mm=max(abs(a) for a in slips),
                     shear_energy=.5*(k or 0)*sum(a*a for a in slips),
                     max_velocity=max(abs(v[6*i+j]) for i in free_nodes for j in range(3)),
                     residual_force=residual_force,residual_torque=residual_torque,
                     relative_residual=relative_residual,max_rotation_rad=angle)
            rows.append(row)
        if abs(rows[-1]['time_s']-duration)>1e-9:
            raise ValueError('wrong simulation time')
        with (out/'timeseries.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        tail=rows[-max(2,round(min(.1,duration/4)/dt)):]
        drift=(max(r['tip_deflection_mm'] for r in tail)-min(r['tip_deflection_mm'] for r in tail))/max(abs(rows[-1]['tip_deflection_mm']),1e-10)
        equilibrium=max(r['max_velocity'] for r in tail)<1e-5 and max(r['relative_residual'] for r in tail)<1e-3 and drift<1e-4
        report.update(rows[-1])
        report.update(status='complete' if equilibrium else 'not_converged', equilibrium_validated=equilibrium,
                      tail_relative_drift=drift, samples=steps,
                      effective_stiffness=load/rows[-1]['tip_deflection_mm'] if equilibrium else None)
        if not equilibrium:
            report['failure_reason']='static equilibrium criteria not met (v<1e-5, residual<1e-3, tail drift<1e-4)'
    except (ValueError,KeyError,OSError) as exc:
        report['failure_reason']=str(exc)
    (out/'metrics.json').write_text(json.dumps(report,indent=2))
    print(out.name,report['status'],'tip=',report.get('tip_deflection_mm'),'residual=',report.get('relative_residual'),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('out');parser.add_argument('--k',type=float)
    parser.add_argument('--dt',type=float,default=.0005);parser.add_argument('--duration',type=float,default=3.)
    parser.add_argument('--connectors',type=int,nargs='+');parser.add_argument('--nodes',type=int,default=11)
    parser.add_argument('--load',type=float,default=.0001);parser.add_argument('--timeout',type=float,default=60.)
    a=parser.parse_args()
    result=run_trial(a.out,a.k,a.connectors,a.dt,a.duration,a.load,a.nodes,a.timeout)
    raise SystemExit(0 if result['status']=='complete' else 1)
