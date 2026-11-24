"""Cylinder support-plane lower bound using actual Guide poses;not fullhardware."""
import argparse,csv,json,itertools,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from mechanism_candidates import world,width,guide_outboard,guide_normal
def read(p):return list(csv.DictReader(p.open()))
def cylinder_support(projection,ro,half):
 projection=np.clip(abs(projection),0,1)
 return half*projection+ro*np.sqrt(1-projection*projection)
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();cfg=json.loads((src/'config.json').read_text());ro=cfg['tendon']['guide_outer_radius']*.001;half=cfg['tendon'].get('guide_length_mm',2.)*.0005;buffer=cfg['simulation']['contact_distance_mm']*.001;groups=[];hashes={}
 for i,angle in enumerate((0,120,240)):
  film=read(src/f'finger{i}.csv');frames=read(src/f'guide_frames{i}.csv');times=np.array([float(r['time_s']) for r in film]);assert [float(r['time_s']) for r in frames]==times.tolist();rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);initial=np.fromstring(root.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  for j,side in enumerate((-1,1)):
   node=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");owners=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);q=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in film]);axes=[]
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    local=np.array([x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)]);h=np.array([.001,0,0]);axis=np.array(world(cfg,local+h,angle))-world(cfg,local-h,angle);axis/=np.linalg.norm(axis);body=Rotation.from_quat(initial[owners[k],3:]).inv().apply(axis);axes.append(Rotation.from_quat(rigid[:,owners[k],3:]).apply(np.repeat(body[None],len(times),axis=0)))
   groups.append(dict(finger=i,cable=j,q=q,axis=np.stack(axes,axis=1),radius=float(node.find('SphereCollisionModel').get('radius'))))
  for file in (f'finger{i}.csv',f'guide_frames{i}.csv'):hashes[file]=sha(src/file)
 allmin=1e9;nearmin=1e9;count=0;nearcount=0;worst=None
 for g,b in itertools.combinations(groups,2):
  if g['finger']==b['finger']:continue
  d=b['q'][:,None]-g['q'][:,:,None];distance=np.linalg.norm(d,axis=3);n=d/distance[:,:,:,None];support0=cylinder_support(np.sum(n*g['axis'][:,:,None],axis=3),ro,half);support1=cylinder_support(np.sum(n*b['axis'][:,None],axis=3),ro,half);bound=distance-support0-support1;allmin=min(allmin,float(bound.min()));spheregap=distance-g['radius']-b['radius'];near=spheregap<=buffer;count+=int(near.sum());nearcount+=int((near&(bound>buffer)).sum())
  if near.any() and bound[near].min()<nearmin:
   nearmin=float(bound[near].min());idx=np.unravel_index(np.where(near,bound,np.inf).argmin(),bound.shape);worst=dict(time_s=float(times[idx[0]]),finger0=g['finger'],cable0=g['cable'],guide0=int(idx[1]),finger1=b['finger'],cable1=b['cable'],guide1=int(idx[2]),spheregap_mm=float(spheregap[idx]*1000),cylinder_support_plane_gap_lower_bound_mm=nearmin*1000)
 d=dict(status='SAVED_CYLINDER_SUPPORT_PLANE_BOUND_ONLY',case=a.case,minimum_all_pair_lower_bound_mm=allmin*1000,near_proxy_pair_samples=count,near_proxy_samples_with_cylinder_bound_above_contact_buffer=nearcount,minimum_near_proxy_cylinder_lower_bound_mm=None if count==0 else nearmin*1000,worst_near_proxy=worst,outer_radius_mm=ro*1000,length_mm=half*2000,contact_buffer_mm=buffer*1000,scope='Finiteclosedcylinder supportfunction gives separatingplane lowerbound whenpositive. AnnularEyeletsubset inheritsbound. Manufacturedaxis=fingerreference tangent underactualRigidMapping,explicitorientationassumption. ActualsavedposesONLY,notnewdynamics/wholeSupport/CAD/CCD/materialqualification. Proxyforce may beconservativegeometry;supportsolidmustbecheckedseparately. NoSpherecollisiondisabled.',source_sha256=sha(Path(__file__)),input_hashes=hashes);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
