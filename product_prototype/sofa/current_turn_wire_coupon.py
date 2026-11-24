"""Actual elastic bending through finite bore at current guide3 turn.
Only endpoint fixtures move;initial beam is straight and stress-free.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from finite_guide_coupon import eyelet
from native_bending_coupon import guarded
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_eyelet_audit1436';turn=json.loads((BASE/'results/bore_axis_feasibility1612/summary.json').read_text());angle=max(g['maximum_actual_path_turn_deg'] for g in turn['records'][0]['groups'] if g['guide']==3);beta=np.radians(angle/2);dt=.0001;ramp=.08;duration=.12;steps=round(duration/dt);cfg=json.loads((BASE/'results/dispatch_finite_holding1586/config.json').read_text());ring,geometry=eyelet(cfg,32);records=[]
 for guide in (False,True):
  d=out/('guide' if guide else 'no_guide_control');d.mkdir();root=ET.parse(src/'scene.scn').getroot();wire=root.find("Node[@name='wire']")
  for n in list(wire):
   if n.tag in ('ConstantForceField','FixedProjectiveConstraint','PartialFixedProjectiveConstraint'):wire.remove(n)
  for idx,side in ((0,-1),(10,1)):
   movement=np.array([side*.01*(np.cos(beta)-1),.01*np.sin(beta),0,0,0,side*beta]);ET.SubElement(wire,'LinearMovementProjectiveConstraint',indices=str(idx),keyTimes=flat([-dt,ramp-dt,10]),movements=flat([np.zeros(6),movement,movement]))
  old=root.find("Node[@name='finiteEyelet']");root.remove(old)
  if guide:
   eye=ET.SubElement(root,'Node',name='finiteEyelet');v=ring.vertices*.001+[.01,0,0];ET.SubElement(eye,'MeshTopology',position=flat(v),triangles=flat(ring.faces));ET.SubElement(eye,'MechanicalObject',position=flat(v))
   for kind in ('Triangle','Line','Point'):ET.SubElement(eye,kind+'CollisionModel',moving='0',simulated='0',group='2')
  for n in root.iter():
   for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(d)))
  ET.ElementTree(root).write(d/'scene.scn');pre=dict(source_scene_sha256=sha(src/'scene.scn'),source_sha256=sha(Path(__file__)),scene_sha256=sha(d/'scene.scn'),target_turn_deg=angle,beta_rad=float(beta),duration_s=duration,ramp_s=ramp,dt_s=dt,initial_reference='Straight20mm nativeBeamAdapter,zeroinitialstress peroriginalnativebeamrestgeometry',material='InheritedE2GPa/rho1000researchassumptions,NOTactualwirematerial',guide_geometry=geometry,mechanical_change='ONLYtwoendpointprojectivefixtures move;interior DOFs not prescribed. NoGuide variant is isolated elasticcontrol ONLY.',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},runSofa_sha256=sha(Path('/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00')),memory_GiB=4,child_limit_s=120);(d/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(d/'scene.scn')],d/'process',120);rows=read(d/'states.csv') if (d/'states.csv').exists() else [];logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));q0=np.fromstring(wire.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);poserr=orierr=0.;finite=True;maxstrain=0.;interior=0.;contact=0
  for r in rows:
   t=float(r['time_s']);q=np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7);v=np.fromstring(r['rigid_v'],sep=' ');finite=finite and bool(np.isfinite(q).all() and np.isfinite(v).all());scale=min(1,t/ramp)
   for idx,side in ((0,-1),(10,1)):
    delta=np.array([side*.01*(np.cos(beta)-1),.01*np.sin(beta),0])*scale;poserr=max(poserr,float(abs(q[idx,:3]-q0[idx,:3]-delta).max()));expected=Rotation.from_rotvec([0,0,side*beta*scale]);orierr=max(orierr,float(abs(Rotation.from_quat(q[idx,3:]).as_matrix()-expected.as_matrix()).max()))
   maxstrain=max(maxstrain,float(abs(np.linalg.norm(np.diff(q[:,:3],axis=0),axis=1)/.002-1).max()));interior=max(interior,float(np.linalg.norm(q[1:-1,:3]-q0[1:-1,:3],axis=1).max()));contact+=int(np.linalg.norm(np.fromstring(r['object_impulse_Ns_Nms'],sep=' '))>0)
  ok=proc['exit_code']==0 and '[ERROR]'not in logs and len(rows)==steps and finite;records.append(dict(guide=guide,status='ACTUAL_COUPON_COMPLETED_NOT_QUALIFIED' if ok else 'FAIL_NATIVE_COUPON',process=proc,outputs=len(rows),finite=finite,maximum_endpoint_position_error_m=poserr,maximum_endpoint_orientation_matrix_error=orierr,maximum_interior_displacement_m=interior,maximum_segment_chord_strain_proxy=maxstrain,nonzero_contact_impulse_outputs=contact,scope='Chordstrain isNOTBeamAdaptermaterialstrain;reaction/supportwork/beamenergy notmeasured. FixtureAPI,finite-surfacegap andresponseprovenance need independentassessment. Notwholegrasp/material/time/meshPASS.'))
 d=dict(status='CURRENT_TURN_WIRE_COUPONS_EXECUTED',records=records,source_sha256=sha(Path(__file__)),source_turn_summary_sha256=sha(BASE/'results/bore_axis_feasibility1612/summary.json'),physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
