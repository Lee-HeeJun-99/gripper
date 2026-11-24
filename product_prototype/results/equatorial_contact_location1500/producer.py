"""Locate actual Detector points relative to saved accepted Skin triangles.
Detector/free geometry and accepted geometry may differ:report gap,not identity.
No contact-row force assignment or contact area inferred from these samples.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);results=[]
 for case in a.cases:
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);states={};faces={};records=[]
  for i in range(3):
   states[i]={float(r['time_s']):np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in read(src/f'finger{i}.csv') if .5-1e-12<=float(r['time_s'])<=.6+1e-12};n=root.find(f"Node[@name='finger{i}']/Node[@name='skinCollision']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces[i]=ids[np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)]
  with (src/'detector.csv').open() as stream:
   for row in csv.DictReader(stream):
    time=float(row['accepted_time_s']);paths=[row['model0'],row['model1']]
    if not (.5-1e-12<=time<=.6+1e-12 and any('/object/'in x for x in paths) and any('/skinCollision/'in x for x in paths)):continue
    side=0 if '/skinCollision/'in paths[0] else 1;i=next(i for i in range(3) if f'/finger{i}/'in paths[side]);point=np.fromstring(row[f'detected_point{side}'],sep=' ');tri=states[i][time][faces[i]];closest=trimesh.triangles.closest_point(tri,np.repeat(point[None],len(tri),axis=0));dist=np.linalg.norm(closest-point,axis=1);k=int(dist.argmin());bary=trimesh.triangles.points_to_barycentric(tri[k:k+1],closest[k:k+1])[0];material=float(bary@local[faces[i][k],0]);records.append(dict(time_s=time,finger=i,model=paths[side],nearest_accepted_material_x_mm=material,detector_to_accepted_surface_mm=float(dist[k]*1000)))
  assert records;xs=np.array([r['nearest_accepted_material_x_mm'] for r in records]);gaps=np.array([r['detector_to_accepted_surface_mm'] for r in records]);results.append(dict(case=case,samples=len(records),material_x_min_p10_median_p90_max_mm=np.percentile(xs,[0,10,50,90,100]).tolist(),maximum_detector_to_accepted_surface_gap_mm=float(gaps.max()),samples_x_below70mm=int((xs<70).sum()),scope='Sample inventory only,not area or force-bearing fraction. Different Detector/accepted stages explicitly nonzero gap;no claim exactmaterialcontacttrajectory.',input_hashes={f:sha(src/f) for f in ('scene.scn','mesh.json','detector.csv','finger0.csv','finger1.csv','finger2.csv')}));(out/(case+'_samples.json')).write_text(json.dumps(records,indent=2))
 d=dict(status='DETECTOR_TO_ACCEPTED_GEOMETRY_INVENTORY_ONLY',records=results,source_sha256=sha(Path(__file__)),scope='No response-row/Detector-index equivalence assumed,no pressure or force assigned to nearesttriangle');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
