"""One-sided exact-rational separating certificates for stored CAD floats.

Not a collision solver: failure to find a certificate means UNRESOLVED.
No model thickening or epsilon. Every certified axis is rechecked with Fraction.
"""
import argparse,json,subprocess,sys,time
from fractions import Fraction as F
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def rational_gap(triangle,delta,target,axis):
 a=[F(float(x)) for x in axis]
 def dot(v):return sum((F(float(x))*y for x,y in zip(v,a)),F(0))
 p=[dot(v) for v in triangle];shift=dot(delta);p=p+[x+shift for x in p]
 q=[dot(v) for v in target]
 return max(min(q)-max(p),min(p)-max(q))

def certificate(triangle,delta,target):
 triangle=np.asarray(triangle,float);delta=np.asarray(delta,float);target=np.asarray(target,float)
 if triangle.shape!=(3,3) or target.shape!=(3,3) or delta.shape!=(3,) or not all(np.all(np.isfinite(v)) for v in (triangle,delta,target)):
  raise ValueError('finite triangle/translation required')
 e=np.roll(triangle,-1,axis=0)-triangle;f=np.roll(target,-1,axis=0)-target
 n=np.cross(e[0],e[1]);m=np.cross(f[0],f[1])
 # Arbitrary extra axes are safe: only strictly separated projections pass.
 axes=np.vstack((np.eye(3),n,m,np.cross(e,delta),np.cross(np.vstack((e,delta))[:,None,:],f[None,:,:]).reshape(-1,3),np.cross(e,n),np.cross(f,m)))
 axes=axes[np.any(axes!=0,axis=1)]
 points=np.vstack((triangle,triangle+delta));p=points@axes.T;q=target@axes.T
 gaps=np.maximum(q.min(axis=0)-p.max(axis=0),p.min(axis=0)-q.max(axis=0))
 for i in np.argsort(gaps)[::-1]:
  if gaps[i]<=0:break
  gap=rational_gap(triangle,delta,target,axes[i])
  if gap>0:return dict(axis=axes[i].tolist(),exact_projection_gap=[str(gap.numerator),str(gap.denominator)])
 return None

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();prior=BASE/'results'/a.surface_case/'summary.json';src=BASE/'results'/a.assembly_case/'full_assembly_recipe.json'
 d=json.loads(prior.read_text());parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};support=evaluate(lookup['f0_c1_s0_support']['shape']);delta=np.asarray(next(r['translation_mm'] for r in d['records'] if r['part']=='f0_c1_s0_support'));bodies={n:evaluate(lookup[n]['shape']) for n in ('f0_skin','f0_rail_right')};records=[];proofs=[]
 if d['input_hashes'].get(str(src.relative_to(BASE)))!=sha(src):raise ValueError('surface/assembly input identity mismatch')
 for item in d['support_surface_refinement']['unresolved_prisms']:
  i=item['triangle'];tri=support.triangles[i];row=dict(triangle=i,obstacles=[],unresolved_pairs=[])
  for name in item['obstacles']:
   count=0
   for j,target in enumerate(bodies[name].triangles):
    proof=certificate(tri,delta,target)
    if proof is None:row['unresolved_pairs'].append(dict(part=name,triangle=j))
    else:proofs.append(dict(source_triangle=i,part=name,target_triangle=j,**proof));count+=1
   row['obstacles'].append(dict(part=name,certified_triangle_pairs=count,total_target_triangles=len(bodies[name].faces)))
  records.append(row)
 proofpath=out/'certificates.json';proofpath.write_text(json.dumps(proofs,indent=2))
 result=dict(status='EXACT_STORED_FLOAT_SEPARATION_CERTIFIED_ONLY' if not any(r['unresolved_pairs'] for r in records) else 'SEPARATION_CERTIFICATE_UNRESOLVED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,prior,BASE/'cad/manufacturing_assembly.py')},certificate_sha256=sha(proofpath),certified_pairs=len(proofs),records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,scope=f'ONLY{len(records)}nonvolume Support prisms previously unresolved in{a.surface_case} vsactualSkin/Rail surface triangles. Vertices,translation andaxis finite floats treated as EXACT rational inputs;endpoint is exact v+delta,not rounded float sum. Strict positive projection gap proves disjoint convex hulls along entire straight translation. Failure means unresolved,NOT collision. Not wholeassembly containment/tolerance/fullwire/movingfinger/Native/physicaljoint/product qualification;other surface-CSG tests retain original scope.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],pairs=len(proofs),unresolved=sum(len(r['unresolved_pairs']) for r in records),runtime_s=result['runtime_s']),indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--assembly-case',default='product_rail_clamp908');p.add_argument('--surface-case',default='product_rail_surface917');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.assembly_case,a.surface_case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--assembly-case',a.assembly_case,'--surface-case',a.surface_case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_SEPARATION_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
