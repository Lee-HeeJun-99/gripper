"""Re-centred, unmounted Root module with actual circular tangent geometry."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,box,cyl,union,cut,transform,evaluate,poly,sha
from supplier_root_wheel import supplier_dimensions,wheel_mesh
from root_redirect_candidate import corner_frame
from root_thrust_candidate import lands
from deformed_wire_screen import probes

def single_corner(a,b,c,radius):
 a,b,c=map(lambda x:np.asarray(x,float),(a,b,c));M,angle,trim=corner_frame(a,b,c,radius)
 if trim>=min(np.linalg.norm(b-a),np.linalg.norm(c-b)):raise ValueError('tangent point exceeds available branch')
 u=(b-a)/np.linalg.norm(b-a);start=b-u*trim;radial=start-M[:3,3];axis=M[:3,2];n=max(2,math.ceil(angle/math.radians(1)))
 arc=np.array([M[:3,3]+radial*math.cos(t)+np.cross(axis,radial)*math.sin(t) for t in np.linspace(0,angle,n+1)])
 return np.vstack([a,arc,c]),M,angle,trim,radius*(1-math.cos(angle/(2*n)))

def module_fork(outer,cfg):
 back=outer+2
 base=union(box([-back-1,-1.5,-2.4],[-back,1.5,2.4]),box([-back,-1.5,-2.4],[.5,1.5,-1.4]),box([-back,-1.5,1.4],[.5,1.5,2.4]))
 # One final through-bore,not a union of separately coincident bore surfaces.
 # Same nominal solid set,not a removed mesh seam or tolerance relaxation.
 inner=cfg['land_fork_span']/2;outer_z=cfg['land_outer_z'];r=cfg['land_outer_radius'];bore=cfg['land_bore_radius']
 return cut(union(base,cyl(r,inner,outer_z),cyl(r,-outer_z,-inner)),cyl(bore,-2.5,2.5))

def worker(a):
 out=BASE/'results'/a.tag;dest=BASE/'meshes'/a.name;dest.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'results/product_root_fork780/summary.json';lead=BASE/'results/product_motor_lead748/summary.json';cfgfile=BASE/'config/root_thrust_v37.json';supplier=BASE/'config/wire_bend_supplier_v40.json';cfg=json.loads(cfgfile.read_text());d=supplier_dimensions(json.loads(supplier.read_text()))
 old=next(r for r in json.loads(src.read_text())['records'] if r['part']=='f0_c0_root_redirect');oldlead=next(r for r in json.loads(lead.read_text())['records'] if r['model']=='perimeter_rounded_candidate' and r['finger']==0 and r['cable']==0)
 first=np.array(old['route_mm'][0]);pull=np.array(oldlead['route_mm'][0]);direction=np.array(oldlead['route_mm'][1])-pull;direction/=np.linalg.norm(direction);endpoint=pull+8*direction
 route,M,angle,trim,sag=single_corner(first,pull,endpoint,d['wire_centre_pitch_radius_mm']);facing=np.mean(route[1:-1],axis=0)-M[:3,3];facing-=M[:3,2]*(M[:3,2]@facing);facing/=np.linalg.norm(facing);F=M.copy();F[:3,:3]=np.column_stack([facing,np.cross(M[:3,2],facing),M[:3,2]])
 mesh,profile=wheel_mesh(d);parts=[dict(name='supplier_root_wheel',shape=transform(poly(mesh),M)),dict(name='supplier_root_fork_unmounted',shape=transform(module_fork(d['flange_outer_radius_mm'],cfg),F)),dict(name='supplier_root_pin_proxy',shape=transform(cyl(.5,-2.4,2.4),F))];solids=[evaluate(p['shape']) for p in parts];records=[]
 for part,body in zip(parts,solids):
  path=dest/(part['name']+'.stl');path.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(path)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('module STL readback invalid')
  records.append(dict(part=part['name'],volume_mm3=float(saved.volume),STL_sha256=sha(path),closed_single_body=True))
 pairs=[]
 for i,left in enumerate(solids):
  for j,right in enumerate(solids[i+1:],i+1):
   hit=trimesh.boolean.intersection([left,right],engine='manifold')
   if len(hit.faces):pairs.append(dict(parts=[parts[i]['name'],parts[j]['name']],volume_mm3=float(hit.volume),faces=len(hit.faces)))
 wirehits=[]
 for sample,probe in probes(route,d['wire_diameter_mm']/2+sag):
  for j in (1,2):
   if np.any(np.minimum(probe.bounds[1],solids[j].bounds[1])-np.maximum(probe.bounds[0],solids[j].bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([probe,solids[j]],engine='manifold')
   if len(hit.faces):wirehits.append(dict(sample=sample,part=parts[j]['name'],volume_mm3=float(hit.volume)))
 (dest/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=parts,scope='UNMOUNTED ONE ROOT MODULE ONLY'),indent=2));(dest/'route_mm.json').write_text(json.dumps(route.tolist(),indent=2));(dest/'profile_mm.json').write_text(json.dumps(profile.tolist(),indent=2))
 files=[Path(__file__),BASE/'cad/supplier_root_wheel.py',BASE/'cad/root_redirect_candidate.py',BASE/'cad/root_thrust_candidate.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py',cfgfile,supplier,src,lead]
 result=dict(status='LOCAL_MODULE_REFERENCE_CLEAR_NOT_ASSEMBLY_PASS' if not pairs and not wirehits else 'LOCAL_MODULE_REVIEW_REQUIRED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in files},records=records,dimensions=d,turn_angle_deg=math.degrees(angle),trim_mm=trim,centre_mm=M[:3,3].tolist(),old_centre_mm=old['centre_mm'],centre_shift_mm=float(np.linalg.norm(M[:3,3]-old['centre_mm'])),route_sagitta_bound_mm=sag,solid_intersections=pairs,wire_vs_fork_pin_intersections=wirehits,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='New0.45mmwire/re-centredR5.85/expandedfork+existingV39thrustlands hypothesis. One3partUNMOUNTEDmodule:NOTPalm/6modules/fullassembly clearance. Oldoldmodule notremoved/adopted inV39. Pin isNOTretained/threaded. Wire vsfork/pin conservative circumscribedprobes;wire/wheel tangency intended,notCTCcollision certification. NoNative/FEM/force/fatigue/material/wholemotionvalidation. All18turnpulleys andotherguide bends remainunqualified.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('status','runtime_s','solid_intersections','wire_vs_fork_pin_intersections','centre_shift_mm')},indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 command=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--name',a.name,'--worker'];proc=guarded(command,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=command,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_MODULE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
