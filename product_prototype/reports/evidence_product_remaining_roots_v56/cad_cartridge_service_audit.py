"""Sampled geometric removal checks,NOT swept collision or physical service PASS.

Object/tendons must be removed and retaining screws taken out first. The
remaining actual CAD parts/proxies stay present. No Skin deformation prescribed.
"""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,root_frame,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='b3_manufacturing_spotface_v18');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'meshes'/a.candidate/'assembly_recipe.json';assembly=json.loads(source.read_text());parts=assembly['parts'];shapes=[evaluate(p['shape']) for p in parts];records=[]
 for finger,angle in enumerate(assembly['baseline_config']['palm']['angles_deg']):
  moving=[i for i,p in enumerate(parts) if p['finger']==finger and (p['group'] in ('cartridge','clamp','finger','eyelet','support') or any(t in p['name'] for t in ('_clamp_bolt_','_clamp_nut_','_retaining_nut_')))];removed=[i for i,p in enumerate(parts) if p['finger']==finger and '_retaining_bolt_' in p['name']];fixed=[i for i in range(len(parts)) if i not in moving and i not in removed];axis=root_frame(assembly['baseline_config'],angle)[:3,0]
  for distance in (5,10,15,20):
   hits=[]
   for i in moving:
    shifted=shapes[i].copy();shifted.apply_translation(distance*axis)
    for j in fixed:
     if np.any(np.minimum(shifted.bounds[1],shapes[j].bounds[1])-np.maximum(shifted.bounds[0],shapes[j].bounds[0])<=0):continue
     result=trimesh.boolean.intersection([shifted,shapes[j]],engine='manifold',check_volume=True);volume=float(result.volume) if not result.is_empty else 0.
     if volume>1e-6:hits.append(dict(moving=parts[i]['name'],fixed=parts[j]['name'],volume_mm3=volume))
   records.append(dict(finger=finger,positive_root_axis_withdrawal_mm=distance,removed_retaining_screws=len(removed),moving_parts=len(moving),positive_intersections=hits,status='SAMPLED_REMOVAL_BLOCKED' if hits else 'NO_POSITIVE_INTERSECTION_AT_THIS_SAMPLE_NOT_CCD_PASS'))
 result=dict(status='CARTRIDGE_SAMPLED_SERVICE_DIAGNOSTIC_NOT_SWEPT_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_recipe_sha256=sha(source),candidate=a.candidate,records=records,
             prerequisites=['object removed','zero actuation and wire disconnected','two normal retaining screws removed','motor/frame and other fingers remain present'],
             scope='Rigid movement of manufactured CAD cartridge for service only,NOT driven deformation or Native SOFA dynamics.Not a continuous swept-clearance test.No full wire-routing model;pinch/tool/force/adhesive service unverified.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(samples=len(records),blocked_samples=sum(bool(r['positive_intersections']) for r in records),maximum_intersection_mm3=max((h['volume_mm3'] for r in records for h in r['positive_intersections']),default=0.)),indent=2))
if __name__=='__main__':main()
