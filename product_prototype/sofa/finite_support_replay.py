"""Proposed support hulls on actual saved B3 transforms;NOT candidate dynamics."""
import argparse,csv,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha,rotation
sys.path.insert(0,str(BASE/'cad'))
from finite_guide_product import support
from closest_geometry import closest
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_alarm_window485';cfg=json.loads((src/'config.json').read_text());cad=BASE/'meshes/finite_eyelet_support_v11';native=json.loads((BASE/'results/b3_finite_local64_542/summary.json').read_text());design=json.loads((cad/'geometry.json').read_text());config_match=sha(src/'config.json')==sha(cad/'config.json')==native['source_config_sha256'];assert config_match;tree=ET.parse(src/'scene.scn');objects=read(src/'object.csv');time=np.array([float(r['time_s']) for r in objects]);centres=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in objects]);R=cfg['simulation']['sphere_radius_mm']*.001;records=[];identity=0.;inputs={str((src/'object.csv').relative_to(BASE.parent)):sha(src/'object.csv')}
 for i,(finger,cable,k) in enumerate(((1,0,5),(2,1,5))):
  ref=next(g for g in design['guides'] if g['finger']==finger and g['cable']==cable and g['station_mm']==98);identity=max(identity,float(np.max(abs(np.array(ref['center_mm'])-native['models'][i]['manufactured_center_mm']))*.001),float(np.max(abs(np.array(ref['basis'])-native['models'][i]['manufactured_basis']))))
 for finger,angle in enumerate(cfg['palm']['angles_deg']):
  frames=read(src/f'guide_frames{finger}.csv');assert np.array_equal(time,np.array([float(r['time_s']) for r in frames]));q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);qrest=np.fromstring(tree.find(f"./Node[@name='guides{finger}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);inputs[str((src/f'guide_frames{finger}.csv').relative_to(BASE.parent))]=sha(src/f'guide_frames{finger}.csv')
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    index=cable*6+k;hull=support(cfg,x,side,angle);local=(hull.vertices*.001-qrest[index,:3])@rotation(qrest[index,3:]);rot=np.array([rotation(v[index,3:]) for v in q]);# Transform sphere into the fixed body-local support frame,avoiding large repeated mesh transforms.
    bodycentres=np.einsum('nij,ni->nj',rot,centres-q[:,index,:3]);tri=local[hull.faces];points=np.repeat(bodycentres,len(tri),axis=0);near=closest(np.tile(tri,(len(time),1,1)),points).reshape(len(time),len(tri),3);distance=np.linalg.norm(near-bodycentres[:,None,:],axis=2).min(axis=1)
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normals/=np.linalg.norm(normals,axis=1)[:,None];inside=np.all(np.einsum('nfi,fi->nf',bodycentres[:,None,:]-tri[None,:,0],normals)<=0,axis=1);signed=np.where(inside,-distance,distance)-R;idx=int(np.argmin(signed));hold=(time>=1.6)&(time<=2);records.append(dict(finger=finger,cable=cable,station_mm=x,minimum_support_sphere_gap_mm=float(signed[idx]*1000),worst_time_s=float(time[idx]),negative_saved_frames=int(np.count_nonzero(signed<0)),hold_minimum_gap_mm=float(signed[hold].min()*1000),support_mass_kg=None))
 result=dict(status='FROZEN_MOTION_SUPPORT_SCREEN_NOT_DYNAMIC_RESULT',scope='NEW proposed support solids replayed on ACTUAL OLD Native485 transforms. This is not a SOFA run of supports;changed hardware mass/contact can change motion. Negative margins reject replayed clearance,not prove new dynamic penetration. Eyelet-support joint/Boolean/strength/interfinger/wire not certified.',source_sha256=sha(Path(__file__)),same_config=config_match,two_actual_native_CAD_center_and_basis_max_error=identity,inputs=inputs,source_CAD_sha256=sha(cad/'geometry.json'),actual_saved_frames=len(time),minimum_gap_mm=min(r['minimum_support_sphere_gap_mm'] for r in records),minimum_hold_gap_mm=min(r['hold_minimum_gap_mm'] for r in records),records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('records','inputs')},indent=2))
if __name__=='__main__':main()
