"""Actual ONE placed Root wire segment against all retained solids."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from deformed_wire_screen import probes

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();folder=BASE/'results'/a.case;src=folder/'full_assembly_recipe.json';routefile=folder/'route_mm.json';meta=folder/'summary.json';d=json.loads(meta.read_text());parts=json.loads(src.read_text())['parts'];solids=[evaluate(p['shape']) for p in parts];route=np.asarray(json.loads(routefile.read_text()));radius=.225+.00022275007459783834;prefix=f"f{d['target_finger']}_c0";contacts=[];count=0
 for sample,probe in probes(route,radius):
  count+=1
  for p,body in zip(parts,solids):
   if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([probe,body],engine='manifold')
   if len(h.faces):contacts.append(dict(sample=sample,part=p['name'],faces=len(h.faces),signed_volume_mm3=float(h.volume),classification='INTENDED_ROOT_WHEEL_PROXIMITY_NOT_CONTACT_PASS' if p['name']==prefix+'_root_redirect' else 'UNRESOLVED_OBSTACLE'))
 result=dict(status='PLACED_ROOT_WIRE_REVIEW_REQUIRED' if any(h['classification']=='UNRESOLVED_OBSTACLE' for h in contacts) else 'PLACED_ROOT_SEGMENT_OBSTACLE_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,routefile,meta,BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py')},probe_count=count,assembly_part_count=len(parts),envelope_radius_mm=radius,intersections=contacts,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONLYsaved951placedRootsegment,notwholefinger/lead/turns/drum or other5channels. Allactualsolidsretained;wheelproximitiesrecorded,not response/friction/fatigueapproval. Circumscribedsphere/cylinder+arc-sagittabound inheritedfromsourcepath. Mount/bondinterface failures unchanged. NoNative/physicalholding/fullassemblyqualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],unresolved=sum(h['classification']=='UNRESOLVED_OBSTACLE' for h in contacts),runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_remaining_root951');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_PLACED_ROOT_WIRE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
