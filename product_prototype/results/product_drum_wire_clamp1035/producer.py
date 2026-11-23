"""Finite reusable free-end clamp candidate,not wire retention/actuation proof."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,box,cyl,union,cut,transform,poly
from assembly_recipe_io import resolve_recipe
from distal_keeper_service import intersections

def radial(radius,x0,x1,y,z,sections=64):
 R=np.eye(4);R[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]];R[:3,3]=[0,y,z]
 return transform(cyl(radius,x0,x1,sections=sections),R)

def clamp_shapes(drum,cfg,fast):
 y=cfg['wire_axis_Y_mm'];z=cfg['wire_axis_Z_mm'];h=cfg['body_half_YZ_mm'];lo,hi=cfg['body_X_mm'];body=union(drum,box([lo,y-h,z-h],[hi,y+h,z+h]));px0,px1=cfg['pad_X_mm'];py,pz=cfg['pad_half_YZ_mm'];pad=box([px0,y-py,z-pz],[px1,y+py,z+pz]);sx=cfg['screw_under_head_X_mm'];s=fast['screw'];n=fast['nut'];head=max(s['head_height_mm']);nr=max(n['AF_mm'])/math.sqrt(3)
 screw=cut(union(radial(s['diameter_mm']/2,sx-s['nominal_length_mm'],sx,y,z),radial(max(s['head_diameter_mm'])/2,sx,sx+head,y,z)),radial(s['hex_AF_mm']/math.sqrt(3),sx+head-s['nominal_drive_depth_mm'],sx+head+.2,y,z,6))
 nx0,nx1=cfg['nut_X_mm'];nut=cut(radial(nr,nx0,nx1,y,z,6),radial(.81,nx0-.1,nx1+.1,y,z));np0,np1=cfg['nut_pocket_X_mm'];ny=cfg['nut_pocket_AF_mm']/math.sqrt(3);p0,p1=cfg['pad_pocket_X_mm'];hy,hz=cfg['pad_pocket_half_YZ_mm'];wire=poly(trimesh.creation.cylinder(radius=cfg['wire_bore_radius_mm'],segment=[[cfg['wire_axis_X_mm'],y-4,z],[cfg['wire_axis_X_mm'],y+4,z]],sections=64))
 body=cut(body,wire,box([p0,y-hy,z-hz],[p1,y+hy,z+hz]),radial(cfg['screw_clearance_radius_mm'],px1,sx+.5,y,z),radial(ny,np0,np1,y,z,6),box([np0,y-1.91,z+cfg['nut_entry_start_Z_offset_mm']],[np1,y+1.91,z+3]))
 return [body,pad,screw,nut]

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';spec=BASE/'config/termination_drum_clamp_v58.json';cfg=json.loads(spec.read_text());fastpath=BASE/'config'/cfg['source_fasteners'];fast=json.loads(fastpath.read_text());parts,hashes=resolve_recipe(src);old=next(p for p in parts if p['name']=='f0_two_channel_drum');shape=old['shape']
 if shape['op']!='transform' or not np.array_equal(np.asarray(shape['matrix']),np.eye(4)):raise ValueError('explicit f0 drum frame identity required')
 local=clamp_shapes(old['shape'],cfg,fast);names=['f0_two_channel_drum','f0_c0_drum_pressure_pad','f0_c0_drum_adjuster_M1p6','f0_c0_drum_nut_M1p6'];new=[];records=[];bodies=[]
 for name,shape in zip(names,local):
  part=dict(name=name,group='UNQUALIFIED_REUSABLE_DRUM_TERMINATION',shape=shape,role='UNLOADED_RADIAL_CLAMP_NOT_PULLTESTED');body=evaluate(shape);file=out/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid/disconnected clamp part:'+name)
  records.append(dict(part=name,STL_SHA256=sha(file),CAD_volume_mm3=float(saved.volume)));bodies.append(body);new.append(part)
 fixed=[p for p in parts if p['name']!=old['name']];obstacles=[(p['name'],evaluate(p['shape'])) for p in fixed];hits=[]
 for i,(name,body) in enumerate(zip(names,bodies)):
  for h in intersections(body,[*obstacles,*zip(names[i+1:],bodies[i+1:])]):hits.append(dict(changed_part=name,**h))
 (out/'assembly_delta_recipe.json').write_text(json.dumps(dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=[old['name']],add_parts=new),indent=2))
 for f in (Path(__file__),spec,fastpath,BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py',BASE/'cad/distal_keeper_service.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DRUM_WIRE_CLAMP_STATIC_REVIEW' if hits else 'ONE_UNLOADED_DRUM_CLAMP_STATIC_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,solid_intersections=hits,candidate_part_count=len(fixed+new),actual_pullout_N=None,actual_preload_N=None,actual_wire_friction=None,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='One c0 free-feed-end drum clamp on actual f0 drum;integral body/pad/nominal catalog cap screw/nut. All other hardware retained. Adjuster intentionally not seated against body;no torque-to-preload inference. Wire/pad initially unloaded with gaps,not a no-slip constraint or actual gripping result. New drum volume/inertia/rotating envelope changes;genericD6shaft/horn fit unqualified. Thread/pilot/process/material/nut capture/drive access/wire crush/slip/friction/pullout/fatigue and c1 design not qualified. No Native/holding/STEP approval.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],hits=hits)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_root_nut_hood1032');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_DRUM_CLAMP_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s','solid_intersections') if k in d}))
if __name__=='__main__':main()
