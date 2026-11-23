"""Other five legacy lead envelopes vs changed branch; not a qualified new route."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from deformed_wire_screen import probes

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_supplier_mount875/assembly_recipe.json';leadfile=BASE/'results/product_motor_lead748/summary.json';rootfile=BASE/'results/product_root_fork780/summary.json';parts=json.loads(src.read_text())['parts'];solids=[evaluate(p['shape']) for p in parts];leads=[r for r in json.loads(leadfile.read_text())['records'] if r['model']=='perimeter_rounded_candidate'];roots=json.loads(rootfile.read_text())['records'];hits=[];records=[]
 for lead in leads:
  f,c=lead['finger'],lead['cable']
  if (f,c)==(0,0):continue
  root=next(r for r in roots if r['part']==f'f{f}_c{c}_root_redirect');count=0
  # Separate root/lead original design sections retained,not joined with an
  # invented corner. Overlapping source sections are counted independently.
  for section,route in [('root',root['route_mm']),('lead',lead['route_mm'])]:
   for sample,probe in probes(np.array(route),.25+2*(1-math.cos(math.radians(.5)))):
    count+=1
    for p,body in zip(parts,solids):
     if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
     h=trimesh.boolean.intersection([probe,body],engine='manifold')
     if len(h.faces):hits.append(dict(finger=f,cable=c,section=section,sample=sample,part=p['name'],volume_mm3=float(h.volume),faces=len(h.faces)))
  records.append(dict(finger=f,cable=c,probe_count=count,wire_diameter_mm=.5,construction='LEGACY_UNSPECIFIED_NOT_SUPPLIER_QUALIFIED'))
 result=dict(status='FAIL_OTHER_WIRE_ENVELOPE' if hits else 'OTHER_LEGACY_WIRE_OBSTACLE_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,leadfile,rootfile,BASE/'cad/deformed_wire_screen.py')},records=records,intersections=hits,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Other5 ORIGINAL .5mm rest-design Root/lead paths against10 changed solids only. Not supplier compatibility approval of legacyR2bends,not all-wire mutual or full finger/moving clearance. No Native run or product PASS.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=len(hits),runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_OTHER_WIRE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
