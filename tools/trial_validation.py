"""Strict result validation; no result is synthesized or read from older trials."""
import csv
import json
import math
from pathlib import Path
from verification_common import sha


class TrialError(ValueError):
    def __init__(self,status,reason):
        super().__init__(reason);self.status=status


def read_states(path):
    records=[]
    with Path(path).open() as stream:
        for number,line in enumerate(stream,1):
            if not line.strip():continue
            if '=' not in line:raise TrialError('crash',f'malformed state line {number}')
            key,value=(part.strip() for part in line.split('=',1))
            if key=='T':
                records.append({'time':float(value)})
            elif key in ('X','V','R') and records and key not in records[-1]:
                records[-1][key]=list(map(float,value.split()))
            else:raise TrialError('crash',f'unknown/duplicate state field at line {number}')
    if not records:raise TrialError('crash','empty state output')
    return records


def validate_config(k,connectors,dt,duration,load,n,timeout):
    scalars=[dt,duration,load,timeout]+([] if k is None else [k])
    if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in scalars):
        raise ValueError('configuration must contain finite numbers')
    if min(dt,duration,load,timeout)<=0 or (k is not None and k<0):raise ValueError('invalid configuration')
    if type(n) is not int or n<3:raise ValueError('nodes must be an integer >=3')
    if connectors is not None:
        if not connectors or any(type(i) is not int or not 1<=i<n for i in connectors) or len(set(connectors))!=len(connectors):
            raise ValueError('connectors must be unique non-root node indices')
    steps=round(duration/dt)
    if steps<1 or abs(steps*dt-duration)>1e-10:raise ValueError('duration must be an integer number of steps')
    return steps


