"""Read-only audit of force-stage BDF1 kinematics and the first Newton RHS.

Scope: uniform mass=1e-6, Rayleigh mass=2, ramped tip load, displacement
coordinates. previous_rhs/solution refer to the linear solve preceding a force
query; they must never be labelled the newly evaluated trial's system.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np

def assess(path,load,ramp,ny):
    calls={}
    for row in csv.DictReader(Path(path).open()):
        calls.setdefault(int(row['call']),[]).append(row)
    blocks=[]
    for rows in calls.values():
        def vector(key):
            return np.array([float(r[key]) if r[key]!='null' else np.nan for r in rows])
        blocks.append(dict(t=float(rows[0]['time']),dt=float(rows[0]['dt']),
                           x=vector('x'),v=vector('v'),f=vector('internal'),
                           rhs=vector('previous_rhs'),dv=vector('previous_solution'),
                           free=np.array([r['constrained']=='0' for r in rows])))
    result=[]
    oldx=oldv=None
    for i,b in enumerate(blocks):
        if i and b['t']==blocks[i-1]['t']:continue
        dt=b['dt'];free=b['free'];mass=1e-6/(len(b['x'])/3)
        # BDF1 initial prediction q_old+dt*v_old, v_old.
        oldv=b['v'];oldx=b['x']-dt*oldv
        force=b['f'].copy()
        force[-3*ny+2::3]+=load*min(1,b['t']/ramp)/ny if ramp>0 else load/ny
        residual=mass*(b['v']-oldv)-dt*(force-2*mass*b['v'])
        entry=dict(time=b['t'],initial_residual_norm=float(np.linalg.norm(residual[free])))
        trials=[q for q in blocks[i:] if q['t']==b['t']]
        entry['max_trial_kinematic_defect']=max(float(np.linalg.norm((q['x']-oldx-dt*q['v'])[free])) for q in trials)
        if i+1<len(blocks) and blocks[i+1]['t']==b['t']:
            nxt=blocks[i+1]
            entry['first_rhs_absolute_error']=float(np.linalg.norm((nxt['rhs']+residual)[free]))
            entry['first_rhs_relative_error']=entry['first_rhs_absolute_error']/max(float(np.linalg.norm(residual[free])),1e-300)
            entry['kinematic_update_error']=float(np.linalg.norm((nxt['x']-oldx-dt*nxt['v'])[free]))
            entry['full_step_velocity_update_error']=float(np.linalg.norm((nxt['v']-b['v']-nxt['dv'])[free]))
        result.append(entry)
    return dict(scope='first correction per step only; not total energy/grasp certification',calls=len(blocks),steps=result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('trace');p.add_argument('--load',type=float,default=1e-6);p.add_argument('--ramp',type=float,default=10);p.add_argument('--ny',type=int,default=5);a=p.parse_args()
    print(json.dumps(assess(a.trace,a.load,a.ramp,a.ny),indent=2))
