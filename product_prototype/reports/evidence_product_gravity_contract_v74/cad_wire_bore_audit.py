"""Analytic straight-branch wire/finite-bore necessary clearance,NOT bend CCD.

At an eyelet end plane,an oblique radius-r wire has ellipse semiaxis r/cos(theta).
For a branch through the eyelet centre,the radial extent is h*tan(theta)+r/cos.
No radius floor,wire removal or falsely prescribed driven shape is used.
"""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha
from generate import world,width,guide_outboard,guide_normal
from finite_guide_product import guide_basis

def radial_extent(axis,direction,half_length,wire_radius):
 a=np.asarray(axis,float);v=np.asarray(direction,float)
 if np.linalg.norm(a)==0 or np.linalg.norm(v)==0:raise ValueError('undefined bore/branch direction')
 a/=np.linalg.norm(a);v/=np.linalg.norm(v);cosine=abs(float(a@v))
 if cosine==0:raise ValueError('branch parallel to bore face:reject,not divide by epsilon')
 cosine=min(cosine,1.) # dot-product roundoff bound only,not a physical radius margin
 return half_length*np.sqrt(max(0.,1-cosine*cosine))/cosine+wire_radius/cosine

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'meshes/b3_manufacturing_service_v19/assembly_recipe.json';cfg=json.loads(source.read_text())['baseline_config'];td=cfg['tendon'];records=[]
 for finger,angle in enumerate(cfg['palm']['angles_deg']):
  for cable,side in enumerate((-1,1)):
   local=[np.array([x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)]) for x in [0]+td['guide_stations']];points=np.asarray([world(cfg,p,angle) for p in local]);segments=np.diff(points,axis=0);segments/=np.linalg.norm(segments,axis=1)[:,None]
   for k,x in enumerate(td['guide_stations']):
    branches=[segments[k]]+([segments[k+1]] if k+1<len(segments) else []);axis=guide_basis(cfg,local[k+1],angle)[:,0];bisector=np.sum(branches,axis=0)
    if np.linalg.norm(bisector)==0:raise ValueError('undefined opposite-branch bisector')
    for label,direction in [('existing_manufactured_tangent',axis),('UNBUILT_branch_bisector_candidate',bisector)]:
     extent=max(radial_extent(direction,b,1.,td['wire_radius']) for b in branches);records.append(dict(finger=finger,cable=cable,station_mm=x,axis_model=label,minimum_required_bore_radius_mm=float(extent),existing_bore_radius_mm=td['guide_hole_radius'],necessary_radial_margin_mm=float(td['guide_hole_radius']-extent),status='FAIL_STRAIGHT_BRANCH_BORE_CONDITION' if extent>td['guide_hole_radius'] else 'NECESSARY_BORE_CONDITION_ONLY_NOT_WIRE_CLEARANCE_PASS'))
 result=dict(status='WIRE_BORE_NECESSARY_CONDITION_DIAGNOSTIC_NOT_ROUTING_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),source_recipe_sha256=sha(source),records=records,wire_radius_mm=td['wire_radius'],eyelet_length_mm=2.,physical_wire_minimum_bend_radius_mm=None,actual_wire_and_guide_material=None,
             scope='Actual manufactured reference guide/path dimensions;straight cylindrical branch necessary condition only,not real rounded wire solution,support collision,friction,moving clearance or Native driven results.Bisector orientation is an UNBUILT independent design hypothesis,not an observed improvement.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({label:dict(failed=sum(r['status'].startswith('FAIL') for r in records if r['axis_model']==label),maximum_required_bore_radius_mm=max(r['minimum_required_bore_radius_mm'] for r in records if r['axis_model']==label)) for label in ('existing_manufactured_tangent','UNBUILT_branch_bisector_candidate')},indent=2))
if __name__=='__main__':main()
