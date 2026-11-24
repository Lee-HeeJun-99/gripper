"""Stock indexed UniformMass: separate inertia per rigid DOF without DiagonalMass.
Actual forced acceleration tests assembly, not first-component BaseMass queries.
"""
import argparse,csv,copy,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 src=BASE/'results/capillary_hold1700';old=ET.parse(src/'scene.scn').getroot();root=ET.Element('Node',dt='.001',gravity='0 0 0')
 for n in old:
  if n.tag in ('RequiredPlugin','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):root.append(copy.deepcopy(n))
 ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad')
 node=ET.SubElement(root,'Node',name='body');ET.SubElement(node,'MechanicalObject',template='Rigid3d',name='frames',position='0 0 0 0 0 0 1  .02 0 0 0 0 0 1')
 masses=[1e-5,3e-5];normalized=[1e-6,2e-6]
 for i,(m,I) in enumerate(zip(masses,normalized)):ET.SubElement(node,'UniformMass',template='Rigid3d',name=f'mass{i}',indices=str(i),vertexMass=f'{m} 1e-8 {I} 0 0 0 {I} 0 0 0 {I}')
 ET.SubElement(node,'ConstantForceField',template='Rigid3d',indices='0 1',forces='1e-4 0 0 0 1e-8 0   1e-4 0 0 0 1e-8 0')
 ET.SubElement(node,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(out/'body.csv'))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),masses_kg=masses,normalized_inertia_m2=normalized,force_N=1e-4,torque_Nm=1e-8,dt_s=.001,steps=4,SDK='/home/ubuntu/SOFA/v26.06.00',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2))
 process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',out/'scene.scn'],out/'process',60)
 logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));err=None;records=[]
 if process['exit_code']==0 and '[ERROR]' not in logs:
  for r in csv.DictReader((out/'body.csv').open()):
   t=float(r['time_s']);v=np.fromstring(r['rigid_v'],sep=' ').reshape(-1,6);expected=np.zeros((2,6));expected[:,0]=1e-4*t/np.array(masses);expected[:,4]=1e-8*t/(np.array(masses)*normalized);records.append(float(abs(v-expected).max()))
  err=max(records) if len(records)==4 else None
 d=dict(status='PASS_INDEXED_NATIVE_MASS_TRANSLATION_ROTATION_ONLY' if err is not None and err<=1e-12 else 'FAIL_INDEXED_NATIVE_MASS',maximum_velocity_error=err,process=process,scope='Two independent rigid DOFs, indexed stock UniformMass, actual F/m and torque/I. Not mapped yoke, deformation, contact or whole-system energy qualification.',preflight_sha256=sha(out/'preflight.json'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
