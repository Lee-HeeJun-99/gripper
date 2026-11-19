"""Stock straight-cable command tracking isolation; NOT finger/grasp physics."""
import argparse,csv,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent;sys.path.insert(0,str(ROOT/'tools'))
from film_guarded_process import guarded
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--build-case',default='native_single_generic_045');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.build_case;m=json.loads((src/'summary.json').read_text());binary=ROOT/m['build']/'libReGripProductSequence.so'
 if sha(binary)!=m['binary_sha256'] or sha(BASE/'sofa/Controller.cpp')!=m['source_hashes']['Controller.cpp']:raise ValueError('exact input/logger binary required')
 tree=ET.parse(src/'scene.scn');root=tree.getroot()
 for node in list(root):
  if node.tag=='Node':root.remove(node)
 root.find('GenericConstraintSolver').tag='BlockGaussSeidelConstraintSolver'
 def add(parent,tag,**kw):return ET.SubElement(parent,tag,{k:str(v) for k,v in kw.items()})
 add(root,'RequiredPlugin',pluginName='Sofa.Component.SolidMechanics.Spring')
 finger=add(root,'Node',name='coupon');add(finger,'EulerImplicitSolver');add(finger,'SparseLDLSolver',name='linear');add(finger,'MechanicalObject',name='dofs',template='Vec3d',position='0 0 0 .01 0 0');add(finger,'UniformMass',totalMass=.002);add(finger,'RestShapeSpringsForceField',stiffness=1000,points='0 1');add(finger,'GenericConstraintCorrection')
 for j in (0,1):
  node=add(finger,'Node',name=f'cable{j}');add(node,'MechanicalObject',name='points',template='Vec3d',position=f'{j*.01} 0 0');add(node,'CableConstraint',name='actuator',indices=0,pullPoint=f'{j*.01} 0 .1',value=0,valueType='displacement',minForce=0);add(node,'SubsetMapping',input='@../dofs',output='@points',indices=j,handleTopologyChange=0)
 add(finger,'NativeCableSequence',body='@dofs',cable0='@cable0/actuator',cable1='@cable1/actuator',filename=str(out/'coupon.csv'),stroke=.005)
 tree.write(out/'scene.scn');r=dict(scope='two independent straight cables on native spring-mass points;NOT FEM/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),scene_sha256=sha(out/'scene.scn'),dt_s=.0025,mass_kg=.001,stiffness_N_per_m=1000,sdk='/home/ubuntu/SOFA/v26.06.00');r['process']=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','800','--hideProgressBar',out/'scene.scn'],out/'process',480);r['status']='FAIL'
 if r['process']['exit_code']==0:
  rows=list(csv.DictReader((out/'coupon.csv').open()));errors=[]
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(2,3)
   for j in (0,1):errors.append(abs(.1-np.linalg.norm(q[j]-np.array([j*.01,0,.1]))-float(row['command_m'])))
  r.update(rows=len(rows),maximum_path_tracking_error_m=max(errors),strict_api_gate_m=1e-12,status='PASS' if len(rows)==800 and max(errors)<=1e-12 else 'FAIL',raw_sha256=sha(out/'coupon.csv'))
 (out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
