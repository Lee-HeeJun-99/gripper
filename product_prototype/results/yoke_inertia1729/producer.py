"""Actual candidate's full tensors in indexed stock Native mass assembly.
One initially resting step only, no claim about deformed nonlinear dynamics.
"""
import argparse,csv,copy,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);design=ET.parse(src/'scene.scn').getroot();root=ET.Element('Node',dt='.001',gravity='0 0 0')
 for n in design:
  if n.tag in ('RequiredPlugin','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','EulerImplicitSolver','SparseLDLSolver','GenericConstraintCorrection'):root.append(copy.deepcopy(n))
 ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad');body=ET.SubElement(root,'Node',name='test');ET.SubElement(body,'MechanicalObject',name='frames',template='Rigid3d',position=flat([[.02*i,0,0,0,0,0,1] for i in range(3)]));expected=[];force=np.array([1e-4,2e-4,-1e-4]);torque=np.array([1e-8,2e-8,3e-8])
 for i in range(3):
  v=design.find(f"Node[@name='guides{i}']/UniformMass[@name='yokeMass']").get('vertexMass');ET.SubElement(body,'UniformMass',name=f'mass{i}',template='Rigid3d',indices=str(i),vertexMass=v);data=np.fromstring(v,sep=' ');m=data[0];I=data[2:].reshape(3,3)*m;expected.append(np.r_[force/m,np.linalg.solve(I,torque)]*.001)
 ET.SubElement(body,'ConstantForceField',template='Rigid3d',indices='0 1 2',forces=flat([np.r_[force,torque]]*3));ET.SubElement(body,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(out/'body.csv'));ET.ElementTree(root).write(out/'scene.scn')
 process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));err=None
 if process['exit_code']==0 and '[ERROR]'not in logs:
  rows=list(csv.DictReader((out/'body.csv').open()));assert len(rows)==1;actual=np.fromstring(rows[0]['rigid_v'],sep=' ').reshape(-1,6);err=float(abs(actual-np.array(expected)).max())
 d=dict(status='PASS_ACTUAL_YOKE_INITIAL_TENSOR_ASSEMBLY_ONLY' if err is not None and err<=1e-12 else 'FAIL_ACTUAL_YOKE_TENSOR_ASSEMBLY',case=a.case,maximum_velocity_error=err,expected_velocity=np.array(expected).tolist(),process=process,source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),scope='Actual three full non-diagonal tensors, known six-component input and initially zero velocity. Initial Native A response only; not full nonlinear/contact/energy or hardware qualification. Same SDK/plugins as candidate.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
