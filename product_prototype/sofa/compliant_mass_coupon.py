"""Initial spatial inertia contract of finite shaft cells and rotor, no ODE fix."""
import argparse,csv,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat
sys.path.insert(0,str(BASE/'cad'))
from bellcrank_link_geometry import shapes
from finite_csg64 import register

def skew(r):
 x,y,z=r;return np.array([[0,-z,y],[z,0,-x],[-y,x,0.]])
def spatial(m,I,r):
 S=skew(r);return np.block([[m*np.eye(3),-m*S],[m*S,I+m*S.T@S]])
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());register()
 L=.003;r=.00025;rho=1000.;dt=.0001;positions=np.array([[0,0,0],[L/2,0,0],[L,0,0]]);boundaries=[0,L/4,3*L/4,L];cells=[]
 for i in range(3):
  h=boundaries[i+1]-boundaries[i];m=rho*np.pi*r*r*h;I=m*np.diag([r*r/2,(3*r*r+h*h)/12,(3*r*r+h*h)/12]);centre=np.array([(boundaries[i]+boundaries[i+1])/2,0,0]);cells.append(dict(index=i,mass=m,volume=m/rho,I=I,centre=centre))
 rotor=shapes()[0];rotor.apply_scale(.001);R=Rotation.from_euler('y',90,degrees=True).as_matrix();rotor.apply_transform(np.block([[R,np.zeros((3,1))],[np.zeros((1,3)),np.ones((1,1))]]));rotor.apply_translation([L+.0015,0,0]);rotor_data=dict(index=2,mass=rho*rotor.volume,volume=rotor.volume,I=rho*rotor.moment_inertia,centre=rotor.center_mass)
 M=spatial(cells[-1]['mass'],cells[-1]['I'],cells[-1]['centre']-positions[-1])+spatial(rotor_data['mass'],rotor_data['I'],rotor_data['centre']-positions[-1]);assert np.linalg.eigvalsh(M).min()>0
 journal=BASE/'cad/build_default_control332/libReGripProductSequence.so';records=[]
 for axis in range(6):
  folder=out/f'axis{axis}';folder.mkdir();f=np.zeros(6);f[axis]=1e-6 if axis<3 else 1e-9;root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
  for name in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer','Mapping.NonLinear','MechanicalLoad'):ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.'+name)
  ET.SubElement(root,'RequiredPlugin',pluginName=str(journal));ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'BlockGaussSeidelConstraintSolver',name='constraints');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(root,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd')
  node=ET.SubElement(root,'Node',name='shaft');ET.SubElement(node,'MechanicalObject',template='Rigid3d',name='frames',position=flat(np.column_stack([positions,np.tile([0,0,0,1],(3,1))])));ET.SubElement(node,'FixedProjectiveConstraint',template='Rigid3d',indices='0 1');ET.SubElement(node,'ConstantForceField',template='Rigid3d',indices='2',forces=flat([f]));ET.SubElement(node,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(folder/'states.csv'))
  for k,data in enumerate(cells+[rotor_data]):
   child=ET.SubElement(node,'Node',name=f'body{k}');ET.SubElement(child,'MechanicalObject',template='Rigid3d',name='com',position=flat([[*data['centre'],0,0,0,1]]));ET.SubElement(child,'RigidMapping',template='Rigid3d,Rigid3d',input='@../frames',output='@com',globalToLocalCoords='1',rigidIndexPerPoint=str(data['index']),mapMatrices='1');ET.SubElement(child,'UniformMass',template='Rigid3d',vertexMass=flat([[data['mass'],data['volume'],*(data['I']/data['mass']).ravel()]]))
  ET.ElementTree(root).write(folder/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));rec=dict(axis=axis,process=process,status='FAIL_NATIVE_INITIAL_MASS',scene_sha256=sha(folder/'scene.scn'),errors=[s for s in logs.splitlines() if '[ERROR]'in s])
  if process['exit_code']==0 and '[ERROR]'not in logs:
   rows=list(csv.DictReader((folder/'states.csv').open()));assert len(rows)==1;v=np.fromstring(rows[0]['rigid_v'],sep=' ').reshape(-1,6);expected=np.linalg.solve(M,dt*f);err=float(abs(v[-1]-expected).max());rel=float(np.linalg.norm(v[-1]-expected)/np.linalg.norm(expected));fixed=float(abs(v[:2]).max());rec.update(status='PASS_INITIAL_SPATIAL_MASS_ONLY' if err<=1e-12 and rel<=1e-9 and fixed<=1e-12 else 'FAIL_INITIAL_MASS_RESPONSE',actual_tip_v=v[-1].tolist(),independent_tip_v=expected.tolist(),maximum_absolute_velocity_difference=err,relative_vector_difference=rel,fixed_node_velocity=fixed)
  records.append(rec)
 d=dict(status='PASS_COMPLIANT_ROOT_INITIAL_MASS_SCOPE' if all(x['status']=='PASS_INITIAL_SPATIAL_MASS_ONLY' for x in records) else 'FAIL_COMPLIANT_ROOT_INITIAL_MASS',records=records,initial_tip_spatial_mass_matrix=M.tolist(),shaft_total_mass_kg=sum(c['mass'] for c in cells),shaft_volume_m3=np.pi*r*r*L,rotor_mass_kg=rotor_data['mass'],rotor_COM_m=rotor_data['centre'].tolist(),rotor_COM_inertia_kg_m2=rotor_data['I'].tolist(),density_assumed_kg_m3=rho,dt_s=dt,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256={str(journal):sha(journal)},scope='Six independent one-step full spatial mass response checks at rest; stock Rigid3-Rigid3 Mapping of exact cylinder cell COMs and finite3bore rotor COM/tensor. Three Voronoi cells cover entire3mm shaft without changed volume/mass; only last cell and rotor mobile because other nodes fixed. No BeamFEM/cable/contact or finite-velocity force law in this isolation coupon; not a complete deformable shaft dynamic test. Assumedrho1000 not measured hardware. No first-component getMass inference, customODE, correction or tolerance change. No time/mesh/energy/grasp PASS.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
