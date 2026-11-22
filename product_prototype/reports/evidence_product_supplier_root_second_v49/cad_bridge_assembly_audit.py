"""Finite hole/tool/axle sampled-service checks;not preload,tolerance or CCD qualification."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,transform,evaluate,sector,sha

def hits(shape,parts,shapes,exclude=()):
 result=[]
 for part,solid in zip(parts,shapes):
  if part['name'] in exclude:continue
  if np.any(np.minimum(shape.bounds[1],solid.bounds[1])-np.maximum(shape.bounds[0],solid.bounds[0])<=0):continue
  value=trimesh.boolean.intersection([shape,solid],engine='manifold')
  if len(value.faces):result.append(dict(part=part['name'],signed_volume_mm3=float(value.volume)))
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes'/a.candidate/'full_assembly_recipe.json';assembly=json.loads(src.read_text());parts=assembly['parts'];shapes=[evaluate(p['shape']) for p in parts];gauges=[];tools=[];pins=[]
 for f,angle in enumerate((0,120,240)):
  S=sector(angle)
  for c,side in enumerate((1,-1)):
   for j,x in enumerate((44,52)):
    names=['palm_bridge_bores',f'f{f}_c{c}_bridge'];indices=[i for i,p in enumerate(parts) if p['name'] in names];g=evaluate(transform(cyl(1.65,1,20,(x,side*30)),S));gauges.append(dict(finger=f,cable=c,bolt=j,gauge_radius_mm=1.65,nominal_bore_radius_mm=1.7,intersections=hits(g,[parts[i] for i in indices],[shapes[i] for i in indices])))
    tool=evaluate(transform(cyl(2.25,21.2,46.2,(x,side*30)),S));tools.append(dict(finger=f,cable=c,bolt=j,tool_radius_mm=2.25,tool_length_mm=25,intersections=hits(tool,parts,shapes,exclude=[f'f{f}_c{c}_mount_bolt{j}'])))
 for p,shape in zip(parts,shapes):
  if p['group']!='headed_pin_proxy':continue
  axis=np.asarray(p['shape']['matrix'])[:3,2];ownnut=p['name'].replace('_headed_pin','_axle_nut')
  for distance in (2,5,10):
   shifted=shape.copy();shifted.apply_translation(-distance*axis);pins.append(dict(pin=p['name'],negative_axis_withdrawal_mm=distance,removed_part=ownnut,intersections=hits(shifted,parts,shapes,exclude=[p['name'],ownnut])))
 result=dict(status='NOMINAL_ASSEMBLY_GAUGE_AND_SAMPLED_SERVICE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),source_recipe_sha256=sha(src),hole_gauges=gauges,mount_driver_access=tools,pin_withdrawal_samples=pins,runtime_s=time.monotonic()-start,scope='12finite bore gauges across actualPalm/bridge,12nominal25mmshank-only driver paths,54actualheadedpin withdrawal samples after ownnut removed. Existing hardware retained. Not continuous insertion/removal,thread engagement,actual supplier tool/hand access,preload,tolerance/strength or assemblyPASS.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(blocked_holes=sum(bool(r['intersections']) for r in gauges),blocked_drivers=sum(bool(r['intersections']) for r in tools),blocked_pin_samples=sum(bool(r['intersections']) for r in pins),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
