"""Finite Rail/Skin edge-clamp candidate,not a qualified joint or applied preload."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,root_frame,box,cyl,cut,union,transform,poly

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_eyelet_keeper894/full_assembly_recipe.json';cfgfile=BASE/'meshes/b3_manufacturing_bore_v21/assembly_recipe.json';cfg=json.loads(cfgfile.read_text())['baseline_config'];M=root_frame(cfg,0);parts=json.loads(src.read_text())['parts'];support=next(p for p in parts if p['name']=='f0_c1_s0_support');rail=cfg['finger']['rail_thickness'];skin=cfg['finger']['skin_thickness'];back=-rail-.05;front=skin+.05
 if rail!=.5 or skin!=.1:raise ValueError('review this candidate for changed stack geometry')
 # Rootregion edgeclamp only:finite lower saddle/web/innerlip,not removed Rail.
 # .05mm clearance retained UNLOADED;no invented tight joint or friction force.
 frame=union(box([10,9.6,-1.3],[14,13,back]),box([10,12.05,-1.3],[14,13,front+.4]),box([10,10.5,front],[14,13,front+.4]),cyl(1.1,front+.3,1.7,(12,11.5)))
 frame=cut(frame,cyl(.55,front-.1,1.8,(12,11.5)))
 if a.local_csg:
  body=evaluate(support['shape']);body.apply_transform(np.linalg.inv(M));mounted=transform(union(poly(body),frame),M)
 else:mounted=union(support['shape'],transform(frame,M))
 screw=transform(union(cyl(.5,front,1.75,(12,11.5)),cyl(1.1,1.75,2.75,(12,11.5))),M);pad=transform(box([11.2,10.7,skin+.01],[12.8,12.3,front]),M)
 new=[dict(support,shape=mounted),dict(name='f0_c1_s0_rail_clamp_screw_PROXY',group='rail_clamp_RESEARCH',shape=screw),dict(name='f0_c1_s0_rail_pressure_pad_RESEARCH',group='rail_clamp_RESEARCH',shape=pad)];solids=[];records=[]
 for p in new:
  body=evaluate(p['shape']);file=out/(p['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('invalid/disconnected edgeclamp:'+p['name'])
  solids.append(body);records.append(dict(part=p['name'],volume_mm3=float(read.volume),STL_sha256=sha(file),singlebody=True))
 fixed=[p for p in parts if p['name']!=support['name']];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,solids)):
  for q,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],volume_mm3=float(h.volume),faces=len(h.faces)))
 (out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2));(out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(out/'root_frame.json').write_text(json.dumps(M.tolist()))
 result=dict(status='EDGE_CLAMP_CAD_REVIEW_REQUIRED' if hits else 'EDGE_CLAMP_UNLOADED_STATIC_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,cfgfile,BASE/'cad/manufacturing_assembly.py',BASE/'cad/generate.py')},records=records,solid_intersections=hits,full_part_count=len(fixed+new),rail_thickness_mm=rail,skin_thickness_mm=skin,UNLOADED_lower_rail_gap_mm=.05,UNLOADED_pad_skin_gap_mm=.01,pad_geometry_footprint_mm2=2.56,actual_preload_N=None,actual_friction=None,actual_clamp_material=None,actual_joint_strength_N=None,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE NEW rootregion x10..14mm edgeclamp design on actual894 keeper parent. Existing Rail/Skin uncut,finite web/lip/boss/screw/pad added. UNLOADED clearances:not an assembled tight/force-transferring joint. Pad footprint is CADgeometry,NOT contactarea orpressure. Preload/friction/slip/film indentation/fatigue/tolerance/toolaccess/movingwire/Nativejoint andholding NOT qualified;no STEP.')
 result['local_CSG']=a.local_csg
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--local-csg',action='store_true');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker']+(['--local-csg'] if a.local_csg else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_EDGE_CLAMP_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
