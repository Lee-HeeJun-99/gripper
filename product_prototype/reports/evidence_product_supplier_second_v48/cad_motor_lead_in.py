"""Conditional finite lead-in design,not motor interface or pulley assembly qualification."""
import argparse,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sector,sha
from generate import world,width,guide_normal,guide_outboard
from rounded_wire_path import fillet
from deformed_wire_screen import probes

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();source=BASE/'meshes'/a.candidate/'assembly_recipe.json';recipe=json.loads(source.read_text());cfg=recipe['baseline_config'];drive=recipe['manufacturing_config']['drive'];solids=[(p,evaluate(p['shape'])) for p in recipe['parts']];records=[];u=drive['motor_center_radius_mm'];r=drive['drum_effective_wire_radius_mm'];z0,z1=drive['drum_z_range_mm'];grooves=[(z0+1+z0+2.5)/2,(z0+3.5+z1-1)/2]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  S=sector(angle)
  for c,side in enumerate((-1,1)):
   pull=np.asarray(world(cfg,[0,side*(width(cfg,0)/2+guide_outboard(cfg,0)),guide_normal(cfg,0)],angle));local=(np.linalg.inv(S)@np.r_[pull,1])[:3];y=local[1];z=grooves[c];tangent=np.array([u+r,0,z])
   for model in ('direct_unrouted_diagnostic','perimeter_rounded_candidate'):
    points=np.array([local,tangent]) if model.startswith('direct') else np.array([local,[70,y,local[2]],[70,y,z],[u+r,y,z],tangent]);route,sag,trim=fillet(points,2.);route=(np.c_[route,np.ones(len(route))]@S.T)[:,:3];hits=[]
    for sample,probe in probes(route,cfg['tendon']['wire_radius']+sag):
     for part,solid in solids:
      if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
      hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
      if len(hit.faces):hits.append(dict(sample=sample,part=part['name'],signed_volume_mm3=float(hit.volume),classification='INTENDED_DRUM_TANGENCY_REQUIRES_CONTACT_CHECK' if part['name']==f'f{f}_two_channel_drum' else 'UNRESOLVED_OBSTACLE'))
    records.append(dict(finger=f,cable=c,model=model,route_mm=route.tolist(),length_mm=float(np.linalg.norm(np.diff(route,axis=0),axis=1).sum()),groove_height_mm=z,maximum_radial_envelope_mm=float(np.linalg.norm(route[:,:2],axis=1).max()+cfg['tendon']['wire_radius']+sag),intersections=hits))
 result=dict(status='CONDITIONAL_LEAD_IN_GEOMETRY_NOT_HARDWARE_ASSEMBLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),source_recipe_sha256=sha(source),records=records,runtime_s=time.monotonic()-start,pulley_radius_mm=2.,wire_supplier_minimum_radius_mm=None,scope='SameV21parts/finitewire,compare direct path vs deliberate perimeter route atx70mm and horizontal generic drum tangency. Motor output axis is ONLY assumed CAD axis;not supplier verified. Turning pulleys/supports NOT modeled;extra envelope/stroke/friction/material/strength unqualified. Endpoint drum contact kept and classified,not hidden. Rest design only,NOT SOFA.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({model:dict(obstacle_hits=sum(h['classification']=='UNRESOLVED_OBSTACLE' for r in records if r['model']==model for h in r['intersections']),drum_hits=sum(h['classification'].startswith('INTENDED') for r in records if r['model']==model for h in r['intersections'])) for model in ('direct_unrouted_diagnostic','perimeter_rounded_candidate')},indent=2))
if __name__=='__main__':main()
