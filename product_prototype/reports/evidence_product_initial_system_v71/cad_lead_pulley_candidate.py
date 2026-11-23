"""Finite turn-pulley modules for conditional lead-in route;mounts/bearings unqualified."""
import argparse,csv,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,union,cut,transform,evaluate,sector,sha
from generate import world,width,guide_normal,guide_outboard

def wheel_recipe():
 return cut(union(cyl(1.75,-.4,.4),cyl(3.,-.9,-.4),cyl(3.,.4,.9)),cyl(.6,-1,1))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);target=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;target.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes'/a.candidate/'assembly_recipe.json';parent=json.loads(src.read_text());cfg=parent['baseline_config'];drive=parent['manufacturing_config']['drive'];parts=[];shapes=[];records=[]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  S=sector(angle);u=drive['motor_center_radius_mm'];z0,z1=drive['drum_z_range_mm'];grooves=[z0+1.75,(z0+3.5+z1-1)/2]
  for c,side in enumerate((-1,1)):
   pull=np.array(world(cfg,[0,side*(width(cfg,0)/2+guide_outboard(cfg,0)),guide_normal(cfg,0)],angle));local=(np.linalg.inv(S)@np.r_[pull,1])[:3];y=local[1];z=grooves[c];points=np.array([local,[70,y,local[2]],[70,y,z],[u+drive['drum_effective_wire_radius_mm'],y,z],[u+drive['drum_effective_wire_radius_mm'],0,z]])
   for k in range(1,len(points)-1):
    incoming=points[k]-points[k-1];outgoing=points[k+1]-points[k];incoming/=np.linalg.norm(incoming);outgoing/=np.linalg.norm(outgoing);normal=np.cross(incoming,outgoing);normal/=np.linalg.norm(normal);theta=math.acos(float(incoming@outgoing));distance=2*math.tan(theta/2);startpoint=points[k]-incoming*distance;center=startpoint+2*np.cross(normal,incoming);R=trimesh.geometry.align_vectors([0,0,1],normal);R[:3,3]=center;R=S@R;name=f'f{f}_c{c}_turn{k}';op=transform(wheel_recipe(),R);shape=evaluate(op);path=target/(name+'.stl');path.write_text(shape.export(file_type='stl_ascii'));reread=trimesh.load_mesh(path)
    if not reread.is_volume or reread.body_count!=1:raise ValueError('pulley saved STL readback failed')
    parts.append(dict(name=name,shape=op,group='conditional_turn_pulley',finger=f));shapes.append(shape);records.append(dict(part=name,center_mm=R[:3,3].tolist(),axis=R[:3,2].tolist(),STL_sha256=sha(path),volume_mm3=float(shape.volume),watertight_readback=bool(reread.is_watertight),mass_kg=None))
 fixed=[(p,evaluate(p['shape'])) for p in parent['parts']];hits=[]
 for part,shape in zip(parts,shapes):
  for other,solid in fixed:
   if np.any(np.minimum(shape.bounds[1],solid.bounds[1])-np.maximum(shape.bounds[0],solid.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([shape,solid],engine='manifold')
   if len(hit.faces):hits.append(dict(pulley=part['name'],part=other['name'],signed_volume_mm3=float(hit.volume)))
 module=dict(units='mm',parts=parts,parent_recipe_sha256=sha(src),scope='Only turn pulleys,not mounted assembly;no shafts/bearings/supports/root inlet pulley yet.')
 (target/'assembly_recipe.json').write_text(json.dumps(module,indent=2));(draw/'assembly_recipe.json').write_text(json.dumps(module,indent=2))
 with (draw/'BOM.csv').open('w') as stream:
  w=csv.writer(stream);w.writerow(['part','qty','nominal_dimensions_mm','status']);w.writerow(['turn pulley',18,'OD6;wire pitch diameter4;groove width0.8;bore1.2;overall width1.8','DESIGN_ONLY material strength friction unverified']);w.writerow(['shaft/bearing/support','TBD','TBD','NOT MODELED']);w.writerow(['root inlet redirect','TBD','TBD','NOT MODELED'])
 result=dict(status='FINITE_PULLEY_MODULES_CREATED_NOT_MOUNTED_ASSEMBLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),parent_recipe_sha256=sha(src),records=records,intersections_with_parent=hits,runtime_s=time.monotonic()-start,mesh_output=str(target.relative_to(BASE.parent)),drawing_output=str(draw.relative_to(BASE.parent)),wire_pitch_radius_mm=2.,wire_radius_mm=cfg['tendon']['wire_radius'],supplier_minimum_bend_radius_mm=None,STEP_generated=False,fabrication_ready=False,scope='Implements18finite wheels at actual designed fillet centers/axes,not prescribed finger deformation. 18saved ASCIISTL readbacks. Wheels against160parentparts checked;pulley-pulley/wire-tube,mounts,shaft,bearings,tolerances,rotational friction and strength NOT YET verified;no actual motor selection or Native dynamics.')
 for d in (out,draw):(d/'summary.json').write_text(json.dumps(result,indent=2))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(pulleys=len(records),parent_intersections=len(hits),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
