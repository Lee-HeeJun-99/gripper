"""Actual skin triangles versus sphere and actual response provenance,not area."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();obj=read(src/'object.csv');times=[float(r['time_s']) for r in obj];centre=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in obj]);radius=float(root.find("Node[@name='object']/Node/SphereCollisionModel").get('radius'));records=[];forces={}
 for r in read(src/'response_rows.csv'):
  if not any('/object/'in r[k] for k in ('model0','model1')):continue
  other=next(r[k] for k in ('model0','model1') if '/object/'not in r[k]);name='skin' if '/skinCollision/'in other else 'guide' if '/guides'in other else 'support' if '/floor/'in other else 'other';key=(float(r['time_s']),name);forces[key]=forces.get(key,np.zeros(6))+np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
 for i in range(3):
  rows=read(src/f'finger{i}.csv');assert [float(r['time_s']) for r in rows]==times;node=root.find(f"Node[@name='finger{i}']/Node[@name='skinCollision']");ids=np.fromstring(node.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);gaps=[]
  for r,c in zip(rows,centre):
   q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);tri=q[ids][faces];near=trimesh.triangles.closest_point(tri,np.repeat(c[None],len(tri),axis=0));gaps.append(float(np.linalg.norm(near-c,axis=1).min()-radius))
  gaps=np.array(gaps);bad=np.flatnonzero(gaps<0);missing=sum(np.linalg.norm(forces.get((times[k],'skin'),np.zeros(6)))==0 for k in bad);records.append(dict(finger=i,minimum_actual_triangle_sphere_gap_mm=float(gaps.min()*1000),negative_geometry_outputs=len(bad),negative_geometry_without_any_skin_response_outputs=int(missing),first_negative_s=None if not len(bad) else times[bad[0]]))
 active=int(sum(bool(np.linalg.norm(v)>0) for (t,n),v in forces.items() if n=='skin'))
 maxima={n:max((float(np.linalg.norm(v[:3]))/.0025 for (t,name),v in forces.items() if name==n),default=0.) for n in ('skin','guide','support','other')}
 d=dict(status='ACTUAL_GEOMETRY_RESPONSE_CROSSCHECK_ONLY',case=a.case,records=records,actual_nonzero_skin_response_outputs=active,maximum_object_force_by_source_N=maxima,scope='ActualsavedSkintriangle closestpoints andsource-resolvedNativeJlambda;negativephysicalgap signalspenetration. NoShellthickness/truearea/pressure/CCD/timeaccuracyclaim. Zeroresponse mustNOTbeinterpreted ascorrectifphysicalgeometryintersects.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
