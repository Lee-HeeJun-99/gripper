"""Native BeamFEM static pure-moment flexure reference; not Finger redesign."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());E=250e6;radius=.00025;length=.003;moment=1e-7;I=np.pi*radius**4/4;theta=moment*length/(E*I);reference_y=length*(1-np.cos(theta))/theta
 mesh=trimesh.creation.cylinder(radius=.25,height=3,sections=32);mesh.apply_transform(trimesh.geometry.align_vectors([0,0,1],[1,0,0]));mesh.apply_translation([1.5,0,0]);assert mesh.is_volume;mesh.export(out/'round_flexure_rest_mm.stl')
 binary=BASE/'cad/build_default_control332/libReGripProductSequence.so';records=[]
 for count in (3,5,9):
  folder=out/f'n{count}';folder.mkdir();root=ET.Element('Node',name='root',dt='1',gravity='0 0 0')
  for plugin in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer','Topology.Container.Constant','SolidMechanics.FEM.Elastic','MechanicalLoad'):
   ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
  ET.SubElement(root,'RequiredPlugin',pluginName=str(binary));ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'BlockGaussSeidelConstraintSolver',name='constraints')
  n=ET.SubElement(root,'Node',name='flexure');q=np.zeros((count,7));q[:,0]=np.linspace(0,length,count);q[:,6]=1;ET.SubElement(n,'MeshTopology',name='topology',position=flat(q[:,:3]),edges=flat(np.column_stack([np.arange(count-1),np.arange(1,count)])));ET.SubElement(n,'MechanicalObject',name='frames',template='Rigid3d',position=flat(q));ET.SubElement(n,'FixedProjectiveConstraint',template='Rigid3d',indices='0');ET.SubElement(n,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton='25',absoluteResidualStoppingThreshold='1e-12',relativeInitialStoppingThreshold='1e-12',printLog='1');ET.SubElement(n,'StaticSolver',newtonSolver='@newton');ET.SubElement(n,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');ET.SubElement(n,'BeamFEMForceField',template='Rigid3d',name='nativeFlexure',radius=str(radius),radiusInner='0',youngModulus=str(E),poissonRatio='.3');ET.SubElement(n,'ConstantForceField',template='Rigid3d',indices=str(count-1),forces=flat([[0,0,0,0,0,moment]]));ET.SubElement(n,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(folder/'states.csv'))
  ET.ElementTree(root).write(folder/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','3','--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));record=dict(nodes=count,process=proc,scene_sha256=sha(folder/'scene.scn'),status='FAIL_NATIVE_FLEXURE_STATIC',errors=[s for s in logs.splitlines() if '[ERROR]'in s])
  if proc['exit_code']==0 and '[ERROR]'not in logs and (folder/'states.csv').exists():
   rows=list(csv.DictReader((folder/'states.csv').open()));states=[np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows]
   if len(states)==3:
    tip=states[-1][-1];angle=float(Rotation.from_quat(tip[3:]).as_rotvec()[2]);relative_angle=abs(angle-theta)/abs(theta);relative_y=abs(tip[1]-reference_y)/abs(reference_y);stationarity=float(abs(states[-1]-states[-2]).max());ok=max(relative_angle,relative_y)<=.01 and stationarity<=1e-12;record.update(status='PASS_SMALL_STATIC_FLEXURE_REFERENCE_ONLY' if ok else 'FAIL_STATIC_FLEXURE_REFERENCE_OR_STATIONARITY',tip_angle_rad=angle,tip_y_m=float(tip[1]),angle_reference_relative_error=relative_angle,tip_y_reference_relative_error=relative_y,last_state_change=stationarity)
  records.append(record)
 pairs=[]
 for j,x in enumerate(records):
  for y in records[j+1:]:
   if 'tip_y_m'in x and 'tip_y_m'in y:pairs.append(dict(nodes=[x['nodes'],y['nodes']],tip_y_relative_difference=abs(x['tip_y_m']-y['tip_y_m'])/max(abs(x['tip_y_m']),abs(y['tip_y_m']))))
 result=dict(status='PASS_SMALL_STATIC_FLEXURE_MESH_PAIR_SCOPE' if all(r['status']=='PASS_SMALL_STATIC_FLEXURE_REFERENCE_ONLY' for r in records) and len(pairs)==3 and all(p['tip_y_relative_difference']<=.01 for p in pairs) else 'FAIL_OR_BLOCKED_NATIVE_FLEXURE',records=records,mesh_pairs=pairs,configuration=dict(length_m=length,radius_m=radius,E_assumed_Pa=E,poisson_ratio_assumed=.3,pure_moment_Nm=moment,root_fixed=True,no_cable_contact_guide=True,model='installed stock BeamFEMForceField circular cross-section'),independent_small_bending_reference=dict(I_m4=I,EI_Nm2=E*I,tip_angle_rad=theta,tip_y_m=reference_y,outer_fibre_reference_strain=radius*theta/length),strain_energy_J=None,root_reaction_N_Nm=None,material_allowable_strain=None,source_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256=sha(binary),installed_forcefield_source_sha256=sha(Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.SolidMechanics.FEM.Elastic/sofa/component/solidmechanics/fem/elastic/BeamFEMForceField.inl')),scope='Alternative compliant-joint necessary coupon, not repeat thin-TetraB3/FEM372. Static pure moment, no mass/time integration/actual hardware data. E250MPa research assumption inherited from B3, not fitted or measured. Euler small-bending reference is approximate; result only small static circular beam response. No finite-operation flexure, pin replacement assembly, dynamic energy/time, Finger, Skin wrapping or grasp PASS.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
