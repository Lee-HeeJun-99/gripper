"""Finite thrust-shim design to reduce nominal endplay;material/friction unqualified."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,cut,transform,evaluate,sha
from deformed_wire_screen import probes

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);target=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;target.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes/b3_bridge_service_v28/full_assembly_recipe.json';parent=json.loads(src.read_text());fixed=parent['parts'];fixed_shapes=[evaluate(p['shape']) for p in fixed];parts=[];shapes=[];records=[];hits=[]
 for p in fixed:
  if p['group']!='headed_pin_proxy':continue
  M=np.asarray(p['shape']['matrix']);wheel=p['name'].replace('_headed_pin','')
  for side,(z0,z1) in enumerate(((-1.3,-.9),(.9,1.3))):
   name=wheel+f'_thrust_shim{side}';op=transform(cut(cyl(1.25,z0,z1),cyl(.6,z0-.1,z1+.1)),M);shape=evaluate(op);file=target/(name+'.stl');file.write_text(shape.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
   if not read.is_volume or read.body_count!=1:raise ValueError('shim STLreadback invalid')
   parts.append(dict(name=name,shape=op,group='thrust_shim'));shapes.append(shape);records.append(dict(part=name,saved_STL_sha256=sha(file),closed_positive_singlebody=True,volume_mm3=float(shape.volume),mass_kg=None))
   for other,solid in zip(fixed,fixed_shapes):
    if np.any(np.minimum(shape.bounds[1],solid.bounds[1])-np.maximum(shape.bounds[0],solid.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([shape,solid],engine='manifold')
    if len(hit.faces):hits.append(dict(shim=name,part=other['name'],signed_volume_mm3=float(hit.volume),pair_type='NOMINAL_WHEEL_FACE_MATING' if other['name']==wheel else 'UNRESOLVED'))
 leadsrc=BASE/'results/product_motor_lead748/summary.json';wirehits=[]
 for wire in [r for r in json.loads(leadsrc.read_text())['records'] if r['model']=='perimeter_rounded_candidate']:
  import math
  for sample,probe in probes(np.asarray(wire['route_mm']),.25+2*(1-math.cos(math.radians(.5)))):
   for p,solid in zip(parts,shapes):
    if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
    if len(hit.faces):wirehits.append(dict(shim=p['name'],signed_volume_mm3=float(hit.volume),sample=sample))
 recipe=dict(units='mm',parts=parts);full=dict(units='mm',parts=fixed+parts)
 for directory in (target,draw):
  (directory/'assembly_recipe.json').write_text(json.dumps(recipe,indent=2));(directory/'full_assembly_recipe.json').write_text(json.dumps(full,indent=2))
 result=dict(status='THRUST_SHIM_CANDIDATE_NOT_TOLERANCE_OR_FRICTION_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),input_hashes={str(p.relative_to(BASE.parent)):sha(p) for p in (src,leadsrc)},records=records,intersections=hits,wire_intersections=wirehits,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='36nominalOD2.5/ID1.2/thickness0.4mm washers replace open0.5mm sidegaps with0.1mm nominal sidegaps. Not selected supplier/material/friction/PV/strength/tolerance. Mating wheel-face results retained,not hidden. Source770coarsetolerance case stillFAIL. Removing axles requires capture loose shims;no physicalassembly or Native dynamics certification.')
 for directory in (out,draw):(directory/'summary.json').write_text(json.dumps(result,indent=2))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(shims=len(parts),solid_hits=len(hits),wire_hits=len(wirehits),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
