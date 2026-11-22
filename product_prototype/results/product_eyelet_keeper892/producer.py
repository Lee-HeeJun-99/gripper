"""Finite split keeper hypothesis;not a selected fastener or qualified joint."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha,box,cyl,cut,union,transform,evaluate

def keeper_parts(ring,support,G,gap=.05):
 axis=G[:3,0];centre=G[:3,3];toward=support.center_mass-centre;toward-=axis*(axis@toward)
 if np.linalg.norm(toward)==0:raise ValueError('support direction undefined')
 y=-toward/np.linalg.norm(toward);x=np.cross(y,axis);H=np.eye(4);H[:3,:3]=np.column_stack([x,y,axis]);H[:3,3]=centre
 local=(ring.vertices-centre)@H[:3,:3];radius=float(np.linalg.norm(local[:,:2],axis=1).max());half=float(np.ptp(local[:,2])/2)
 # Finite axial shoulders on both ends and a through wire bore. Dimensions are
 # research manufacturing inputs,not measured fit or supplier specifications.
 outside=box([-3.6,-2.3,-half-.6],[3.6,2.3,half+.6]);pocket=cyl(radius+gap,-half-.1,half+.1,sections=128);wire=cyl(.55,-half-.8,half+.8,sections=128)
 core=cut(outside,pocket,wire);bottom=cut(core,box([-4,-gap/2,-3],[4,3,3]));top=cut(core,box([-4,-3,-3],[4,gap/2,3]));R=trimesh.transformations.rotation_matrix(-np.pi/2,[1,0,0]);bolts=[];nuts=[];holes=[]
 for at in (-2.5,2.5):
  B=R.copy();B[:3,3]=[at,0,0];holes.append(transform(cyl(.6,-4,4),B));bolts.append(transform(union(cyl(.5,-3.3,2.35),cyl(1.1,2.35,3.35)),H@B));nuts.append(transform(cut(cyl(1.1,-3.35,-2.35,sections=6),cyl(.55,-3.5,-2.2)),H@B))
 lower=union(cut(transform(dict(op='polyhedron',vertices=support.vertices.tolist(),faces=support.faces.tolist()),np.linalg.inv(H)),box([-3.8,-gap/2,-half-.8],[3.8,3,half+.8])),bottom)
 lower=cut(lower,pocket,wire,*holes);top=cut(top,*holes)
 return H,[transform(lower,H),transform(top,H),*bolts,*nuts],dict(eyelet_radius_mm=radius,eyelet_length_mm=2*half,pocket_radius_mm=radius+gap,axial_clearance_mm=.1,wire_bore_radius_mm=.55,split_gap_mm=gap,screw_shaft_diameter_mm=1.,screw_clearance_diameter_mm=1.2)

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_supplier_second_root886/full_assembly_recipe.json';data=json.loads(src.read_text());prefix='f0_c1_s0';lookup={p['name']:p for p in data['parts']};eyelet=lookup[prefix+'_eyelet'];support=lookup[prefix+'_support'];G=np.eye(4);op=eyelet['shape']
 while op['op']=='transform':G=G@np.array(op['matrix']);op=op['shape']
 H,shapes,dims=keeper_parts(evaluate(eyelet['shape']),evaluate(support['shape']),G);names=[prefix+'_support',prefix+'_keeper_cover',prefix+'_keeper_screw0',prefix+'_keeper_screw1',prefix+'_keeper_nut0',prefix+'_keeper_nut1'];new=[dict(name=n,group='mechanical_keeper_RESEARCH',shape=s) for n,s in zip(names,shapes)];records=[];solids=[]
 for p in new:
  body=evaluate(p['shape']);file=out/(p['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('invalid/disconnected keeper STL:'+p['name'])
  records.append(dict(part=p['name'],volume_mm3=float(read.volume),STL_sha256=sha(file),singlebody=True));solids.append(body)
 replaced={prefix+'_support',prefix+'_bondline_RESEARCH'};fixed=[p for p in data['parts'] if p['name'] not in replaced];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,solids)):
  for q,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[p['name'],q['name']],volume_mm3=float(hit.volume),faces=len(hit.faces)))
 (out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(out/'keeper_frame.json').write_text(json.dumps(H.tolist()))
 result=dict(status='MECHANICAL_KEEPER_REVIEW_REQUIRED' if hits else 'KEEPER_STATIC_SOLIDS_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,BASE/'cad/manufacturing_assembly.py')},records=records,dimensions=dims,solid_intersections=hits,full_part_count=len(fixed+new),replaced_parts=sorted(replaced),actual_material=None,actual_fastener_specification=None,actual_preload_N=None,actual_joint_strength_N=None,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE second Root Eyelet mechanical replacement for explicit unselected bondline. Same finite Eyelet and full surrounding solids retained;finite split housing,axial stops,cover,two screw/nut proxies. No adhesive strength inferred,no collision removed without replacement. Skin attachment,wire clearance,service,retention/preload/strength/tolerance/material and Native dynamics NOT qualified;no STEP.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_KEEPER_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
