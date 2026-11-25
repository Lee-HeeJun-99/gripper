"""Independent initial circular-beam end stiffness plus actual mapped mass."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat

def end_stiffness(E,nu,r,l):
 A=np.pi*r*r;I=np.pi*r**4/4;G=E/(2*(1+nu));K=np.diag([E*A/l,12*E*I/l**3,12*E*I/l**3,G*2*I/l,4*E*I/l,4*E*I/l]);K[1,5]=K[5,1]=-6*E*I/l**2;K[2,4]=K[4,2]=6*E*I/l**2;return K
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());source=BASE/'results/compliant_mass1860';baseline=json.loads((source/'summary.json').read_text());M=np.array(baseline['initial_tip_spatial_mass_matrix']);dt=baseline['dt_s'];K=end_stiffness(250e6,.3,.00025,.0015);records=[]
 for axis in range(6):
  folder=out/f'axis{axis}';folder.mkdir();src=source/f'axis{axis}/scene.scn';root=ET.parse(src).getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.SolidMechanics.FEM.Elastic'));root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Topology.Container.Constant'));node=root.find("Node[@name='shaft']");node.insert(0,ET.Element('MeshTopology',name='topology',position=flat([[0,0,0],[.0015,0,0],[.003,0,0]]),edges='0 1 1 2'));ET.SubElement(node,'BeamFEMForceField',template='Rigid3d',radius='.00025',radiusInner='0',youngModulus='250000000',poissonRatio='.3');node.find('NativeRigidJournal').set('filename',str(folder/'states.csv'));ET.ElementTree(root).write(folder/'scene.scn')
  process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));rec=dict(axis=axis,process=process,status='FAIL_INITIAL_ELASTIC_RESPONSE',scene_sha256=sha(folder/'scene.scn'),source_scene_sha256=sha(src),errors=[s for s in logs.splitlines() if '[ERROR]'in s])
  if process['exit_code']==0 and '[ERROR]'not in logs:
   rows=list(csv.DictReader((folder/'states.csv').open()));assert len(rows)==1;v=np.fromstring(rows[0]['rigid_v'],sep=' ').reshape(-1,6);f=np.zeros(6);f[axis]=1e-6 if axis<3 else 1e-9;expected=np.linalg.solve(M+dt*dt*K,dt*f);err=float(abs(v[-1]-expected).max());rel=float(np.linalg.norm(v[-1]-expected)/np.linalg.norm(expected));fixed=float(abs(v[:2]).max());rec.update(status='PASS_INITIAL_ELASTIC_RESPONSE_ONLY' if err<=1e-12 and rel<=1e-9 and fixed<=1e-12 else 'FAIL_ELASTIC_RESPONSE_REFERENCE',actual_tip_v=v[-1].tolist(),independent_tip_v=expected.tolist(),maximum_absolute_velocity_difference=err,relative_vector_difference=rel,fixed_node_velocity=fixed)
  records.append(rec)
 d=dict(status='PASS_COMPLIANT_INITIAL_M_PLUS_DT2_K_SCOPE' if all(x['status']=='PASS_INITIAL_ELASTIC_RESPONSE_ONLY' for x in records) else 'FAIL_COMPLIANT_INITIAL_ELASTIC_RESPONSE',records=records,independent_tip_K_N_m_rad=K.tolist(),source_mass_sha256=sha(source/'summary.json'),source_sha256=sha(Path(__file__)),scope='One-step initial EulerImplicit response to six independent forces/torques. Exact same1860mass and fixture, only stock BeamFEM added; terminal1.5mm element end stiffness independently computed. No nonlinear multi-step, Cable, contact, material, energy/time/mesh or grasp qualification. Absolute1e-12 and relative vector1e-9 predeclared, no floor or fitted coefficients.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
