"""Actual saved facet angles and previous/current detector-point geometry audit."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();state={};facets={};angle=[]
 for i in range(3):
  node=root.find(f"Node[@name='finger{i}']/Node[@name='skinCollision']");ids=np.fromstring(node.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);initial=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);rows=read(src/f'finger{i}.csv');previous=initial;minimum=1.
  for r in rows:
   current=np.fromstring(r['q_m'],sep=' ').reshape(-1,3)[ids];state[i,float(r['time_s'])]=(previous,current);previous=current
   for vertices in (current,):
    tri=vertices[faces];AB=tri[:,1]-tri[:,0];AC=tri[:,2]-tri[:,0];minimum=min(minimum,float((np.sum(AB*AC,axis=1)/(np.linalg.norm(AB,axis=1)*np.linalg.norm(AC,axis=1))).min()))
  angle.append(dict(finger=i,minimum_saved_start_angle_cosine=minimum,start_angle_stayed_acute=minimum>0));facets[i]=faces
 points=[]
 with (src/'detector.csv').open() as stream:
  for r in csv.DictReader(stream):
   names=[r['model0'],r['model1']]
   if not any('/object/'in n for n in names):continue
   side=next((k for k,n in enumerate(names) if '/skinCollision/TriangleCollisionModel'in n),None)
   if side is None:continue
   i=int(names[side].split('/')[1].removeprefix('finger'));t=float(r['accepted_time_s']);point=np.fromstring(r[f'detected_point{side}'],sep=' ');dist=[]
   for vertices in state[i,t]:
    tri=vertices[facets[i]];nearest=trimesh.triangles.closest_point(tri,np.repeat(point[None],len(tri),axis=0));dist.append(float(np.linalg.norm(nearest-point,axis=1).min()))
   points.append(dict(time_s=t,finger=i,previous_accepted_surface_distance_m=dist[0],current_accepted_surface_distance_m=dist[1]))
 (out/'point_distances.json').write_text(json.dumps(points));d=dict(status='ACTUAL_SAVED_CYCLIC_SURFACE_AUDIT_ONLY',case=a.case,angles=angle,actual_triangle_detector_points=len(points),maximum_previous_accepted_surface_distance_m=max((r['previous_accepted_surface_distance_m'] for r in points),default=None),maximum_current_accepted_surface_distance_m=max((r['current_accepted_surface_distance_m'] for r in points),default=None),previous_surface_api_1e12_pass=bool(points) and all(r['previous_accepted_surface_distance_m']<=1e-12 for r in points),scope='BothpreviousandcurrentacceptedstatesREPORTEDSEPARATELY,notcherry-pickedminimum. ActualdetectorTrianglepointsdistance toactualSkinfacetset;noNativefeaturetriangleIDsassumed,notSpherepointinterpretation/contactarea/CCD/globalenergy/timeconvergence. Savedacuteanglesdiagnosebranchorderingonly.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','detector.csv','finger0.csv','finger1.csv','finger2.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
