"""Minimal installed stock Rigid3/DiagonalMass probe; not a grasp test."""
import argparse,json,xml.etree.ElementTree as ET,hashlib,sys,subprocess,csv
from pathlib import Path
import numpy as np
from run_native import BASE,ROOT,SDK,add,sha
sys.path.insert(0,str(ROOT/'tools'))
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--template',default='Rigid3d');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);old=json.loads((BASE/'results/native_mass_api_purity_139/summary.json').read_text());binary=ROOT/old['build']/'libReGripProductSequence.so'
 if sha(binary)!=old['binary_sha256']:raise ValueError('binary identity mismatch')
 root=ET.Element('Node',dt='.001',gravity='0 0 -9.81');
 for name in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','LinearSolver.Direct','ODESolver.Backward','StateContainer','Mass','Mapping.NonLinear','Topology.Container.Constant'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+name)
 add(root,'RequiredPlugin',pluginName=str(binary));add(root,'FreeMotionAnimationLoop');add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance=1e-10,maxIterations=1000,computeConstraintForces=1);add(root,'EulerImplicitSolver');add(root,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');add(root,'GenericConstraintCorrection');body=add(root,'Node',name='body');add(body,'MechanicalObject',name='frames',template='Rigid3d',position='0 0 0 0 0 0 1',velocity='0 0 0 0 0 0');add(body,'DiagonalMass',name='mass',template=a.template,vertexMass='.001 1e-8 1e-6 0 0 0 2e-6 0 0 0 3e-6');add(body,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass=1,filename=str(out/'body.csv'));child=add(body,'Node',name='mapped');add(child,'MechanicalObject',name='points',template='Vec3d',position='.01 0 0');add(child,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords=0);ET.ElementTree(root).write(out/'scene.scn');process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',out/'scene.scn'],out/'process',60);errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'));result=dict(status='FAIL',scope='minimal Rigid3 native mass/rigid mapping ONLY,not full bridge or SubsetMultiMapping qualification',template=a.template,process=process,sofa_errors=errors,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),sdk=str(SDK),scene_sha256=sha(out/'scene.scn'))
 if process['exit_code']==0 and not errors:
  rows=list(csv.DictReader((out/'body.csv').open()));v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);error=float(np.max(abs(v[:,2]+9.81*np.arange(1,5)*.001)));result.update(status='PASS_MINIMAL_TRANSLATION' if error<1e-12 else 'FAIL',gravity_velocity_error_m_s=error,rows=len(rows),mass_api_file='body.csv.mass.json')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
