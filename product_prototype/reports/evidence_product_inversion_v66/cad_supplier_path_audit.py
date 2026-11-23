"""Whole lead-route tangent budget; CAD prerequisite, not swept/physics clearance."""
import argparse,json,math,subprocess,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha,sector
from generate import world,width,guide_normal,guide_outboard
from supplier_root_wheel import supplier_dimensions

def tangent_budget(points,radius):
 p=np.asarray(points,float);segments=np.linalg.norm(np.diff(p,axis=0),axis=1)
 if radius<=0 or not np.isfinite(p).all() or np.any(segments<=0):raise ValueError('invalid route')
 trims=np.zeros(len(p))
 for k in range(1,len(p)-1):
  u=(p[k]-p[k-1])/segments[k-1];v=(p[k+1]-p[k])/segments[k]
  angle=math.atan2(np.linalg.norm(np.cross(u,v)),float(u@v))
  if angle>=math.pi-1e-12:raise ValueError('reversing corner undefined')
  trims[k]=radius*math.tan(angle/2)
 margin=segments-trims[:-1]-trims[1:]
 return dict(segment_lengths_mm=segments.tolist(),corner_trims_mm=trims.tolist(),straight_remainder_mm=margin.tolist(),status='TANGENT_BUDGET_ONLY_CLEAR' if np.all(margin>0) else 'FAIL_OVERLAPPING_TANGENT_INTERVALS')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--tag',required=True);a=ap.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic()
 src=BASE/'meshes/b3_supplier_eyelet_seat_v43/full_assembly_recipe.json';geometry=BASE/'meshes/b3_manufacturing_bore_v21/assembly_recipe.json';cfgfile=BASE/'config/wire_bend_supplier_v40.json';parent=json.loads(src.read_text());metadata=json.loads(geometry.read_text());cfg=metadata['baseline_config'];drive=metadata['manufacturing_config']['drive'];d=supplier_dimensions(json.loads(cfgfile.read_text()));parts=parent['parts'];records=[]
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  S=sector(angle);z0,z1=drive['drum_z_range_mm'];zs=[z0+1.75,(z0+3.5+z1-1)/2]
  for c,side in enumerate((-1,1)):
   pull=np.asarray(world(cfg,[0,side*(width(cfg,0)/2+guide_outboard(cfg,0)),guide_normal(cfg,0)],angle));local=(np.linalg.inv(S)@np.r_[pull,1])[:3];y=local[1];z=zs[c];end=drive['motor_center_radius_mm']+drive['drum_effective_wire_radius_mm']
   points=np.array([local,[70,y,local[2]],[70,y,z],[end,y,z],[end,0,z]])
   names=[f'f{f}_c{c}_turn{k}' for k in (1,2,3)]
   if not all(sum(p['name']==n for p in parts)==1 for n in names):raise ValueError('turn coverage mismatch')
   records.append(dict(finger=f,cable=c,parts=names,design_polyline_local_mm=points.tolist(),budget=tangent_budget(points,d['wire_centre_pitch_radius_mm'])))
 roots=[p['name'] for p in parts if p['name'].endswith('_root_redirect')]
 if len(roots)!=6:raise ValueError('root coverage mismatch')
 result=dict(status='WHOLE_ROUTE_PREREQUISITE_AUDIT_NOT_ASSEMBLY_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (src,geometry,cfgfile,Path(__file__),BASE/'cad/lead_pulley_candidate.py',BASE/'cad/supplier_root_wheel.py')},dimensions=d,remaining_legacy_root_parts=[n for n in roots if n!='f0_c0_root_redirect'],legacy_turn_parts=[n for r in records for n in r['parts']],legacy_groove_root_diameter_mm=3.5,required_groove_root_diameter_mm=2*d['groove_root_radius_mm'],records=records,runtime_s=time.monotonic()-start,scope='Analytic tangent-interval budget on actual lead design polylines. All18 legacy turns and5 legacy Roots still fail supplier diameter recommendation. Positive budget is NOT finite-wheel/fork/wire clearance. Drum wrap, moving Skin guides and wire constitutive data NOT qualified. No Native run,STEP or product PASS.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
