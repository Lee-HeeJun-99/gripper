"""Matched tiny-load Native coupons retaining actual Guide/Rail mappings.

No cable,object,contact,gravity. Not equilibrium or B3 grasp qualification.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from b3_contact_layer_native import flat,add
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cases=['b3_railback_grasp1001298','proximal_reinforcement_mid1370'];records=[];guidegraphs=[]
 for label,case in zip(('baseline','reinforced'),cases):
  src=BASE/'results'/case;folder=out/label;folder.mkdir();root=ET.parse(src/'scene.scn').getroot();root.set('gravity','0 0 0');allowed={'RequiredPlugin','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'}
  for n in list(root):
   if n.tag=='Node':
    if n.get('name') not in ('guides0','free0','finger0','layerFree0','contactLayer0'):root.remove(n)
   elif n.tag not in allowed:root.remove(n)
  root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
  for parent in root.iter():
   for n in list(parent):
    if n.tag in ('CableConstraint','NativeCableSequence') or n.tag.endswith('CollisionModel') or (n.tag=='Node' and n.get('name') in ('skinCollision','railCollision','exterior')) or n.tag.startswith('Native'):parent.remove(n)
  guidegraphs.append(ET.tostring(root.find("Node[@name='guides0']")))
  finger=root.find("Node[@name='finger0']");q=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);tip=np.flatnonzero((local[:,0]==100)&(local[:,2]==.1));F=np.tile([-1e-5/len(tip),0,0],(len(tip),1));add(finger,'ConstantForceField',indices=' '.join(map(str,tip)),forces=flat(F));add(finger,'NativePointJournal',body='@dofs',filename=folder/'states.csv');add(root.find("Node[@name='guides0']"),'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass=1,filename=folder/'guides.csv')
  for n in root.iter('TetrahedronFEMForceField'):n.set('method','small')
  ET.ElementTree(root).write(folder/'scene.scn');cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','20','--hideProgressBar',str(folder/'scene.scn')];pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(folder/'scene.scn'),total_force_N=1e-5,dt_s=.0025,duration_s=.05,forecast_s=5,child_limit_s=30,memory_GiB=4,scope='Same originalGuide/Rail mapping and same Rayleigh in both;linearFEM,zero gravity/noCable/noContact. Not Native equilibrium stiffness ratio.');(folder/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,folder/'process',30);rows=list(csv.DictReader((folder/'states.csv').open())) if (folder/'states.csv').exists() else [];log=''.join((folder/'process'/f).read_text() for f in ('stdout.log','stderr.log'));tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);det0=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));ratios=[];history=[]
  for r in rows:
   qa=np.fromstring(r['q'],sep=' ').reshape(-1,3);ratios.append(float((np.linalg.det((qa[tet[:,1:]]-qa[tet[:,0,None]]).transpose(0,2,1))/det0).min()));history.append(dict(time_s=float(r['time_s']),width_mean_tip_x_displacement_m=float((qa-q)[tip,0].mean())))
  records.append(dict(name=label,process=proc,outputs=len(rows),status='BOUNDED_MAPPED_COUPON_ONLY' if proc['exit_code']==0 and '[ERROR]'not in log and len(rows)==20 and min(ratios,default=-1)>0 else 'FAIL_NATIVE_COUPON',minimum_core_saved_volume_ratio=min(ratios,default=None),tip_history=history))
 assert guidegraphs[0]==guidegraphs[1];d=dict(status='COMPLETED_MATCHED_GUIDE_MAPPING_COUPONS' if all(r['status'].startswith('BOUNDED') for r in records) else 'FAIL_MAPPED_COUPON',originalGuideGraphEqual=True,records=records,scope='Actual transient,not settledload-displacement or static stiffness ratio. Coreelementquality only;newlayerenergy/strain NOTMEASURED. No convergence or graspPASS.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
