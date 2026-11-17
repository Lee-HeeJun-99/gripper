"""Independent used-row geometry/pullback/linear-angular impulse audit."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json

def closest(points,center):
 a,b,c=points;ab=b-a;ac=c-a;n=np.cross(ab,ac);n2=n.dot(n)
 if n2<=0:raise ValueError('degenerate triangle')
 foot=center-n*np.dot(center-a,n)/n2
 uv=np.linalg.solve(np.array([[ab.dot(ab),ab.dot(ac)],[ab.dot(ac),ac.dot(ac)]]),np.array([ab.dot(foot-a),ac.dot(foot-a)]))
 candidates=[]
 if min(uv)>=0 and sum(uv)<=1:candidates.append((foot,np.r_[1-sum(uv),uv]))
 for i,j in ((0,1),(0,2),(1,2)):
  edge=points[j]-points[i];t=np.clip(np.dot(center-points[i],edge)/edge.dot(edge),0,1);weights=np.zeros(3);weights[i]=1-t;weights[j]=t;candidates.append((weights@points,weights))
 p,w=min(candidates,key=lambda v:np.linalg.norm(v[0]-center));delta=p-center;distance=np.linalg.norm(delta)
 if distance==0:raise ValueError('undefined normal')
 return p,w,delta/distance

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True);parser.add_argument('--case',required=True);args=parser.parse_args()
 source=ROOT/'results'/('autonomous_film_'+args.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
 if summary['status']!='PASS' or meta.get('adaptive') or meta.get('frozen_grid'):raise ValueError('completed uniform owner trace required')
 scene=ET.parse(source/'scene.scn');topology=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);nx=int(scene.find('.//FilmRailTendon').get('nx'))
 states=list(csv.DictReader((source/'coupled.states.csv').open()));events=list(csv.DictReader((source/'coupled.event_states.csv').open()));owned=list(csv.DictReader((source/'coupled.rows.csv').open()))
 index=np.full(rest.size,-1,dtype=int);weight=np.ones(rest.size);nf=0
 for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
  for i in range(1,nx):
   for j in range(ny):
    for d in range(3):
     if i!=1 or d!=2:index[3*(offset+i*ny+j)+d]=nf;nf+=1
  for j in range(ny):index[3*(offset+ny+j)+2]=index[3*(offset+2*ny+j)+2];weight[3*(offset+ny+j)+2]=.25
 initialQ=np.fromstring(scene.find("MechanicalObject[@name='dofs']").get('position'),sep=' ').reshape(-1,3);initialC=np.fromstring(meta['initial_body_center'],sep=' ')
 def state(s):return np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3),np.fromstring(s['body_center'],sep=' ')
 records=[]
 for row in owned:
  step=int(row['step']);end=states[step-1];q1,c1=state(end);q0,c0=state(states[step-2]) if step>1 else (initialQ,initialC)
  if row['stage']=='0':q,c=state(next(s for s in events if s['stage']=='pre' and s['time']==row['time']))
  elif row['stage']=='1':
   if int(end['event']):
    lower=float(states[step-2]['time']) if step>1 else 0.;candidates=[s for s in events if s['stage']=='post' and lower<float(s['time'])<=float(end['time'])]
    if len(candidates)!=1:raise ValueError('event remainder not uniquely observable')
    q0,c0=state(candidates[0])
   q,c=(.5*(q0+q1),.5*(c0+c1)) if meta.get('midpoint_contact',False) else (q1,c1)
  elif row['stage']=='2':q,c=q1,c1
  else:raise ValueError('unknown owned row stage')
  ids=tri[int(row['triangle'])];x=(rest+q)[ids];p,bary,normal=closest(x,c);full=np.zeros_like(rest)
  for k,node in enumerate(ids):full[node]+=bary[k]*normal
  expected=np.zeros(nf+6)
  for k,free in enumerate(index):
   if free>=0:expected[free]+=weight[k]*full.flat[k]
  expected[nf:nf+3]=-normal;actual=np.fromstring(row['jacobian'],sep=' ')
  linear=full.sum(axis=0)-normal;moment=np.cross(rest+q,full).sum(axis=0)+np.cross(c,-normal)
  records.append(dict(step=step,stage=int(row['stage']),row=int(row['row']),gradient_error=float(np.max(abs(actual-expected))),point_error=float(np.linalg.norm(p-np.array([float(row[k]) for k in ('px','py','pz')]))),normal_error=float(np.linalg.norm(normal-np.array([float(row[k]) for k in ('nx','ny','nz')]))),unit_linear_error=float(np.linalg.norm(linear)),unit_angular_error=float(np.linalg.norm(moment)),impulse=float(row['impulse'])))
 maxima={k:max([r[k] for r in records],default=0.) for k in ('gradient_error','point_error','normal_error','unit_linear_error','unit_angular_error')};valid=bool(records) and all(v<=1e-10 for v in maxima.values())
 out=ROOT/'results'/('autonomous_film_'+args.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'rows.csv').open('x') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 write_json(out/'summary.json',dict(status='PASS' if valid else 'FAIL',scope='independent used-row geometry and virtual-work/linear-angular contact pullback;NOT full force equilibrium/energy/time certificate',case=args.case,rows=len(records),maxima=maxima,hashes={name:sha(source/name) for name in ('identity.json','scene.scn','coupled.states.csv','coupled.rows.csv','coupled.event_states.csv')}));print(json.dumps(dict(status='PASS' if valid else 'FAIL',rows=len(records),maxima=maxima)))
if __name__=='__main__':main()
