"""Exact closest gap on saved-center CHORD paths;NOT actual SOFA swept CCD."""
import argparse,csv,json,itertools
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha,cable_node

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');groups=[];times=None;inputs={}
 for f in range(3):
  path=src/f'finger{f}.csv';rows=list(csv.DictReader(path.open()));t=np.r_[0.,[float(r['time_s']) for r in rows]]
  if times is None:times=t
  else:assert np.array_equal(times,t)
  for j in (0,1):
   node=cable_node(tree,f,j);initial=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);q=np.array([initial]+[np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in rows]);groups.append((f,j,q,float(node.find('SphereCollisionModel').get('radius'))))
  inputs[path.name]=sha(path)
 worst=None;trace=np.full(len(times)-1,np.inf)
 for (f,j,q,R),(g,k,r,S) in itertools.combinations(groups,2):
  if f==g:continue
  start=q[:-1,:,None]-r[:-1,None,:];end=q[1:,:,None]-r[1:,None,:];delta=end-start;den=np.sum(delta*delta,axis=3);u=np.clip(np.divide(-np.sum(start*delta,axis=3),den,out=np.zeros_like(den),where=den>0),0,1);gap=np.linalg.norm(start+u[:,:,:,None]*delta,axis=3)-R-S;trace=np.minimum(trace,gap.min(axis=(1,2)));idx=np.unravel_index(np.argmin(gap),gap.shape)
  if worst is None or gap[idx]*1000<worst['gap_mm']:
   step,i,l=idx;worst=dict(finger0=f,cable0=j,guide_index0=int(i),finger1=g,cable1=k,guide_index1=int(l),begin_s=float(times[step]),end_s=float(times[step+1]),chord_fraction=float(u[idx]),gap_mm=float(gap[idx]*1000))
 with (out/'chord_gap.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['interval_end_s','chord_minimum_gap_mm']);w.writerows(zip(times[1:],trace*1000))
 result=dict(status='CHORD_PATH_DIAGNOSTIC_ONLY',case=a.case,scope='Linear interpolation of mapped guide centers between actual saved states,including initial frame. NOT rigid quaternion interpolation,Native intermediate states,true trajectory,full solid supports or swept CCD certification.',worst=worst,negative_chord_intervals=int(np.count_nonzero(trace<0)),source_sha256=sha(Path(__file__)),inputs={**inputs,'scene.scn':sha(src/'scene.scn')})
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
