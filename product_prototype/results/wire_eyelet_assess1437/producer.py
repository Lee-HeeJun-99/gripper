"""Actual finite-wire states,solid-gap inventory and Native contact provenance."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from eyelet_entry_geometry import solid_distance
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 entry=json.loads((BASE/'results/eccentric_eyelet1415/summary.json').read_text());ecc=np.linalg.norm(next(r for r in entry['records'] if r.get('route')==0 and r.get('guide')==4 and 'trim_mm'in r)['bore_centre_offset_mm']);polygon=np.array(entry['eyelet_meridional_solid_polygon_mm']);polygon[1:3,0]+=ecc
 for case in ('wire_eyelet1431','wire_eyelet_slide1432','wire_eyelet_audit1436'):
  src=BASE/'results'/case;rows=read(src/'states.csv');surface=read(src/'surface.csv');solver=read(src/'solver.csv');root=ET.parse(src/'scene.scn').getroot();initial=np.fromstring(root.find("Node[@name='wire']/Node/MeshTopology").get('position'),sep=' ').reshape(-1,3);q0=np.fromstring(root.find("Node[@name='wire']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  def gap(points):
   points=points*1000;radial=np.sqrt((points[:,1]-ecc)**2+points[:,2]**2);return float(solid_distance(np.column_stack([radial,points[:,0]-10]),polygon).min())
  history=[]
  for row,s,sol in zip(rows,surface,solver):
   assert float(row['time_s'])==float(s['time_s'])==float(sol['time_s']);q=np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7);v=np.fromstring(row['rigid_v'],sep=' ').reshape(-1,6);points=np.fromstring(s['q'],sep=' ').reshape(-1,3);impulse=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ');history.append(dict(time_s=float(row['time_s']),surface_vertex_solid_gap_mm=gap(points),root_axial_motion_mm=float((q[0,0]-q0[0,0])*1000),tip_axial_motion_mm=float((q[-1,0]-q0[-1,0])*1000),contact_force_N=(impulse[:3]/.0001).tolist(),solver_error=float(sol['error']),solver_iterations=int(sol['iterations'])))
  pairs={};partition=None;purity=None
  if (src/'response_rows.csv').exists():
   tindex={float(r['time_s']):i for i,r in enumerate(rows)};sums=np.zeros((len(rows),6))
   for row in read(src/'response_rows.csv'):
    pair=(row['model0'],row['model1']);pairs[' | '.join(pair)]=pairs.get(' | '.join(pair),0)+1;sums[tindex[float(row['time_s'])]]+=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')
   total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);partition=float(abs(sums-total).max());old=read(BASE/'results/wire_eyelet_slide1432/states.csv');purity=all(r==s for r,s in zip(rows,old)) and len(rows)==len(old)
  records.append(dict(case=case,initial_surface_vertex_gap_mm=gap(initial),minimum_saved_surface_vertex_gap_mm=min(r['surface_vertex_solid_gap_mm'] for r in history),maximum_contact_force_N=max(float(np.linalg.norm(r['contact_force_N'])) for r in history),endpoint=history[-1],response_pairs=pairs,response_partition_max_error_Ns_Nms=partition,observer_state_journal_exact=purity,history=history,input_hashes={f:sha(src/f) for f in ('scene.scn','states.csv','surface.csv','solver.csv','summary.json')}))
 result=dict(status='FINITE_WIRE_CONTACT_SLIDING_INVENTORY_ONLY',records=records,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scope='Signed gaps on actual surface VERTICES,not continuousfacets/wholewire nonpenetration. Negative proves sampled interference;positive does not certify continuoussurface. Native impulse/dt yields resultantforce,not pressure. Slidingzero-friction researchassumption,not calibratedfriction/contact/time/mesh or graspPASS. Audit checks actualresponsepair/rowpartition and journalpurity separately.');(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps([{k:v for k,v in r.items() if k not in ('history','input_hashes')} for r in records],indent=2))
if __name__=='__main__':main()
