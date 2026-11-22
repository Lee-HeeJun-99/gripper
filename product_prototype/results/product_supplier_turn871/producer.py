"""Three finite supplier-sized turn wheels on ONE lead; no mounts removed."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha,evaluate,poly,transform
from supplier_root_wheel import supplier_dimensions,wheel_mesh
from root_redirect_candidate import corner_frame

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();routefile=BASE/'results/product_supplier_path870/summary.json';src=BASE/'meshes/b3_supplier_eyelet_seat_v43/full_assembly_recipe.json';cfg=BASE/'config/wire_bend_supplier_v40.json';parent=json.loads(src.read_text());route=json.loads(routefile.read_text())['records'][0];points=np.array(route['design_polyline_local_mm']);d=supplier_dimensions(json.loads(cfg.read_text()));wheel,_=wheel_mesh(d);new=[];solids=[];records=[]
 for k,name in enumerate(route['parts'],1):
  M,angle,trim=corner_frame(*points[k-1:k+2],d['wire_centre_pitch_radius_mm']);part=dict(name=name,shape=transform(poly(wheel),M));body=evaluate(part['shape']);file=out/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('STL readback')
  new.append(part);solids.append(body);records.append(dict(part=name,centre_mm=M[:3,3].tolist(),trim_mm=trim,volume_mm3=float(saved.volume),STL_sha256=sha(file)))
 oldnames={p['name'] for p in new};others=[p for p in parent['parts'] if p['name'] not in oldnames];fixed=[evaluate(p['shape']) for p in others];hits=[]
 for i,(part,body) in enumerate(zip(new,solids)):
  for other,solid in list(zip(others,fixed))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],solid.bounds[1])-np.maximum(body.bounds[0],solid.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([body,solid],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[part['name'],other['name']],volume_mm3=float(hit.volume),faces=len(hit.faces)))
 (out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2))
 result=dict(status='FAIL_FINITE_TURN_RETROFIT' if hits else 'FINITE_WHEELS_ONLY_REVIEW_REQUIRED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,routefile,cfg,BASE/'cad/supplier_root_wheel.py',BASE/'cad/root_redirect_candidate.py')},records=records,intersections=hits,retained_neighbor_count=len(others),runtime_s=time.monotonic()-start,scope='ONE f0/c0 lead,three recentered finite wheels. Only corresponding old wheels replaced;all290 other parts retained. No fork/support redesign,wire envelope,Native run,STEP or product clearance claim.',fabrication_ready=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 command=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(command,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=command,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
