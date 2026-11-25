"""Different physical representation: free elastic Vec3 solid, no RigidMapping.
Finite-speed conservation coupon only, NOT a replacement Guide geometry/load test.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());q=np.array([[x,y,z] for x in [0,.002] for y in [0,.008,.016,.024] for z in [0,.002]]);idx=lambda x,y,z:x*8+y*2+z;tet=[]
 for y in range(3):
  aa,b,c,d,e,f,g,h=[idx(x,y+dy,z) for x,dy,z in [(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0,0,1),(1,0,1),(0,1,1),(1,1,1)]];tet.extend([[aa,b,d,h],[aa,d,c,h],[aa,c,g,h],[aa,g,e,h],[aa,e,f,h],[aa,f,b,h]])
 tet=np.array(tet);D=(q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1)
 for k in np.flatnonzero(np.linalg.det(D)<0):tet[k,[1,2]]=tet[k,[2,1]]
 D=(q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1);volume=np.linalg.det(D)/6;assert (volume>0).all();rho=1000.;m=np.zeros(len(q))
 for cell,V in zip(tet,volume):m[cell]+=rho*V/4
 assert abs(m.sum()-rho*.002*.024*.002)<1e-18;centre=(m[:,None]*q).sum(0)/m.sum();omega=np.array([.1,.2,.3]);translation=np.array([.001,-.002,.003]);v=translation+np.cross(omega,q-centre);dt=.0001;root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0');flat=lambda a:' '.join(format(float(x),'.17g') for x in np.array(a).ravel());journal=BASE/'cad/build_default_control332/libReGripProductSequence.so'
 for plugin in ['AnimationLoop','ODESolver.Backward','LinearSolver.Direct','Mass','StateContainer','Topology.Container.Constant','SolidMechanics.FEM.Elastic']:ET.SubElement(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
 ET.SubElement(root,'RequiredPlugin',pluginName=str(journal));ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(root,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');node=ET.SubElement(root,'Node',name='support');ET.SubElement(node,'MeshTopology',name='mesh',position=flat(q),tetrahedra=flat(tet));ET.SubElement(node,'MechanicalObject',template='Vec3d',name='dofs',position=flat(q),velocity=flat(v));ET.SubElement(node,'DiagonalMass',template='Vec3d',vertexMass=flat(m));ET.SubElement(node,'TetrahedronFEMForceField',name='solid',method='large',youngModulus='250000000',poissonRatio='.3');ET.SubElement(node,'NativePointJournal',body='@dofs',filename=str(out/'states.csv'));ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),journal_binary_sha256=sha(journal),rest_q_m=q.tolist(),initial_v_m_s=v.tolist(),tetrahedra=tet.tolist(),nodal_mass_kg=m.tolist(),total_mass_kg=float(m.sum()),minimum_rest_volume_m3=float(volume.min()),density_assumed_kg_m3=rho,young_assumed_Pa=250e6,poisson_assumed=.3,dt_s=dt,steps=50,scope='Explicit18tet/16node prismatic elastic support, no contact/cable/bond/fixedroot or mapped rigid mass. Inherited research material, not actual hardware. Not actual1.5N transfer or finite eyelet/bore geometry.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','50','--hideProgressBar',out/'scene.scn'],out/'process',60);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ['stdout.log','stderr.log']);metrics={};ok=proc['exit_code']==0 and '[ERROR]'not in logs
 if ok:
  rows=list(csv.DictReader((out/'states.csv').open()));assert len(rows)==50;P0=(m[:,None]*v).sum(0);L0=np.cross(q,m[:,None]*v).sum(0);p_error=0.;l_error=0.;minimum=1.;speed=0.
  for r in rows:
   x=np.fromstring(r['q'],sep=' ').reshape(-1,3);vel=np.fromstring(r['v'],sep=' ').reshape(-1,3);p_error=max(p_error,float(abs((m[:,None]*vel).sum(0)-P0).max()));l_error=max(l_error,float(abs(np.cross(x,m[:,None]*vel).sum(0)-L0).max()));minimum=min(minimum,float((np.linalg.det((x[tet[:,1:]]-x[tet[:,0,None]]).transpose(0,2,1))/(6*volume)).min()));speed=max(speed,float(np.linalg.norm(vel,axis=1).max()))
  metrics=dict(maximum_linear_momentum_error_Ns=p_error,maximum_angular_momentum_error_Nms=l_error,minimum_saved_volume_ratio=minimum,maximum_nodal_speed_m_s=speed);ok=p_error<=1e-12 and l_error<=1e-12 and minimum>0
 d=dict(status='PASS_DIRECT_VEC3_FINITE_SPEED_CONSERVATION_COUPON_ONLY' if ok else 'FAIL_DIRECT_VEC3_CONSERVATION_COUPON',process=proc,metrics=metrics,preflight_sha256=sha(out/'preflight.json'),source_sha256=sha(Path(__file__)),scope=pre['scope']+' Independent closed-system finite mixed velocity conservation, NOT solving original6Dmapping or proving Guide drop-in/grasp/time/mesh/material qualification. Actual topology/attachment/bore and load transfer still required. No SDK/custom physics/state correction.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
