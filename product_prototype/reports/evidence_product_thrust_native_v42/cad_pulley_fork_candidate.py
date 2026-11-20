"""Finite pulley fork/pin modules;mount-to-Palm and material strength NOT qualified."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,box,cyl,union,cut,transform,evaluate,sha
from deformed_wire_screen import probes

def fork_recipe():
 return cut(union(box([-6,-1.5,-2.4],[-5,1.5,2.4]),box([-5,-1.5,-2.4],[.5,1.5,-1.4]),box([-5,-1.5,1.4],[.5,1.5,2.4])),cyl(.6,-2.5,2.5))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);target=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;target.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();wheel_source=BASE/'meshes/b3_lead_pulley_modules_v22/assembly_recipe.json';lead_source=BASE/'results/product_motor_lead748/summary.json';parent_source=BASE/'meshes/b3_manufacturing_bore_v21/assembly_recipe.json';wheels=json.loads(wheel_source.read_text());leads=json.loads(lead_source.read_text());parent=json.loads(parent_source.read_text());fixed=[(p['name'],evaluate(p['shape'])) for p in parent['parts']+wheels['parts']];parts=[];solids=[];metrics=[]
 for wheel in wheels['parts']:
  words=wheel['name'].split('_');f=int(words[0][1:]);c=int(words[1][1:]);R=np.asarray(wheel['shape']['matrix']);centre=R[:3,3];axis=R[:3,2];route=np.asarray(next(r['route_mm'] for r in leads['records'] if r['model']=='perimeter_rounded_candidate' and r['finger']==f and r['cable']==c));relative=route-centre;distance=np.linalg.norm(relative,axis=1);arc=relative[np.abs(distance-2.)<1e-8]
  if len(arc)<3:raise ValueError('cannot establish actual wire arc orientation')
  facing=arc.sum(axis=0);facing-=axis*(axis@facing);facing/=np.linalg.norm(facing);M=np.eye(4);M[:3,:3]=np.column_stack((facing,np.cross(axis,facing),axis));M[:3,3]=centre
  for suffix,op in [('fork',fork_recipe()),('pin_proxy',cyl(.5,-2.4,2.4))]:
   name=wheel['name']+'_'+suffix;shapeop=transform(op,M);shape=evaluate(shapeop);path=target/(name+'.stl');path.write_text(shape.export(file_type='stl_ascii'));reread=trimesh.load_mesh(path)
   if not reread.is_volume or reread.body_count!=1:raise ValueError('fork/pin STL readback failed')
   parts.append(dict(name=name,shape=shapeop,group=suffix,finger=f));solids.append((name,shape));metrics.append(dict(part=name,volume_mm3=float(shape.volume),saved_STL_sha256=sha(path),closed_positive_singlebody=True,mass_kg=None))
 hits=[]
 for i,(name,shape) in enumerate(solids):
  for other,solid in fixed+solids[i+1:]:
   if np.any(np.minimum(shape.bounds[1],solid.bounds[1])-np.maximum(shape.bounds[0],solid.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([shape,solid],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[name,other],signed_volume_mm3=float(hit.volume)))
 wire_hits=[]
 for wire in [r for r in leads['records'] if r['model']=='perimeter_rounded_candidate']:
  route=np.asarray(wire['route_mm'])
  # conservative global1-degree arc sagitta bound for R2;unchanged0.25wire radius
  import math
  rad=.25+2*(1-math.cos(math.radians(.5)))
  for sample,probe in probes(route,rad):
   for name,solid in solids:
    if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
    if len(hit.faces):wire_hits.append(dict(finger=wire['finger'],cable=wire['cable'],sample=sample,part=name,signed_volume_mm3=float(hit.volume)))
 recipe=dict(units='mm',parts=parts,scope='Unfastened fork/pin modules;no structural connection to Palm and no bearing/retainer qualification.')
 for directory in (target,draw):(directory/'assembly_recipe.json').write_text(json.dumps(recipe,indent=2))
 result=dict(status='FORK_PIN_MODULE_CREATED_NOT_MOUNTED_DRIVE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (wheel_source,lead_source,parent_source)},records=metrics,solid_intersections=hits,wire_envelope_intersections=wire_hits,runtime_s=time.monotonic()-start,pin_diameter_mm=1.,fork_bore_mm=1.2,nominal_axial_wheel_clearance_mm=.5,STEP_generated=False,fabrication_ready=False,scope='18forks/18nominalpins;finite geometry and actual ASCIISTL readback. Fork backs face away from actual designed wire arc. No collision removed. Arms/pins/bracket joints/retention/bearing/material/friction/tolerances/thermal/motor-interface not validated. No mounting connection to Palm:NOT complete assembly.')
 for directory in (out,draw):(directory/'summary.json').write_text(json.dumps(result,indent=2))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(parts=len(metrics),solid_intersections=len(hits),wire_intersections=len(wire_hits),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
