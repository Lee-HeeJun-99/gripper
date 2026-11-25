"""Separate finite planar bellcrank/rod/slider candidate, CAD millimetres."""
import argparse,json,sys,itertools,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.optimize import brentq
from scipy.spatial.transform import Rotation
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from analyse import sha
from finite_csg64 import register

def cylinder(r,h,centre):
 m=trimesh.creation.cylinder(radius=r,height=h,sections=32);m.apply_translation(centre);return m
def shapes():
 rotor=trimesh.creation.box([24,2,1]);rotor=trimesh.boolean.difference([rotor,*[cylinder(.3,1.2,[x,0,0]) for x in (-10,0,10)]],engine='manifold64')
 rod=trimesh.creation.box([1,32,1]);rod=trimesh.boolean.difference([rod,*[cylinder(.3,1.2,[0,y,0]) for y in (-15,15)]],engine='manifold64')
 slider=trimesh.boolean.difference([trimesh.creation.box([4,4,1]),cylinder(.3,1.2,[0,0,0])],engine='manifold64')
 return rotor,rod,slider
def pose(theta):
 R=Rotation.from_rotvec([0,0,theta]).as_matrix();point=R@np.array([-10.,0,0]);dx=-10-point[0];y=point[1]+np.sqrt(30**2-dx**2);end=np.array([-10.,y,2.]);start=point+np.array([0,0,2.]);phi=np.arctan2(-dx,y-point[1]);return R,start,end,phi
def moved(mesh,position,R=None):
 m=mesh.copy();T=np.eye(4);T[:3,3]=position
 if R is not None:T[:3,:3]=R
 m.apply_transform(T);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register();rotor,rod,slider=shapes();goal=brentq(lambda t:pose(t)[2][1]-34.,-.6,0);records=[];hits=[];wirehits=[];components={};initial=None
 for k,theta in enumerate(np.linspace(0,goal,21)):
  R,start,end,phi=pose(theta);inputpoint=R@np.array([10.,0,-1.5]);parts=dict(rotor=moved(rotor,[0,0,0],R),rod=moved(rod,(start+end)/2,Rotation.from_rotvec([0,0,phi]).as_matrix()),slider=moved(slider,end+[0,0,2]),pivot_pin=cylinder(.25,2,[0,0,0]),input_anchor_pin=cylinder(.25,2.5,inputpoint+[0,0,.75]),output_pin=cylinder(.25,3,start+[0,0,-1]),slider_pin=cylinder(.25,3,end+[0,0,1]))
  for name,m in parts.items():
   assert m.is_volume and len(m.split(only_watertight=False))==1
   if k==0:
    m.export(out/f'{name}_rest_mm.stl');components[name]=dict(volume_mm3=float(m.volume),COM_mm=m.center_mass.tolist(),unit_density_inertia_mm5=m.moment_inertia.tolist())
  for left,right in itertools.combinations(parts,2):
   x,y=parts[left],parts[right]
   if np.any(x.bounds[1]<y.bounds[0]) or np.any(y.bounds[1]<x.bounds[0]):continue
   value=trimesh.boolean.intersection([x,y],engine='manifold64');volume=float(value.volume) if len(value.faces) else 0.;assert volume>=0
   if volume>0:hits.append(dict(sample=k,pair=[left,right],intersection_mm3=volume))
  pull=np.array([10.,-20.,-1.5]);direction=inputpoint-pull;trim=inputpoint-.7*direction/np.linalg.norm(direction);wire=trimesh.creation.cylinder(radius=.25,segment=np.stack([pull,trim]),sections=32);assert wire.is_volume
  for name,part in parts.items():
   value=trimesh.boolean.intersection([wire,part],engine='manifold64');volume=float(value.volume) if len(value.faces) else 0.;assert volume>=0
   if volume>0:wirehits.append(dict(sample=k,part=name,intersection_mm3=volume))
  if k==0:wire.export(out/'wire_before_declared_termination_domain_mm.stl');initial={n:dict(position_mm=m.center_mass.tolist()) for n,m in parts.items()}
  records.append(dict(sample=k,theta_rad=float(theta),rod_phi_rad=float(phi),rod_endpoint0_mm=start.tolist(),rod_endpoint1_mm=end.tolist(),rod_COM_mm=((start+end)/2).tolist(),slider_COM_mm=(end+[0,0,2]).tolist(),closure_error_mm=abs(float(np.linalg.norm(end-start))-30.),output_stroke_mm=float(end[1]-30),input_cable_length_mm=float(np.linalg.norm(inputpoint-pull))))
 d=dict(status='PASS_SAMPLED_FINITE_LINK_GEOMETRY_ONLY' if not hits and not wirehits else 'REJECTED_LINK_GEOMETRY',samples=21,parts=7,goal_output_stroke_mm=4.,maximum_angle_rad=float(abs(goal)),maximum_loop_closure_error_mm=max(r['closure_error_mm'] for r in records),solid_intersections=hits,wire_intersections_before_termination_domain=wirehits,components=components,poses=records,configuration=dict(rotor_mm=[24,2,1],rod_mm=[1,32,1],rod_pin_distance_mm=30,slider_mm=[4,4,1],pin_radius_mm=.25,bore_radius_mm=.3,wire_radius_mm=.25,rod_plane_z_mm=2,slider_plane_z_mm=4,wire_termination_domain_mm=.7),source_sha256=sha(Path(__file__)),scope='NEW three-bore rotor + rigid connecting rod + prismatic slider geometry, different mass from1841one-bore port. Millimetre indexed CSG only; explicit SI conversion required for Native. Sampled21poses not swept proof. Termination last0.7mm declared unqualified connector domain, not a fabricated wire clamp. Pins unretained, housing/bearings/tooling/Finger interface absent. Radial50um clearance incompatible with inherited200um contact buffer if bearing contact used; ideal joint must be independently declared, not broad contact disable. No Native/Finger/grasp/material/strength/STEP PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k not in ('poses','components')},indent=2))
if __name__=='__main__':main()
