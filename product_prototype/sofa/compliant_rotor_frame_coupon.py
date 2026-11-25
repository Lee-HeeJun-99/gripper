"""Whole-frame objectivity test of completed static compliant rotor, not new dynamics."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat

def read(path,key,width):
 return [np.fromstring(row[key],sep=' ').reshape(-1,width) for row in csv.DictReader(path.open())]

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 records=[]
 # One physical vertical placement plus a generic non-axis-aligned placement.
 for name,rotation in [('vertical',Rotation.from_euler('y',-90,degrees=True)),('oblique',Rotation.from_euler('xyz',[31,-47,23],degrees=True))]:
  folder=out/name;folder.mkdir();src=BASE/'results/compliant_rotor1855/n9/scene.scn';root=ET.parse(src).getroot()
  for e in root.iter():
   if e.tag in ('MechanicalObject','MeshTopology') and 'position'in e.attrib:
    if e.get('template')=='Rigid3d':
     q=np.fromstring(e.get('position'),sep=' ').reshape(-1,7);q[:,:3]=rotation.apply(q[:,:3]);q[:,3:]=(rotation*Rotation.from_quat(q[:,3:])).as_quat();e.set('position',flat(q))
    else:e.set('position',flat(rotation.apply(np.fromstring(e.get('position'),sep=' ').reshape(-1,3))))
   if e.tag=='ConstantForceField':e.set('forces',flat(rotation.apply(np.fromstring(e.get('forces'),sep=' ').reshape(-1,3))))
   if e.tag=='NativeRigidJournal':e.set('filename',str(folder/'states.csv'))
   if e.tag=='NativePointJournal':e.set('filename',str(folder/'ports.csv'))
  ET.ElementTree(root).write(folder/'scene.scn')
  process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','3','--hideProgressBar',folder/'scene.scn'],folder/'process',60)
  logs=''.join((folder/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));rec=dict(placement=name,process=process,status='FAIL_FRAME_NATIVE',scene_sha256=sha(folder/'scene.scn'),reference_scene_sha256=sha(src),errors=[s for s in logs.splitlines() if '[ERROR]'in s])
  if process['exit_code']==0 and '[ERROR]'not in logs:
   qs=read(folder/'states.csv','rigid_q',7);refs=read(src.parent/'states.csv','rigid_q',7);ps=read(folder/'ports.csv','q',3);prefs=read(src.parent/'ports.csv','q',3);assert len(qs)==len(refs)==len(ps)==len(prefs)==3
   poserr=roterr=porterr=0.
   for q,ref,ports,pref in zip(qs,refs,ps,prefs):
    poserr=max(poserr,float(abs(rotation.inv().apply(q[:,:3])-ref[:,:3]).max()))
    roterr=max(roterr,float((Rotation.from_quat(ref[:,3:]).inv()*rotation.inv()*Rotation.from_quat(q[:,3:])).magnitude().max()))
    porterr=max(porterr,float(abs(rotation.inv().apply(ports)-pref).max()))
   rec.update(status='PASS_WHOLE_FRAME_STATIC_OBJECTIVITY_ONLY' if max(poserr,roterr,porterr)<=1e-12 else 'FAIL_FRAME_RESPONSE',maximum_position_difference_m=poserr,maximum_orientation_difference_rad=roterr,maximum_port_difference_m=porterr)
  records.append(rec)
 d=dict(status='PASS_STATIC_PLACEMENT_CONTRACT' if all(r['status']=='PASS_WHOLE_FRAME_STATIC_OBJECTIVITY_ONLY' for r in records) else 'FAIL_STATIC_PLACEMENT',records=records,source_sha256=sha(Path(__file__)),criteria='All three actual saved states back-rotated to1855; translation/port<=1e-12m, relative orientation<=1e-12rad. No fitted correction or tolerance floor.',scope='Actual whole-frame Native static BeamFEM and RigidMapping placement only. Same physical geometry, material, loads, full-root boundary and solver. No CableConstraint/dynamic mass, physical shaft fatigue/retention, wire routing or100g Holding qualification.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
