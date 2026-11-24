"""Matched linear composite FEM diagnostic,not a B3 grasp replacement.

Guide/Cable/contact removed identically in BOTH coupons to isolate material
bending. Thus this does not certify the full rigid-guide mapping contract.
Original curved reference/root/material preserved;added nodal mass retained.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.linalg import cho_factor,cho_solve
from analyse import BASE,sha
from native_bending_coupon import guarded
from b3_contact_layer_native import add,flat
from layer_bending_reference import element,elastic

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--origin-shift',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 src=BASE/'results/b3_railback_grasp1001298';geo=BASE/'results/proximal_reinforcement_geometry1364';mesh=json.loads((src/'mesh.json').read_text());g=json.loads((geo/'mesh.json').read_text());old=ET.parse(src/'scene.scn').getroot();f=old.find("Node[@name='finger0']");q0=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);t0=np.array(mesh['tetrahedra']);local0=np.array(mesh['local_positions_mm']);records=[];young=250e6;nu=.3;D=elastic(young,nu)
 for reinforced in (False,True):
  name='reinforced' if reinforced else 'baseline';folder=out/name;folder.mkdir();q=q0.copy();tet=t0.copy();local=local0.copy();mass=np.full(len(q),.001/len(q))
  if reinforced:
   remap=np.empty(len(g['local_positions_mm']),int);remap[::2]=g['bottom_Skin_parent_indices'];remap[1::2]=np.arange(len(q),len(q)+len(remap)//2);q=np.vstack([q,np.array(g['world_reference_m'][0])[1::2]]);local=np.vstack([local,np.array(g['local_positions_mm'])[1::2]]);tet=np.vstack([tet,remap[np.array(g['tetrahedra'])]]);mass=np.r_[mass,np.zeros(len(remap)//2)];np.add.at(mass,remap,g['records'][0]['mass_kg']/len(remap))
  fixed=np.flatnonzero(local[:,0]<=5);free=np.flatnonzero(np.repeat(local[:,0]>5,3));K=np.zeros((3*len(q),)*2);det=[]
  for t in tet:
   V,B,_=element(q[t],D);idx=(3*t[:,None]+np.arange(3)).ravel();K[np.ix_(idx,idx)]+=V*B.T@D@B;det.append(float(np.linalg.det((q[t[1:]]-q[t[0]]).T)))
  if a.origin_shift:
   q=q-q0.mean(0);K[:]=0;det=[]
   for t in tet:
    V,B,_=element(q[t],D);idx=(3*t[:,None]+np.arange(3)).ravel();K[np.ix_(idx,idx)]+=V*B.T@D@B;det.append(float(np.linalg.det((q[t[1:]]-q[t[0]]).T)))
  F=np.zeros_like(q);tip=np.flatnonzero((local[:,0]==100)&(local[:,2]==.1));F[tip,0]=-1e-5/len(tip);force=F.ravel();kf=K[np.ix_(free,free)];factor=cho_factor(kf);us=np.zeros(3*len(q));us[free]=cho_solve(factor,force[free]);reaction=(K@us-force).reshape(-1,3)[fixed].sum(0);energy=float(.5*us@K@us);equilibrium=float(abs((K@us-force)[free]).max());massdiag=np.repeat(mass,3)[free];dt=.0025;steps=20;A=np.diag(massdiag)+dt*dt*kf;cf=cho_factor(A);u=np.zeros(len(free));v=u.copy();reference=[]
  for _ in range(steps):v=cho_solve(cf,massdiag*v+dt*(force[free]-kf@u));u+=dt*v;reference.append((u.copy(),v.copy()))
  root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
  for plugin in ('AnimationLoop','Constraint.Projective','LinearSolver.Direct','Mass','ODESolver.Backward','SolidMechanics.FEM.Elastic','StateContainer','Topology.Container.Constant','MechanicalLoad'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
  binary=BASE/'cad/build_default_control332/libReGripProductSequence.so';add(root,'RequiredPlugin',pluginName=binary);add(root,'DefaultAnimationLoop');add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0);add(root,'SparseLDLSolver',template='CompressedRowSparseMatrixd');add(root,'MeshTopology',position=flat(q),tetrahedra=flat(tet));add(root,'MechanicalObject',name='dofs',template='Vec3d',position=flat(q));add(root,'DiagonalMass',template='Vec3d',mass=flat(mass));add(root,'FixedProjectiveConstraint',indices=' '.join(map(str,fixed)));add(root,'TetrahedronFEMForceField',method='small',youngModulus=young,poissonRatio=nu);add(root,'ConstantForceField',indices=' '.join(map(str,tip)),forces=flat(F[tip]));add(root,'NativePointJournal',body='@dofs',filename=folder/'states.csv');ET.ElementTree(root).write(folder/'scene.scn')
  root.find('DiagonalMass').set('template','Vec3d,Vec3d');root.find('DiagonalMass').set('vertexMass',root.find('DiagonalMass').attrib.pop('mass'));ET.ElementTree(root).write(folder/'scene.scn')
  np.savez(folder/'reference.npz',q=q,tetrahedra=tet,nodal_mass_kg=mass,static_u=us.reshape(-1,3),F=F,K=K)
  cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(folder/'scene.scn')];pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),scene_sha256=sha(folder/'scene.scn'),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (src/'mesh.json',src/'scene.scn',geo/'mesh.json')},mass_kg=float(mass.sum()),young_Pa=young,nu=nu,total_force_N=1e-5,dt_s=dt,steps=steps,forecast_s=5,child_limit_s=30,memory_GiB=4,scope='Matched guide-free linear curved composite coupon,not fullB3. Native transient compared BE;static reference NOT claimed Native equilibrium.');(folder/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,folder/'process',30);rows=list(csv.DictReader((folder/'states.csv').open())) if (folder/'states.csv').exists() else [];eq=[];ev=[]
  for r,(ur,vr) in zip(rows,reference):
   qa=np.fromstring(r['q'],sep=' ');va=np.fromstring(r['v'],sep=' ');expect=q.ravel().copy();expect[free]+=ur;eq.append(float(abs(qa-expect).max()));ev.append(float(abs(va[free]-vr).max()))
  log=''.join((folder/'process'/x).read_text() for x in ('stdout.log','stderr.log'));valid=proc['exit_code']==0 and '[ERROR]'not in log and len(rows)==steps and max(eq,default=1)<=1e-12 and max(ev,default=1)<=1e-12
  disp=us.reshape(-1,3);centres=[disp[(local[:,0]==s)&(local[:,2]==.1)].mean(0).tolist() for s in np.unique(local0[:,0])];records.append(dict(name=name,status='PASS_LINEAR_TRANSIENT_REFERENCE_ONLY' if valid else 'FAIL_NATIVE_OR_REFERENCE',process=proc,nodes=len(q),tets=len(tet),mass_kg=float(mass.sum()),min_reference_determinant_m3=min(det),static_tip_x_m=float(disp[tip,0].mean()),static_compliance_m_N=float(force@us/(1e-5)**2),static_energy_J=energy,static_half_work_J=float(.5*force@us),static_equilibrium_max_N=equilibrium,static_root_force_N=reaction.tolist(),static_width_mean_displacement_m=centres,native_position_error_m=max(eq,default=None),native_velocity_error_m_s=max(ev,default=None),native_outputs=len(rows)))
 d=dict(status='PASS_MATCHED_LINEAR_COMPOSITE_DIAGNOSTIC' if all(r['status'].startswith('PASS') for r in records) else 'FAIL_MATCHED_DIAGNOSTIC',records=records,static_effective_stiffness_ratio=records[0]['static_compliance_m_N']/records[1]['static_compliance_m_N'],scope='Linear discrete stiffness and shortNativeBE matching only. No Native static equilibrium,mesh/time convergence,fullGuideMapping,largeFEM,contact,Holding or variable-stiffness certification.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
