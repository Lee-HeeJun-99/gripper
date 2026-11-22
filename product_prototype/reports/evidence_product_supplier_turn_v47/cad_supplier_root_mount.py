"""Rebuild one real integral mount;not removal of a colliding support."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,cut,union,transform,evaluate,sha
from palm_bridge_candidate import rod
from deformed_wire_screen import probes

def worker(a):
 out=BASE/'results'/a.tag;dest=BASE/'meshes'/a.name;dest.mkdir(exist_ok=False);start=time.monotonic();parentfile=BASE/'meshes/b3_root_thrust_v39/full_assembly_recipe.json';modulefile=BASE/'meshes/b3_supplier_root_module_v41/assembly_recipe.json';basefile=BASE/'meshes/b3_compact_bridge_v35/assembly_recipe.json';shiftfile=BASE/'results/product_supplier_shift860/changed_guides_recipe.json';routefile=BASE/'meshes/b3_supplier_root_module_v41/route_mm.json';supplier=BASE/'config/wire_bend_supplier_v40.json'
 parent=json.loads(parentfile.read_text());module=json.loads(modulefile.read_text())['parts'];base=next(p for p in json.loads(basefile.read_text())['parts'] if p['name']=='f0_c0_bridge');wheel=next(p for p in module if p['name']=='supplier_root_wheel');fork=next(p for p in module if p['name']=='supplier_root_fork_unmounted');F=np.array(fork['shape']['matrix']);connection=(F@[-9.375,0,0,1])[:3];waypoints=[connection,np.array([58,44,-8]),np.array([58,44,15]),np.array([52,44,15])]
 boss=transform(cut(cyl(1.5,-4.4,-2.2),cyl(.55,-4.5,-2.1)),F)
 mounted=union(base['shape'],fork['shape'],boss,*[rod(x,y,1.5) for x,y in zip(waypoints,waypoints[1:])]);pin=transform(union(cyl(.5,-3.7,2.45),cyl(1.25,2.45,3.45)),F)
 new=[dict(name='f0_c0_root_redirect',group='supplier_recommended_root_wheel',shape=wheel['shape']),dict(name='f0_c0_root_mounted_bridge',group='supplier_integral_root_bridge',shape=mounted),dict(name='f0_c0_root_headed_pin',group='supplier_root_headed_pin_PROXY',shape=pin),*json.loads(shiftfile.read_text())['parts']];lookup={p['name']:p for p in parent['parts']}
 if not all(p['name'] in lookup for p in new):raise ValueError('replacement has unmatched assembly name')
 solids=[];records=[]
 for part in new:
  body=evaluate(part['shape']);file=dest/(part['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('rebuilt mounted STL failed readback:'+part['name'])
  solids.append(body);records.append(dict(part=part['name'],STL_sha256=sha(file),volume_mm3=float(read.volume),closed_positive_singlebody=True))
 replacements={p['name']:p for p in new};fixed=[p for p in parent['parts'] if p['name'] not in replacements];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(left,body) in enumerate(zip(new,solids)):
  for right,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   intersection=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(intersection.faces):hits.append(dict(parts=[left['name'],right['name']],volume_mm3=float(intersection.volume),faces=len(intersection.faces)))
 # First guide now lies 2mm farther along same incoming line;new fillet unchanged.
 route=np.array(json.loads(routefile.read_text()));route[0]+=np.array(json.loads((BASE/'results/product_supplier_shift860/summary.json').read_text())['changed_guides'][0]['translation_mm']);wirehits=[];radius=.225+.00022275007459783834
 for sample,probe in probes(route,radius):
  for part,body in zip(new,solids):
   if part['name'] in ('f0_c0_root_redirect','f0_c0_s0_eyelet'):continue # Intended finite wire contact/hole;not declared clearance.
   if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
   intersection=trimesh.boolean.intersection([probe,body],engine='manifold')
   if len(intersection.faces):wirehits.append(dict(sample=sample,part=part['name'],volume_mm3=float(intersection.volume)))
 full=[replacements.get(p['name'],p) for p in parent['parts']]
 (dest/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(dest/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=full),indent=2));(dest/'route_mm.json').write_text(json.dumps(route.tolist(),indent=2))
 files=[Path(__file__),BASE/'cad/manufacturing_assembly.py',BASE/'cad/palm_bridge_candidate.py',BASE/'cad/deformed_wire_screen.py',parentfile,modulefile,basefile,shiftfile,routefile,supplier,BASE/'results/product_supplier_shift860/summary.json']
 result=dict(status='REBUILT_ROOT_MOUNT_REVIEW_REQUIRED' if hits or wirehits else 'REFERENCE_ROOT_MOUNT_CLEAR_NOT_PRODUCT_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in files},records=records,full_part_count=len(full),changed_parts=len(new),solid_intersections=hits,wire_vs_mount_support_pin_intersections=wirehits,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='Only f0c0Root3parts+firstguide/support physicallyREPLACED;all287otherparts retained. Newconnectedintegralmount reusesrealcompactboltedbridge,notdeletedoldobstacle. Actual5changed-vs-wholeassembly CSG. Intended wire/wheel andwire/eyelet interactionsNOTdeclaredclear. Bossbore/thread/pinhead PROXIES,notactualthreadstrength/material. Other5Rootmodules+18turnpulleys remainold. Noall-parts/motion/service/strength/Native/holdingqualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('status','runtime_s','solid_intersections','wire_vs_mount_support_pin_intersections')},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 command=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--name',a.name,'--worker'];proc=guarded(command,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=command,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_REBUILT_MOUNT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
