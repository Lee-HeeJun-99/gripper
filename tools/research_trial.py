"""Independent experimental bilayer SOFA runner. Never changes legacy scenes/gates.

Generalized length only; equivalent circular A/I remain the original research beam.
EXPERIMENTAL even when numerical gates pass; not calibrated PET or vacuum physics.
"""
import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from native_scene import generate
from run_trial import execute_process
from verification_common import ROOT,SOFA,BUILD,sha,provenance,write_json,assert_build_current
from trial_validation import read_states,TrialError,validate_config

FINITE=ROOT/'build/next_finite_rotation/libReGripFiniteRotation.so'

def model_hashes():
    return {str(p.relative_to(ROOT)):sha(p) for folder in ('models','experiments') for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.cpp','.h','.json','.txt')}

def scene(out,length,n,k,load,dt,finite,connectors):
    generate(out/'scene.scn',dt,load,k,connectors,n)
    tree=ET.parse(out/'scene.scn');root=tree.getroot();root.set('name','EXPERIMENTAL_BILAYER')
    for obj in root.iter('MechanicalObject'):
        width=7 if obj.get('template')=='Rigid3d' else 3
        pos=list(map(float,obj.get('position').split()))
        for i in range(0,len(pos),width):pos[i]*=length/30
        obj.set('position',' '.join(map(str,pos)))
    if finite:
        solver=root.find('SparseLDLSolver');solver.tag='EigenSparseLU';solver.attrib.pop('template',None)
        ff=root.find('.//TangentialRigidForceField');ff.tag='FiniteRotationShear'
        ff.set('height',ff.attrib.pop('layerThickness'));ff.attrib.pop('includeRoot')
    ET.indent(root);tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)

