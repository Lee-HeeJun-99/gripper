"""Individually rebuild second Root and finite guide seat against two-channel CAD."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha,evaluate,union,cut,cyl,transform,poly
from supplier_root_wheel import supplier_dimensions,wheel_mesh
from supplier_root_module import single_corner,module_fork
from palm_bridge_candidate import rod

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_supplier_second882/full_assembly_recipe.json';rootfile=BASE/'results/product_root_fork780/summary.json';leadfile=BASE/'results/product_motor_lead748/summary.json';cfgfile=BASE/'config/root_thrust_v37.json';supplier=BASE/'config/wire_bend_supplier_v40.json';parts=json.loads(src.read_text())['parts'];lookup={p['name']:p for p in parts};d=supplier_dimensions(json.loads(supplier.read_text()));cfg=json.loads(cfgfile.read_text());old=next(r for r in json.loads(rootfile.read_text())['records'] if r['part']=='f0_c1_root_redirect');lead=next(r for r in json.loads(leadfile.read_text())['records'] if r['model']=='perimeter_rounded_candidate' and (r['finger'],r['cable'])==(0,1));first=np.array(old['route_mm'][0]);pull=np.array(lead['route_mm'][0]);direction=np.array(lead['route_mm'][1])-pull;direction/=np.linalg.norm(direction);route,M,angle,trim,sag=single_corner(first,pull,pull+8*direction,d['wire_centre_pitch_radius_mm']);facing=np.mean(route[1:-1],axis=0)-M[:3,3];facing-=M[:3,2]*(M[:3,2]@facing);facing/=np.linalg.norm(facing);F=M.copy();F[:3,:3]=np.column_stack([facing,np.cross(M[:3,2],facing),M[:3,2]])
 if F[1,2]>0:F[:3,:3]=F[:3,:3]@np.diag([1,-1,-1])
 branch=lookup['f0_c1_root_mounted_bridge']['shape']['items'][0];connection=(F@[-9.375,0,0,1])[:3];waypoints=[connection,np.array([58,-44,-8]),np.array([58,-44,15]),np.array([52,-44,15])];boss=transform(cut(cyl(1.5,-4.4,-2.2),cyl(.55,-4.5,-2.1)),F);mounted=union(branch,transform(module_fork(d['flange_outer_radius_mm'],cfg),F),boss,*[rod(x,y,1.5) for x,y in zip(waypoints,waypoints[1:])]);wheel,_=wheel_mesh(d)
 T=np.eye(4);T[:3,3]=2*(first-pull)/np.linalg.norm(first-pull);eyelet=dict(lookup['f0_c1_s0_eyelet'],shape=transform(lookup['f0_c1_s0_eyelet']['shape'],T));support=transform(lookup['f0_c1_s0_support']['shape'],T);G=np.eye(4);op=eyelet['shape']
 while op['op']=='transform':G=G@np.array(op['matrix']);op=op['shape']
 ring=evaluate(eyelet['shape']);body=evaluate(support);local=(ring.vertices-G[:3,3])@G[:3,:3];radius=float(np.linalg.norm(local[:,1:],axis=1).max());length=float(np.ptp(local[:,0]));axis=G[:3,0];centre=G[:3,3];gap=.05
 tool=trimesh.creation.cylinder(radius=radius+gap,segment=[centre-axis*(length/2+.2),centre+axis*(length/2+.2)],sections=128);seated=evaluate(cut(support,poly(tool)));shell=trimesh.boolean.difference([trimesh.creation.cylinder(radius=radius+gap,segment=[centre-axis*length/2,centre+axis*length/2],sections=128),trimesh.creation.cylinder(radius=radius,segment=[centre-axis*(length/2+.1),centre+axis*(length/2+.1)],sections=128)],engine='manifold');bond=trimesh.boolean.intersection([body,shell],engine='manifold')
 new=[dict(name='f0_c1_root_redirect',group='supplier_recommended_root_wheel',shape=transform(poly(wheel),M)),dict(name='f0_c1_root_mounted_bridge',group='supplier_integral_root_bridge',shape=mounted),dict(name='f0_c1_root_headed_pin',group='supplier_root_headed_pin_PROXY',shape=transform(union(cyl(.5,-3.7,2.45),cyl(1.25,2.45,3.45)),F)),eyelet,dict(lookup['f0_c1_s0_support'],shape=poly(seated)),dict(name='f0_c1_s0_bondline_RESEARCH',group='UNSELECTED_adhesive_design_volume',shape=poly(bond))];solids=[];records=[]
 for p in new:
  shape=evaluate(p['shape']);file=out/(p['name']+'.stl');file.write_text(shape.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('second Root invalid saved mesh:'+p['name'])
  solids.append(shape);records.append(dict(part=p['name'],STL_sha256=sha(file),volume_mm3=float(read.volume),singlebody=True))
 changed={p['name'] for p in new};fixed=[p for p in parts if p['name'] not in changed];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,solids)):
  for q,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],volume_mm3=float(h.volume),faces=len(h.faces)))
 route[0]+=T[:3,3];(out/'route_mm.json').write_text(json.dumps(route.tolist()));(out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2))
 result=dict(status='SECOND_ROOT_SEAT_REVIEW_REQUIRED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,rootfile,leadfile,cfgfile,supplier,BASE/'cad/supplier_root_module.py',BASE/'cad/palm_bridge_candidate.py')},records=records,solid_intersections=hits,full_part_count=len(fixed+new),centre_mm=M[:3,3].tolist(),pin_outward_axis=F[:3,2].tolist(),guide_translation_mm=T[:3,3].tolist(),ASSUMED_bondline_gap_mm=gap,actual_material=None,actual_bond_strength_N=None,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Second Root individually reconstructed with actual two-turn-branch parent and independently composed guide frame. Finite support seat/UNSELECTED bondline,not a removed collision. Same-size guide translated2mm;its Skin attachment remains UNQUALIFIED. No fullwire/moving/Native/strength/STEP qualification;remaining4Roots/12turns stilllegacy.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],intersections=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_SECOND_ROOT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
