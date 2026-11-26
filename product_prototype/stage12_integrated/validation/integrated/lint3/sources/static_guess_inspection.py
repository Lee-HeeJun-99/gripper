"""Inspect an interrupted STATIC optimizer guess without changing its state.

No successful execution/physical equilibrium is inferred from a saved callback.
Independent geometry and force certificates may subsequently inspect this state.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,ref,dump
import finite_pet_coupon as geometric

def main():
    p=argparse.ArgumentParser();p.add_argument('--checkpoint',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/a.checkpoint
    if not source.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Unsafe checkpoint path')
    d=json.loads(source.read_text());L=d['PET_free_length_m'];geometric.L=L;rows=[]
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    for old in d['rows']:
        q=np.asarray(old['state_angles_rad'],dtype=float);n=old['n'];h=L/n;theta=math.radians(old['fixture_angle_deg']);R=.088/theta
        if len(q)!=n or not np.isfinite(q).all():raise ValueError('Invalid stored state')
        da=np.diff(np.r_[0.,q]);u=1j*.00025+np.sum(h*np.sinc(da/(2*np.pi))*np.exp(1j*(np.r_[0.,q][:-1]+q)/2))
        world=np.array([.0504-u.imag,-.007-u.real]);arc=R*math.atan2(-world[1]-.007,world[0]-(.0504-R))
        EI=507000*6894.757293168*(.024-.012*(.007+(np.arange(n)+.5)*h)/.100)*.0003**3/12
        rows.append(dict(old,energy_J=float(np.sum(EI*da**2/(2*h))),axial_migration_m=float(arc-L),continuous_min_gap_m=float(geometric.continuous_gap(q,n,R).min()),status='INTERRUPTED_STATIC_GUESS_NOT_QUALIFIED',state_changed=False))
    result=dict(status='INTERRUPTED_NO_COMPLETED_SOLVE',scope='READ-ONLY STATIC INITIAL-GUESS INSPECTION; NOT NATIVE OR EQUILIBRIUM PASS',rows=rows,PET_free_length_m=L,candidate=d['candidate'],source=ref(source),producer=ref(out/'producer.py'),geometry_implementation=ref(Path(geometric.__file__)),product_release=False,interruption_exit_code=None,interruption_reason='Prior exec session no longer exists and no final summary was saved; exact termination cause not captured',completed_exchange_history=d.get('history',[]))
    dump(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','interruption_reason','rows')},indent=2))
if __name__=='__main__':main()