def assess(out,c,result,log):
    n=c['n'];steps=round(c['duration']/c['dt']);L=c['length_mm'];F=c['load'];dt=c['dt']
    if result['process_status']!='exited' or result['exit_code']!=0 or any(s in log for s in ('[ERROR]','Traceback','SIGABRT')):raise TrialError('FAIL','SOFA process or error log')
    if f'{steps} iterations done' not in log:raise TrialError('FAIL','completion marker absent')
    rigid=read_states(out/'rigid.txt');points=read_states(out/'interface.txt')
    if len(rigid)!=steps+1 or len(points)!=steps+1:raise TrialError('FAIL','wrong sample count')
    initial=rigid[0]['X'];rows=[]
    for j,(r,p) in enumerate(zip(rigid,points)):
        x=r.get('X',[]);v=r.get('V',[]);res=r.get('R',[]);pts=p.get('X',[])
        if len(x)!=14*n or len(v)!=12*n or len(pts)!=6*n or len(p.get('V',[]))!=6*n:raise TrialError('FAIL','state size')
        if not all(math.isfinite(a) for a in x+v+pts+p['V']+[r['time'],p['time']]):raise TrialError('FAIL','nonfinite state')
        if abs(r['time']-j*dt)>1e-9 or abs(r['time']-p['time'])>1e-12:raise TrialError('FAIL','sample times')
        if any(abs(x[7*i+a]-initial[7*i+a])>1e-10 for i in (0,n) for a in range(7)):raise TrialError('FAIL','root moved')
        angles=[];map_error=0
        for i in range(2*n):
            q=x[7*i+3:7*i+7];a=2*math.atan2(math.sqrt(sum(v*v for v in q[:3])),abs(q[3]));angles.append(a)
            if abs(sum(v*v for v in q)-1)>1e-8:raise TrialError('FAIL','quaternion norm')
            if not c['finite_rotation'] and (a>=.005 or max(abs(q[0]),abs(q[2]))>1e-8):raise TrialError('FAIL','legacy planar domain exceeded')
            z=.2 if i<n else -.2
            offset=[2*(q[0]*q[2]+q[1]*q[3])*z,2*(q[1]*q[2]-q[0]*q[3])*z,(1-2*(q[0]*q[0]+q[1]*q[1]))*z]
            map_error=max(map_error,max(abs(pts[3*i+a]-x[7*i+a]-offset[a]) for a in range(3)))
        if map_error>1e-10:raise TrialError('FAIL','mapping mismatch')
        if j==0:continue
        if len(res)!=12*n or not all(map(math.isfinite,res)):raise TrialError('FAIL','invalid residual')
        free=[i for i in range(2*n) if i not in (0,n)]
        rf=max(abs(res[6*i+a]) for i in free for a in range(3));rt=max(abs(res[6*i+a]) for i in free for a in range(3,6))
        tip=-sum(x[7*i+2]-initial[7*i+2] for i in (n-1,2*n-1))/2
        rows.append(dict(time=r['time'],tip=tip,residual=max(rf/(F/2),rt/(F*L/2)),
            velocity=max(abs(v[6*i+a]) for i in free for a in range(3)),
            angular_velocity=max(abs(v[6*i+a]) for i in free for a in range(3,6)),
            rotation=max(angles),x_slip=max(abs(pts[3*(n+i)]-pts[3*i]) for i in range(1,n))))
    tail=rows[-max(2,round(.1/dt)):];last=rows[-1]
    drift=(max(r['tip'] for r in tail)-min(r['tip'] for r in tail))/max(abs(last['tip']),1e-10)
    eq=max(r['velocity'] for r in tail)<1e-5 and max(r['angular_velocity'] for r in tail)<1e-5 and max(r['residual'] for r in tail)<1e-3 and drift<1e-4
    import csv
    with (out/'timeseries.csv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(last));writer.writeheader();writer.writerows(rows)
    return dict(status='PASS' if eq else 'not_converged',equilibrium=eq,tip_deflection_mm=last['tip'],max_x_slip_mm=last['x_slip'],
        relative_residual=last['residual'],max_rotation_rad=max(r['rotation'] for r in rows),final_velocity=last['velocity'],tail_drift=drift,
        effective_stiffness=F/last['tip'] if eq and last['tip']>0 else None,samples=steps)

def run(out,length=100,n=11,k=1,load=1e-6,dt=.0005,duration=6,finite=False,connectors=None):
    steps=validate_config(k,connectors,dt,duration,load,n,180)
    if steps>120000:raise ValueError('research resource bound: at most 120000 steps')
    if not all(math.isfinite(v) and v>0 for v in (length,load,dt,duration)) or length>150 or duration>60 or n>41:raise ValueError('bounded research range exceeded')
    assert_build_current();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    config=dict(model_version='objective-3d-0.1' if finite else 'planar-length-extension-0.1',length_mm=length,n=n,k=k,load=load,
        dt=dt,duration=duration,finite_rotation=finite,material='unchanged equivalent circular section, E250, not PET calibration',
        height_mm=.4,total_mass=2e-5,solver='EigenSparseLU' if finite else 'SparseLDL',rayleigh_mass=.2,rayleigh_stiffness=.1,
        boundary='clamped roots; equal vertical tip loads',connector_indices=connectors,
        connector_positions_mm=[length*i/(n-1) for i in (range(1,n) if connectors is None else connectors)])
    write_json(out/'config.json',config);scene(out,length,n,k,load,dt,finite,connectors)
    plugin=FINITE if finite else BUILD/'plugin/bin/libSofaTangentialV110.so';diag=BUILD/'diagnostics/libReGripDiagnostics.so'
    if finite:
        manifest=json.loads((FINITE.parent/'manifest.json').read_text())
        for path,digest in manifest['sources'].items():
            if sha(ROOT/path)!=digest:raise RuntimeError('experimental build source mismatch')
        if sha(FINITE)!=manifest['binary']:raise RuntimeError('experimental binary mismatch')
    cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n',str(round(duration/dt)),
        '--hideProgressBar','-l',str(diag),'-l',str(plugin),str(out/'scene.scn')]
    write_json(out/'command.json',cmd)
    report=dict(config=config,provenance=provenance(),model_source_sha256=model_hashes(),runner_sha256=sha(__file__),
        binary_sha256={str(plugin):sha(plugin),str(diag):sha(diag)},scope='EXPERIMENTAL simulation; no real gripper validation',status='incomplete')
    write_json(out/'metrics.json',report)
    result=execute_process(cmd,out,180);report.update(result)
    log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    try:report.update(assess(out,config,result,log))
    except (TrialError,ValueError,OSError,KeyError) as e:report.update(status='FAIL',failure_reason=str(e),equilibrium=False,effective_stiffness=None)
    report['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='metrics.json'}
    write_json(out/'metrics.json',report);print(out.name,report['status'],report.get('tip_deflection_mm'),flush=True);return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('out',type=Path)
    p.add_argument('--length',type=float,default=100);p.add_argument('--k',type=float,default=1);p.add_argument('--load',type=float,default=1e-6)
    p.add_argument('--nodes',type=int,default=11);p.add_argument('--duration',type=float,default=6);p.add_argument('--dt',type=float,default=.0005);p.add_argument('--finite',action='store_true');p.add_argument('--connectors',type=int,nargs='+');a=p.parse_args()
    r=run(a.out,a.length,a.nodes,a.k,a.load,a.dt,a.duration,a.finite,a.connectors);raise SystemExit(0 if r['status']=='PASS' else 1)