def analyze(out,config,exit_code,log):
    out=Path(out);n=config['n'];dt=config['dt'];load=config['load'];k=config['k']
    steps=round(config['duration']/dt)
    if exit_code!=0 or '[ERROR]' in log or 'SIGABRT' in log or 'Traceback' in log:
        raise TrialError('crash','SOFA error log or abnormal exit')
    if f'{steps} iterations done' not in log:raise TrialError('crash','missing completion marker')
    if k is not None and any(marker not in log for marker in ('REGRIP_ADD_FORCE','REGRIP_BUILD_STIFFNESS')):
        raise TrialError('crash','native force/matrix path not exercised')
    rigid=read_states(out/'rigid.txt');points=read_states(out/'interface.txt')
    if len(rigid)!=steps+1 or len(points)!=steps+1:raise TrialError('crash','incomplete state output')
    if len(rigid[0].get('X',[]))!=14*n:raise TrialError('crash','invalid initial mechanical state')
    initial=rigid[0]['X'];rows=[]
    for step,(r,p) in enumerate(zip(rigid,points)):
        x,v,pts,pv=r.get('X',[]),r.get('V',[]),p.get('X',[]),p.get('V',[])
        if len(x)!=14*n or len(v)!=12*n or len(pts)!=6*n or len(pv)!=6*n:raise TrialError('crash','invalid state dimensions')
        if not all(math.isfinite(a) for a in x+v+pts+pv+[r['time'],p['time']]):raise TrialError('diverged','nonfinite state')
        if abs(r['time']-step*dt)>1e-9 or abs(r['time']-p['time'])>1e-12:
            raise TrialError('crash','wrong/nonmonotonic sample times')
        if any(abs(x[7*i+j]-initial[7*i+j])>1e-10 for i in (0,n) for j in range(7)):
            raise TrialError('invalid_physics','clamped root moved')
        if max(math.sqrt(sum((x[7*i+j]-initial[7*i+j])**2 for j in range(3))) for i in range(2*n))>1 or max(map(abs,v))>1e5:
            raise TrialError('diverged','displacement/velocity safety bound')
        angles=[];map_error=0.
        for i in range(2*n):
            q=x[7*i+3:7*i+7];norm=sum(a*a for a in q)
            angle=2*math.atan2(math.sqrt(sum(a*a for a in q[:3])),q[3])
            if abs(norm-1)>1e-8 or q[3]<=0 or max(abs(q[0]),abs(q[2]))>1e-8 or angle>=.005:
                raise TrialError('invalid_physics','outside validated small-angle planar domain')
            angles.append(angle)
            rz=.2 if i<n else -.2
            offset=[2*(q[0]*q[2]+q[1]*q[3])*rz,2*(q[1]*q[2]-q[0]*q[3])*rz,(1-2*(q[0]*q[0]+q[1]*q[1]))*rz]
            map_error=max(map_error,max(abs(pts[3*i+j]-x[7*i+j]-offset[j]) for j in range(3)))
        if map_error>1e-10:raise TrialError('invalid_physics','RigidMapping state does not match rigid transforms')
        if step==0:continue
        residual=r.get('R',[])
        if len(residual)!=12*n:raise TrialError('crash','missing/malformed static residual')
        if not all(map(math.isfinite,residual)):raise TrialError('diverged','nonfinite static residual')
        tip=-.5*((x[7*(n-1)+2]-initial[7*(n-1)+2])+(x[7*(2*n-1)+2]-initial[7*(2*n-1)+2]))
        selected=config['connectors'] if config['connectors'] is not None else list(range(1,n))
        slips=[x[7*(n+i)]-x[7*i]-.4*(math.atan2(x[7*i+4],x[7*i+6])+math.atan2(x[7*(n+i)+4],x[7*(n+i)+6])) for i in selected]
        free=[i for i in range(2*n) if i not in (0,n)]
        rf=max(abs(residual[6*i+j]) for i in free for j in range(3))
        rt=max(abs(residual[6*i+j]) for i in free for j in range(3,6))
        reaction_z=-sum(residual[6*i+2] for i in (0,n))
        reaction_y=-sum(residual[6*i+4]+x[7*i+2]*residual[6*i]-x[7*i]*residual[6*i+2] for i in (0,n))
        applied_y=load/2*(x[7*(n-1)]+x[7*(2*n-1)])
        row=dict(time_s=r['time'],tip_deflection_mm=tip,tip_velocity_z_mm_s=.5*(v[6*(n-1)+2]+v[6*(2*n-1)+2]),
                 max_x_slip_mm=max(abs(pts[3*(n+i)]-pts[3*i]) for i in range(1,n)),
                 max_connector_shear_mm=max(map(abs,slips)),shear_energy=.5*(k or 0)*sum(a*a for a in slips),
                 max_velocity=max(abs(v[6*i+j]) for i in free for j in range(3)),
                 max_angular_velocity=max(abs(v[6*i+j]) for i in free for j in range(3,6)),
                 residual_force=rf,residual_torque=rt,relative_residual=max(rf/(load/2),rt/(load*30/2)),
                 max_rotation_rad=max(angles),mapping_error=map_error,
                 reaction_force_balance=abs(reaction_z-load)/load,reaction_moment_balance=abs(reaction_y+applied_y)/(load*30))
        if not all(map(math.isfinite,row.values())):raise TrialError('diverged','derived metric overflow')
        rows.append(row)
    with (out/'timeseries.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    tail=rows[-max(2,round(min(.1,config['duration']/4)/dt)):]
    drift=(max(r['tip_deflection_mm'] for r in tail)-min(r['tip_deflection_mm'] for r in tail))/max(abs(rows[-1]['tip_deflection_mm']),1e-10)
    equilibrium=(max(r['max_velocity'] for r in tail)<1e-5 and max(r['max_angular_velocity'] for r in tail)<1e-5
                 and max(r['relative_residual'] for r in tail)<1e-3 and drift<1e-4)
    if equilibrium and rows[-1]['tip_deflection_mm']<=0:raise TrialError('invalid_physics','nonpositive equilibrium deflection')
    return dict(**rows[-1],status='complete' if equilibrium else 'not_converged',equilibrium_validated=equilibrium,
                samples=steps,tail_relative_drift=drift,execution_completed=True,
                failure_reason='' if equilibrium else 'static equilibrium criteria not met',
                effective_stiffness=load/rows[-1]['tip_deflection_mm'] if equilibrium else None)


def verify_artifacts(out):
    out=Path(out);report=json.loads((out/'metrics.json').read_text())
    for filename,digest in report.get('artifact_sha256',{}).items():
        if not (out/filename).is_file() or sha(out/filename)!=digest:raise TrialError('crash','missing or corrupted artifact: '+filename)
    if not report.get('artifact_sha256'):raise TrialError('crash','missing artifact manifest')
    if report['execution_completed']:
        with (out/'timeseries.csv').open() as stream:rows=list(csv.DictReader(stream))
        if len(rows)!=report['samples']:raise TrialError('crash','CSV sample count mismatch')
    return report
