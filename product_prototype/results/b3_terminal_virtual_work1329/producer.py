"""Independent initial cable-length gradient;not observed Native impulse."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def length(q,p,ids):return np.linalg.norm(np.diff(np.vstack([p,q[ids]]),axis=0),axis=1).sum()
def gradient(q,p,ids):
 chain=np.vstack([p,q[ids]]);u=np.diff(chain,axis=0);u/=np.linalg.norm(u,axis=1)[:,None];g=np.zeros_like(q)
 for k,i in enumerate(ids):g[i]+=u[k]-(u[k+1] if k+1<len(u) else 0)
 return g
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for name in ('b3_railback_grasp1001298','b3_proximal_terminal1326'):
  scene=BASE/'results'/name/'scene.scn';root=ET.parse(scene).getroot()
  for finger in range(3):
   for side in range(2):
    n=root.find(f"./Node[@name='guides{finger}']/Node[@name='cable{side}']");q=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);c=n.find('CableConstraint');ids=np.fromstring(c.get('indices'),sep=' ',dtype=int);pull=np.fromstring(c.get('pullPoint'),sep=' ');g=gradient(q,pull,ids);fd=np.zeros_like(q);h=1e-7
    for i in range(len(q)):
     for j in range(3):
      plus=q.copy();minus=q.copy();plus[i,j]+=h;minus[i,j]-=h;fd[i,j]=(length(plus,pull,ids)-length(minus,pull,ids))/(2*h)
    err=float(abs(fd-g).max());assert err<1e-7
    records.append(dict(case=name,finger=finger,cable=side,initial_length_m=length(q,pull,ids),ideal_force_N=(-1.5*g).tolist(),last_98mm_guide_force_norm_N=float(np.linalg.norm(1.5*g[-1])),gradient_FD_max_abs_error=err,scene_sha256=sha(scene)))
 result=dict(status='INITIAL_LENGTH_GRADIENT_FD_PASS',records=records,scope='Independent ideal constant-tension force=-T*dL/dq at manufactured reference. Not Native accepted impulse,mapping pullback or dynamic efficacy. No unmeasured cable friction.',physical_validation='NOT QUALIFIED')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],max_error=max(r['gradient_FD_max_abs_error'] for r in records))))
if __name__=='__main__':main()
