"""Link measured contact J to signed solid, not unsigned point separation."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from current_turn_wire_assess import polygon_ring_distance
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/identified_contact_phase1626';target=.0452;rr=read(src/'response_rows.csv');owner=next(r for r in rr if abs(float(r['time_s'])-target)<1e-12 and int(r['row_id'])==34);children=[]
 for r in read(src/'probe.children.csv'):
  side=int(r['side']);prefix=owner['model'+str(side)].rsplit('/',1)[0]+'/'
  if r['phase']=='accepted_end' and abs(float(r['time_s'])-target)<1e-12 and int(r['row'])==34 and r['constraint']==owner['constraint_path'] and r['state'].startswith(prefix):children.append(r)
 assert len(children)==2;children.sort(key=lambda r:int(r['side']));q0,q1=[np.fromstring(r['q'],sep=' ') for r in children];j0,j1=[np.fromstring(r['J'],sep=' ') for r in children];surface=read(src/'surface.csv');previous=np.fromstring(surface[-2]['q'],sep=' ').reshape(-1,3)[328];actual=np.fromstring(surface[-1]['q'],sep=' ').reshape(-1,3)[328];assert np.array_equal(q1,actual);separation=previous-q0;n=separation/np.linalg.norm(separation);normal_error=float(abs(n-j1).max());assert normal_error<=1e-12
 # A bore face solid-outward normal points INTO the hole. Its polygon support
 # plane is known independently of contact J and of the wire displacement.
 theta=(np.arange(32)+.5)*2*np.pi/32;normals=np.column_stack([np.cos(theta),np.sin(theta)]);face=int(np.argmax((q0-[.01,0,0])[1:]@normals.T));outward=np.r_[0,-normals[face]];plane_error=abs(float(q0[1:]@normals[face])-.0006*np.cos(np.pi/32));assert plane_error<=1e-12
 physical=float(polygon_ring_distance((actual-[.01,0,0])[None])[0]);halfspace=float(j0@q0+j1@q1-.000002)
 records=[]
 for r in read(BASE/'results/wire_contact_policy1616/detector.csv'):
  if r['model0']!='/finiteEyelet/TriangleCollisionModel1' or r['model1']!='/wire/wireSurface/PointCollisionModel1':continue
  a0=np.fromstring(r['detected_point0'],sep=' ')-[.01,0,0];a1=np.fromstring(r['detected_point1'],sep=' ')-[.01,0,0]
  if abs(a0[0])>=.001 or np.linalg.norm(a0[1:])>=.0007:continue
  k=int(np.argmax(a0[1:]@normals.T));err=abs(a0[1:]@normals[k]-.0006*np.cos(np.pi/32))
  delta=a1-a0;length=np.linalg.norm(delta)
  if err>1e-12 or length==0:continue
  signed=float(polygon_ring_distance(a1[None])[0]);dot=float(delta/length@np.r_[0,-normals[k]]);records.append(dict(accepted_time_s=float(r['accepted_time_s']),previous_point_solid_gap_m=signed,normal_dot_solid_outward=dot))
 inside=[r for r in records if r['previous_point_solid_gap_m']<0];outside=[r for r in records if r['previous_point_solid_gap_m']>0]
 d=dict(status='FAIL_CONTACT_HALFSPACE_SOLID_SIDEDNESS_AT_MEASURED_STEP',target_time_s=target,row=34,multiplier_Ns=float(owner['lambda_Ns']),wire_vertex=328,actual_surface_vs_child_error_m=float(abs(actual-q1).max()),measured_J_vs_previous_point_separation_error=normal_error,actual_face_plane_error_m=float(plane_error),normal_dot_solid_outward=float(j1@outward),previous_vertex_solid_gap_m=float(polygon_ring_distance((previous-[.01,0,0])[None])[0]),accepted_vertex_solid_gap_m=physical,Native_accepted_frozen_halfspace_gap_m=halfspace,contact_distance_m=.000002,inner_triangle_point_records=len(records),inside_previous_point_records=len(inside),inside_records_with_inward_geometric_separation=sum(r['normal_dot_solid_outward']<0 for r in inside),outside_previous_point_records=len(outside),outside_records_with_outward_geometric_separation=sum(r['normal_dot_solid_outward']>0 for r in outside),scope='Actual measured J at row34 equals previous-point separation,not solid orientation. After crossing wall Native distance-halfspace is positive while signedsolidgap is negative;lambda0 is consistent with that halfspace,NOTa valid solid contact. Temporal inventory uses actual detector point pairs;does NOT infer unobserved native J or multipliers at othersteps. Not solecause of initialcrossing,solverfix,CCD orwholegrasp.',source_sha256=sha(Path(__file__)),input_sha256={f:sha(src/f) for f in ('surface.csv','probe.children.csv','response_rows.csv')},detector_sha256=sha(BASE/'results/wire_contact_policy1616/detector.csv'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'temporal_inventory.json').write_text(json.dumps(records));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
