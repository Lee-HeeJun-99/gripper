"""Exact material-coordinate transfer of a piecewise circular STATIC guess.
No dynamic checkpoint, no physical position correction, no inherited PASS.
"""
import argparse,ast,json,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,ref,dump
import rod_point_jacobian as rod
def energy(q,L):
    n=len(q);h=L/n;w=.024-.012*(.007+(np.arange(n)+.5)*h)/.100;EI=507000*6894.757293168*w*.0003**3/12
    return float(np.sum(EI*np.diff(np.r_[0.,q])**2/(2*h)))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--input',required=True);p.add_argument('--old-n',type=int,required=True);p.add_argument('--new-n',type=int,required=True);a=p.parse_args();out=ROOT/'models/contact'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/finger'/a.input/'summary.json';d=json.loads(source.read_text());old=next(r for r in d['rows'] if r['n']==a.old_n);L=d['PET_free_length_m'];q=np.array(old['state_angles_rad']);nn=a.new_n
    if nn<=len(q) or nn%len(q):raise ValueError('Only integer refinement of the same material-coordinate rod')
    v=np.interp(np.arange(nn+1)/nn,np.arange(len(q)+1)/len(q),np.r_[0.,q])[1:];factor=nn//len(q)
    error=float(max(abs(rod.prepare(q,L)[1]-rod.prepare(v,L)[1][::factor])));ee=abs(energy(q,L)-energy(v,L))/energy(q,L)
    points={(i,side):[0.,1.,*((np.polynomial.legendre.leggauss(3)[0]+1)/2).tolist()] for i in range(nn) for side in (-1,1)};material_error=0.
    for key,ts in old['material_contact_points'].items():
        i,side=ast.literal_eval(key)
        for t in ts:
            coordinate=(i+t)/len(q);j=min(nn-1,int(math.floor(coordinate*nn)));local=coordinate*nn-j;points[(j,side)].append(local);material_error=max(material_error,abs((j+local)/nn-coordinate)*L)
    assert error<1e-12 and ee<1e-12 and material_error<1e-14
    row=dict(n=nn,fixture_angle_deg=old['fixture_angle_deg'],state_angles_rad=v.tolist(),material_contact_points={str(k):sorted(set(ts)) for k,ts in points.items()},status='STATIC_OPTIMIZER_GUESS_ONLY')
    result=dict(status='SEED_TRANSFER_CONTRACT_PASS',scope='STATIC GUESS GEOMETRY/ENERGY/MATERIAL COORDINATE TRANSFER ONLY',rows=[row],PET_free_length_m=L,candidate=d['candidate'],source=ref(source),producer=ref(out/'producer.py'),geometry_implementation=ref(Path(rod.__file__)),node_position_error_m=error,energy_relative_error=ee,material_coordinate_error_m=material_error,physical_equilibrium=False,dynamic_equivalence=False)
    dump(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','node_position_error_m','energy_relative_error','material_coordinate_error_m','physical_equilibrium','dynamic_equivalence')},indent=2))
if __name__=='__main__':main()
