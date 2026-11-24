"""Read-only sampled wire/actual polygon-frustum solid intersection audit (mm)."""
import argparse,csv,json
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from rounded_bore_wire import geometry,inside
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='rounded_bore_wire1633');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;m,inner=geometry();meta=json.loads((src/'geometry.json').read_text());assert meta['volume_mm3']==m.volume;history=[];pair={}
 for r in read(src/'response_rows.csv'):
  if float(r['lambda_Ns'])!=0:
   key=r['model0']+' | '+r['model1'];pair[key]=pair.get(key,0)+1
 states=read(src/'states.csv');surface=read(src/'surface.csv');assert len(states)==len(surface)==1200
 for r,s in zip(states,surface):
  assert r['time_s']==s['time_s'];points=(np.fromstring(s['q'],sep=' ').reshape(-1,3)-[.01,0,0])*1000;mask=inside(points,inner);depth=0.
  if mask.any():depth=float(trimesh.proximity.closest_point(m,points[mask])[1].max())
  history.append(dict(time_s=float(s['time_s']),inside_vertices=int(mask.sum()),maximum_vertex_penetration_mm=depth,solver_iterations=int(r['solver_iterations']),contact_impulse_norm_Ns=float(np.linalg.norm(np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')[:3]))))
 bad=[r for r in history if r['inside_vertices']];peak=max(history,key=lambda r:r['maximum_vertex_penetration_mm']);d=dict(status='FAIL_ACTUAL_WIRE_SOLID_INTERSECTION' if bad else 'NO_SAMPLED_VERTEX_INTERSECTION_ONLY',case=a.case,outputs=len(history),negative_outputs=len(bad),first_negative_time_s=bad[0]['time_s'] if bad else None,maximum_vertex_penetration_mm=peak['maximum_vertex_penetration_mm'],peak_time_s=peak['time_s'],maximum_solver_iterations=max(r['solver_iterations'] for r in history),negative_outputs_without_contact_impulse=sum(r['contact_impulse_norm_Ns']==0 for r in bad),actual_nonzero_model_pairs=pair,minimum_positive_gap_mm=None,scope='Exact membership of actual32-sided piecewise-linear inner-profile solid;distance to actual triangles evaluated in mm. Negative vertex proves intersection;no negative vertices would NOT certify surface facets/CCD. No tolerance floor or output correction. Not hardware/grasp/material/time convergence PASS.',source_sha256=sha(Path(__file__)),input_sha256={f:sha(src/f) for f in ('scene.scn','geometry.json','surface.csv','states.csv','response_rows.csv')});(out/'history.json').write_text(json.dumps(history));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
