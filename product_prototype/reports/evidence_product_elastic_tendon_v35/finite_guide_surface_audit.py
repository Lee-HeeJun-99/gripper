"""Independent floating-point edge/triangle crossing audit,NOT swept CCD.
Strict interior intersections flag crossing;near-parallel/boundary cases are reported
as uncertain rather than cleared with a physical tolerance.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
def read(p):return list(csv.DictReader(p.open()))
def crossings(vertices,faces):
    edges=np.array(sorted({tuple(sorted((int(f[j]),int(f[(j+1)%3])))) for f in faces for j in range(3)}));count=0;uncertain=0
    for i in (0,1):
        a=vertices[i][edges[:,0]];b=vertices[i][edges[:,1]];tri=vertices[1-i][faces]
        for x,y in zip(a,b):
            mask=np.all(np.maximum(x,y)>=tri.min(axis=1),axis=1)&np.all(np.minimum(x,y)<=tri.max(axis=1),axis=1);q=tri[mask]
            if not len(q):continue
            d=y-x;e1=q[:,1]-q[:,0];e2=q[:,2]-q[:,0];h=np.cross(np.repeat(d[None,:],len(q),axis=0),e2);det=np.einsum('ij,ij->i',e1,h);bound=64*np.finfo(float).eps*np.linalg.norm(e1,axis=1)*np.linalg.norm(e2,axis=1)*np.linalg.norm(d);good=abs(det)>bound;uncertain+=int(np.count_nonzero(~good))
            q=q[good];e1=e1[good];e2=e2[good];h=h[good];det=det[good]
            if not len(q):continue
            s=x-q[:,0];u=np.einsum('ij,ij->i',s,h)/det;k=np.cross(s,e1);v=np.einsum('j,ij->i',d,k)/det;t=np.einsum('ij,ij->i',e2,k)/det;eps=64*np.finfo(float).eps
            inside=(u>eps)&(v>eps)&(u+v<1-eps)&(t>eps)&(t<1-eps);boundary=(u>=-eps)&(v>=-eps)&(u+v<=1+eps)&(t>=-eps)&(t<=1+eps)&~inside;count+=int(np.count_nonzero(inside));uncertain+=int(np.count_nonzero(boundary))
    return count,uncertain
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());mesh,_=eyelet(cfg,meta['geometry']['segments']);local=[np.array(m['body_local_vertices_m']) for m in meta['models']];records=[];purity=0.
 # Analytical crossing and separated references validate the geometric classifier.
 vv=[np.array([[0.,0.,0.],[1,0,0],[0,1,0]]),np.array([[.2,.2,-1],[.2,.2,1],[.8,.2,1]])];f=np.array([[0,1,2]]);assert crossings(vv,f)[0]>0;assert crossings([vv[0],vv[1]+[5,0,0]],f)[0]==0
 for alarm in ('1','5'):
  states=[read(src/alarm/f'guide{i}.csv') for i in (0,1)]
  if a.reference:
   for i in (0,1):
    original=read(BASE/'results'/a.reference/alarm/f'guide{i}.csv')
    if len(original)!=len(states[i]):raise ValueError('incomplete trajectory')
    for x,y in zip(states[i],original):
     for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):purity=max(purity,float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))))
  for k,s in enumerate(states[0]):
   q=[np.fromstring(states[i][k]['rigid_q'],sep=' ') for i in (0,1)];vertices=[local[i]@rotation(q[i][3:]).T+q[i][:3] for i in (0,1)];cross,unknown=crossings(vertices,mesh.faces);records.append(dict(alarm_mm=int(alarm),time_s=float(s['time_s']),strict_interior_edge_face_crossings=cross,parallel_or_boundary_uncertain_tests=unknown,status='FAIL_SAVED_FACET_CROSSING' if cross else 'UNCERTAIN_PARALLEL_OR_BOUNDARY' if unknown else 'NO_DETECTED_FACET_CROSSING_NOT_CONTAINMENT_CERTIFIED'))
 result=dict(status='FAIL_SAVED_FACET_CROSSING' if any(r['strict_interior_edge_face_crossings'] for r in records) else 'SAVED_FACET_CROSSING_AUDIT_ONLY',scope='Actual finite faceted eyelet states. Not a continuous motion,analytic curved-cylinder,containment/support/wholeassembly certificate. Numerical uncertainty is explicit;no physical gate relaxed.',source_sha256=sha(Path(__file__)),source_summary_sha256=sha(src/'summary.json'),observer_reference=a.reference,strict_observer_state_error=None if not a.reference else purity,strict_observer_state_gate=1e-12,strict_observer_state_pass=None if not a.reference else purity<=1e-12,records=records)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
