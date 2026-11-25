"""Matched pure-mass cable phase coupon; independent impulse/work accounting."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def flat(x):return ' '.join(format(float(z),'.17g') for z in np.asarray(x).ravel())
def read(p):return list(csv.DictReader(p.open()))
def jac(q,origin):
 x=np.vstack([origin,q]);delta=np.diff(x,axis=0);u=delta/np.linalg.norm(delta,axis=1)[:,None];J=-u.copy();J[:-1]+=u[1:];return J
def matrix(text,n):
 J=np.zeros((n,3))
 for part in text.split(';'):
  if part:
   row,col,value=part.split(':');assert int(row)==0;J[int(col)]=np.fromstring(value,sep=' ')
 return J

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 dt=.01;mass=.01;T=.05;steps=5;origin=np.zeros(3)
 q0=np.array([[.01,0,0],[.02,.01,0],[.03,.01,.01]]);v0=np.array([[0,.1,0],[.02,0,.04],[-.03,.01,0]])
 binary=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so';journal=BASE/'cad/build_default_control332/libReGripProductSequence.so';records=[]
 compiled=BASE/'results/b3_cable_typed1831';meta=json.loads((compiled/'phase_assessment.json').read_text())
 assert sha(binary)==meta['binary_sha256'] and sha(BASE/'sofa/native_cable_phase/Observer.cpp')==sha(compiled/'Observer.cpp'),'frozen compiled observer identity mismatch'
 for enabled in (False,True):
  folder=out/('observed' if enabled else 'control');folder.mkdir();r=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
  for name in ('AnimationLoop','Constraint.Lagrangian.Solver','Constraint.Lagrangian.Correction','LinearSolver.Direct','Mass','ODESolver.Backward','StateContainer'):
   ET.SubElement(r,'RequiredPlugin',pluginName='Sofa.Component.'+name)
  for name in (str(journal),'/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'):
   ET.SubElement(r,'RequiredPlugin',pluginName=name)
  if enabled:ET.SubElement(r,'RequiredPlugin',pluginName=str(binary))
  ET.SubElement(r,'FreeMotionAnimationLoop');ET.SubElement(r,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-12',maxIterations='1000',computeConstraintForces='1')
  ET.SubElement(r,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(r,'SparseLDLSolver',name='linear',template='CompressedRowSparseMatrixd');ET.SubElement(r,'GenericConstraintCorrection')
  node=ET.SubElement(r,'Node',name='coupon');ET.SubElement(node,'MechanicalObject',name='points',template='Vec3d',position=flat(q0),velocity=flat(v0));ET.SubElement(node,'UniformMass',totalMass=str(mass*3))
  ET.SubElement(node,'CableConstraint',name='actuator',template='Vec3d',indices='0 1 2',pullPoint='0 0 0',valueType='force',value=str(T*dt),minForce='0')
  ET.SubElement(r,'NativePointJournal',body='@coupon/points',filename=str(folder/'points.csv'));ET.SubElement(r,'NativeConstraintJournal',solver='@constraints',filename=str(folder/'constraints.csv'))
  if enabled:ET.SubElement(r,'NativeCablePhase',body='@coupon/points',solver='@constraints',cable='@coupon/actuator',filename=str(folder/'phases.csv'))
  ET.ElementTree(r).write(folder/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',folder/'scene.scn'],folder/'process',60)
  logs=''.join((folder/'process'/s).read_text(errors='replace') for s in ('stdout.log','stderr.log'));assert process['exit_code']==0 and '[ERROR]' not in logs,logs[-3000:]
  records.append(dict(case=folder.name,process=process,scene_sha256=sha(folder/'scene.scn')))
 control=read(out/'control/points.csv');observed=read(out/'observed/points.csv');assert len(control)==len(observed)==steps
 purity=max(float(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')).max()) for x,y in zip(control,observed) for k in ('q','v'))
 phases=read(out/'observed/phases.csv');metrics=[]
 for k in range(steps):
  phase={r['phase']:r for r in phases if int(r['step'])==k};assert set(phase)=={'build_end','solve_end','accepted_end'}
  b,s,e=(phase[n] for n in ('build_end','solve_end','accepted_end'))
  q=np.fromstring(b['q'],sep=' ').reshape(-1,3);v=np.fromstring(b['v'],sep=' ').reshape(-1,3);fq=np.fromstring(b['free_q'],sep=' ').reshape(-1,3);fv=np.fromstring(b['free_v'],sep=' ').reshape(-1,3)
  acceptedq=np.fromstring(e['q'],sep=' ').reshape(-1,3);acceptedv=np.fromstring(e['v'],sep=' ').reshape(-1,3);J=matrix(b['J'],3);lam=float(s['lambda_Ns']);imp=lam*J
  # Midpoint velocity gives the exact kinetic increment for an actual impulse.
  kinetic=.5*mass*float((acceptedv**2-fv**2).sum());mid_work=float((imp*(acceptedv+fv)/2).sum());frozen_work=float((imp*acceptedv).sum())
  metrics.append(dict(step=k,previous_geometry_J_error=float(abs(J-jac(q,origin)).max()),free_geometry_J_difference=float(abs(J-jac(fq,origin)).max()),accepted_geometry_J_difference=float(abs(J-jac(acceptedq,origin)).max()),free_velocity_error=float(abs(fv-v).max()),free_position_error=float(abs(fq-q-dt*v).max()),force_N=lam/dt,impulse_velocity_error=float(abs(mass*(acceptedv-fv)-imp).max()),accepted_position_error=float(abs(acceptedq-fq-dt*(acceptedv-fv)).max()),kinetic_increment_J=kinetic,impulse_midpoint_work_J=mid_work,accepted_velocity_impulse_product_J=frozen_work,implicit_algorithmic_loss_J=frozen_work-mid_work,accepted_force_raw=float(e['cable_force_raw']),solve_end_force_raw=float(s['cable_force_raw'])))
 ok=purity==0 and all(max(m['previous_geometry_J_error'],m['free_velocity_error'],m['free_position_error'],m['impulse_velocity_error'],m['accepted_position_error'],abs(m['kinetic_increment_J']-m['impulse_midpoint_work_J']),abs(m['force_N']-T))<=1e-12 for m in metrics)
 d=dict(status='PASS_CABLE_PHASE_AND_KINETIC_COUPON_ONLY' if ok else 'FAIL_CABLE_PHASE_COUPON',purity_q_v_difference=purity,metrics=metrics,runs=records,assumptions=dict(dt_s=dt,mass_per_point_kg=mass,tension_N=T,steps=steps,gravity_contact_mapping_FEM=False),source_sha256=sha(Path(__file__)),observer_source_sha256=sha(BASE/'sofa/native_cable_phase/Observer.cpp'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),binary_sha256={str(f):sha(f) for f in (binary,journal,Path('/home/ubuntu/SOFA/v26.06.00/plugins/SoftRobots/lib/libSoftRobots.so'))},scope='Actual no-contact pure diagonal mass coupon. J is observed, not inferred from commanded force. Midpoint impulse identity is kinetic bookkeeping, not global FEM/contact energy or continuous motor passivity. No new grasp/Guide independence claim.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'Observer.cpp').write_bytes((BASE/'sofa/native_cable_phase/Observer.cpp').read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
