"""Independent replay and completeness audit of one-sided separation proofs."""
import argparse,json,subprocess,sys,time,math
from fractions import Fraction
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def verify(proofs,source,delta,targets,expected):
 seen=set();minimum=None
 for proof in proofs:
  key=(proof['source_triangle'],proof['part'],proof['target_triangle'])
  if key in seen or key not in expected:raise ValueError('duplicate/unexpected certificate')
  seen.add(key);axis=proof['axis']
  if len(axis)!=3 or not all(math.isfinite(x) for x in axis):raise ValueError('invalid axis')
  axis=list(map(Fraction,axis));a=[[Fraction(float(x)) for x in v] for v in source[key[0]]];d=list(map(lambda x:Fraction(float(x)),delta));b=[[Fraction(float(x)) for x in v] for v in targets[key[1]][key[2]]]
  a+= [[x+y for x,y in zip(v,d)] for v in a[:]]
  def projection(vertices):return [sum((x*y for x,y in zip(v,axis)),Fraction(0)) for v in vertices]
  p=projection(a);q=projection(b);gap=max(min(p)-max(q),min(q)-max(p))
  recorded=Fraction(*map(int,proof['exact_projection_gap']))
  if gap<=0 or gap!=recorded:raise ValueError('invalid exact projection gap')
  minimum=gap if minimum is None else min(minimum,gap)
 if seen!=expected:raise ValueError('incomplete certificate coverage')
 return dict(verified_pairs=len(seen),minimum_UNNORMALIZED_projection_gap=None if minimum is None else [str(minimum.numerator),str(minimum.denominator)])

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;folder=BASE/'results'/a.case;summary=folder/'summary.json';d=json.loads(summary.read_text());proof=folder/'certificates.json'
 if sha(proof)!=d['certificate_sha256']:raise ValueError('certificate hash mismatch')
 for path,digest in d['input_hashes'].items():
  if sha(BASE/path)!=digest:raise ValueError('input hash mismatch:'+path)
 src=BASE/next(n for n in d['input_hashes'] if n.endswith('/full_assembly_recipe.json'));prior=BASE/next(n for n in d['input_hashes'] if n.endswith('/summary.json'));parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};old=json.loads(prior.read_text());source=evaluate(lookup['f0_c1_s0_support']['shape']).triangles;targets={name:evaluate(lookup[name]['shape']).triangles for name in ('f0_skin','f0_rail_right')};delta=next(r['translation_mm'] for r in old['records'] if r['part']=='f0_c1_s0_support');expected={(i['triangle'],name,j) for i in old['support_surface_refinement']['unresolved_prisms'] for name in i['obstacles'] for j in range(len(targets[name]))}
 detail=verify(json.loads(proof.read_text()),source,delta,targets,expected)
 result=dict(status='PASS_EXACT_CERTIFICATE_REPLAY_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),summary,proof,src,prior,BASE/'cad/manufacturing_assembly.py')},detail=detail,runtime_s=time.monotonic()-start,fabrication_ready=False,scope=f'Independent rational dot-product replay;duplicates/missing/invalid axes/gaps rejected. Complete{len(expected)}stored-float triangle pairs only. Projection gap is NOT normalized Euclidean clearance, manufacturing tolerance, Native result or fullassembly qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_rail_certificate924');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CERTIFICATE_AUDIT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
