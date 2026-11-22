"""Read-only accepted-state/provenance analysis;no force or state correction."""
import argparse,csv,json,xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from metric_mesh_query import closest_si,triangle_reference
def vec(s):return np.fromstring(s,sep=' ')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];inputs={}
 for case in a.cases:
  folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());rows=list(csv.DictReader((folder/'wire.csv').open()));scene=ET.parse(folder/'scene.scn').getroot();topology=scene.find("./Node[@name='wheel']/Node/MeshTopology");mesh=trimesh.Trimesh(vertices=vec(topology.get('position')).reshape(-1,3),faces=vec(topology.get('triangles')).astype(int).reshape(-1,3),process=False)
  q=np.array([vec(r['rigid_q'])[:3] for r in rows]);native=np.array([vec(r['object_impulse_Ns_Nms']) for r in rows]);closest,dist,tri=closest_si(mesh,q);gaps=dist-meta['wire_radius_m'];sums=defaultdict(lambda:np.zeros(6));active_pairs=set();positive_lambda=0
  for r in csv.DictReader((folder/'response.csv').open()):
   sums[float(r['time_s'])]+=vec(r['object_impulse_Ns_Nms'])
   if np.linalg.norm(vec(r['object_impulse_Ns_Nms']))>0:
    active_pairs.add(tuple(sorted([r['model0'],r['model1']])));positive_lambda+=float(r['lambda_Ns'])>0
  response_error=max(float(np.max(abs(sums[float(r['time_s'])]-native[i]))) for i,r in enumerate(rows))
  active=np.where(np.linalg.norm(native[:,:3],axis=1)>0)[0];first=int(active[0]) if len(active) else None;pair_ok=bool(active_pairs) and all(any('/wheel/surface/' in x for x in pair) and any('/wire_section/cross_section/' in x for x in pair) for pair in active_pairs)
  # Observed detector geometry at the first impulse time;do not assume same state as accepted q.
  detected=[]
  if first is not None:
   target=float(rows[first]['time_s'])
   for r in csv.DictReader((folder/'detector.csv').open()):
    if float(r['accepted_time_s'])==target and '/wire_section/' in r['model0']+r['model1']:detected.append(dict(models=[r['model0'],r['model1']],p0=vec(r['detected_point0']).tolist(),p1=vec(r['detected_point1']).tolist()))
  rec=dict(case=case,status='PASS_RESPONSE_OWNERSHIP_ONLY' if pair_ok and response_error<1e-20 else 'FAIL_RESPONSE_OWNERSHIP',actual_active_model_pairs=sorted(active_pairs),response_vs_body_max_impulse_error_Ns_Nms=response_error,active_steps=len(active),positive_multiplier_rows=positive_lambda,minimum_accepted_triangle_gap_m=float(min(gaps)),first_active=None if first is None else dict(accepted_time_s=float(rows[first]['time_s']),accepted_center_m=q[first].tolist(),mesh_closest_point_m=closest[first].tolist(),mesh_triangle_id=int(tri[first]),mesh_gap_m=float(gaps[first]),impulse_Ns=native[first,:3].tolist(),detector_points_same_journal_time=detected),physical_contact_qualified=False,scope='Collision model pair -> response rows -> body impulse verified inaggregate. Detector timestamp labels AnimateEnd observation,NOT proof of accepted-geometry detection. Nonzero force atpositive trianglegap is a model/geometry-policy discrepancy to investigate,NOT frictionless-pulleyPASS. No area/pressure/physical energy or time convergence claim.')
  records.append(rec)
  rec['query_units']='Input/output SI;internal triangle query in mm,NO contact tolerance alteration'
  rec['corrected_initial_mesh_gap_m']=float(closest_si(mesh,np.array(meta['initial_q_m'])[None,:])[1][0]-meta['wire_radius_m'])
  rec['closest_point_independent_triangle_reference_error_m']=float(max(np.linalg.norm(triangle_reference(point,mesh.triangles[index])-near) for point,index,near in zip(q,tri,closest)))
  rec['supersedes_unconditioned_SI_gap_analysis_only']=True
  rec['scope']='Collision pair/response/body impulse provenance only. Old SI trimesh closest routine misclassified small triangle faces;conditioned mm query checked against independent dimensionless triangle reference. No SOFA state/tolerance changed;old raw preserved. Negative gaps,however small,remain raw. No whole-wire/contact/time/energy qualification.'
  for name in ('summary.json','scene.scn','wire.csv','response.csv','detector.csv'):inputs[str((folder/name).relative_to(BASE))]=sha(folder/name)
 inputs[str((Path(__file__).parent/'metric_mesh_query.py').relative_to(BASE))]=sha(Path(__file__).parent/'metric_mesh_query.py')
 for module in (trimesh.proximity,trimesh.triangles):inputs[str(Path(module.__file__))]=sha(Path(module.__file__))
 result=dict(status='WIRE_SECTION_PROVENANCE_ANALYSIS_NOT_PHYSICS_QUALIFICATION',input_hashes=inputs,trimesh_version=trimesh.__version__,source_sha256=sha(Path(__file__)),records=records)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
