"""Actual finite straight wire cylinders vs indexed CAD CSG, reference pose only."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha
from generate import world,width,guide_normal,guide_outboard
from wire_bore_audit import radial_extent

def audit(candidate):
 source=BASE/'meshes'/candidate/'assembly_recipe.json';a=json.loads(source.read_text());cfg=a['baseline_config'];td=cfg['tendon'];parts={p['name']:p for p in a['parts']};records=[]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  for c,side in enumerate((-1,1)):
   points=np.asarray([world(cfg,[x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)],angle) for x in [0]+td['guide_stations']])
   directions=np.diff(points,axis=0);directions/=np.linalg.norm(directions,axis=1)[:,None]
   for k,x in enumerate(td['guide_stations']):
    key=f'f{f}_c{c}_s{k}';ring=parts[key+'_eyelet'];axis=np.asarray(ring['shape']['matrix'])[:3,0];branches=[directions[k]]+([directions[k+1]] if k+1<len(directions) else [])
    required=max(radial_extent(axis,b,1.,td['wire_radius']) for b in branches);hits=[]
    # Full adjacent straight segments, not only the bore end planes.
    for seg in [k]+([k+1] if k+2<len(points) else []):
     wire=trimesh.creation.cylinder(radius=td['wire_radius'],segment=points[seg:seg+2],sections=64)
     for suffix in ('eyelet','support'):
      solid=evaluate(parts[key+'_'+suffix]['shape']);intersection=trimesh.boolean.intersection([wire,solid],engine='manifold')
      hits.append(dict(segment=seg,part=key+'_'+suffix,intersection_volume_mm3=float(intersection.volume),empty=bool(len(intersection.faces)==0)))
    records.append(dict(finger=f,cable=c,station_mm=x,required_bore_radius_mm=required,bore_radius_mm=td['guide_hole_radius'],necessary_condition=required<=td['guide_hole_radius'],finite_segment_intersections=hits))
 return dict(candidate=candidate,recipe_sha256=sha(source),records=records,necessary_condition_failures=sum(not r['necessary_condition'] for r in records),positive_solid_intersections=sum(h['intersection_volume_mm3']>0 for r in records for h in r['finite_segment_intersections']),maximum_intersection_mm3=max(h['intersection_volume_mm3'] for r in records for h in r['finite_segment_intersections']))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidates',nargs='+',required=True);args=p.parse_args();out=BASE/'results'/args.tag;out.mkdir(exist_ok=False)
 result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),scope='STATIC_REFERENCE_STRAIGHT_SEGMENTS_ONLY; no rounded bend, moving CCD, strength, friction or Native qualification. Float32 Manifold intersections retain all signed volumes; no clearance epsilon.',minimum_bend_radius_mm=None,candidates=[audit(c) for c in args.candidates])
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps([{k:v for k,v in c.items() if k!='records'} for c in result['candidates']],indent=2))
if __name__=='__main__':main()
