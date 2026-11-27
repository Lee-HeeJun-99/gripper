"""Independent affine tetra forces/energy and rigid virtual work. No solver imports."""
import json,sys,shutil
import numpy as np
from scipy import sparse
from baseline_registry import ROOT,REPO,ref,sha,dump
BODIES=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','F0_MICRO_MOTOR']
def wrench(n,f,a):
 if n=='F0_MICRO_MOTOR':
  o=int(a['motor_offset']);return np.r_[f[o:o+3],f[o+3:o+6]*.001+np.cross([0,0,.020],f[o:o+3])]
 p=a[n+'_points_mm'];off=int(a[n+'_offset']);ff=f[off:off+3*len(p)].reshape(-1,3);return np.r_[ff.sum(axis=0),np.cross(p*.001,ff).sum(axis=0)]
def reconstruct(a,s,bad=False):
 global BODIES
 BODIES=s.get('elastic_bodies',BODIES[:-1])+['F0_MICRO_MOTOR']
 u=a['u_mm'].copy()
 if bad:u[np.argmax(abs(u[:int(a['motor_offset'])]))]+=1e-5
 F=np.zeros_like(u);energy=0;vmrows=[]
 for n in BODIES[:-1]:
  p=a[n+'_points_mm'];t=a[n+'_tetra'];off=int(a[n+'_offset']);E=float(a[n+'_E_MPa']);nu=float(a[n+'_nu']);uu=u[off:off+3*len(p)].reshape(-1,3);dx=p[t[:,1:]]-p[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));stress=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);vol=abs(np.linalg.det(dx))/6;gradN=np.empty((len(t),4,3));gradN[:,1:,:]=np.linalg.inv(dx).transpose(0,2,1);gradN[:,0,:]=-gradN[:,1:,:].sum(axis=1);fe=np.einsum('eij,ekj,e->eki',stress,gradN,vol)
  for j in range(4):
   for k in range(3):np.add.at(F,off+3*t[:,j]+k,fe[:,j,k])
  energy+=float(np.sum(.5*np.einsum('eij,eij->e',eps,stress)*vol));dev=stress-np.trace(stress,axis1=1,axis2=2)[:,None,None]*np.eye(3)/3;vm=np.sqrt(1.5*np.sum(dev*dev,axis=(1,2)));vmrows.append(float(np.max(abs(vm-a[n+'_vm_MPa']))))
 C=sparse.csr_matrix((a['contact_C_data'],a['contact_C_indices'],a['contact_C_indptr']),shape=tuple(a['contact_C_shape']));D=a['bolt_D'];p=a['contact_force_N'];bf=a['bolt_force_N'];res=F-a['applied_force_N']-C.T@p+D.T@bf;g=C@u+a['initial_gaps_mm'];k=a['bolt_k_N_mm'];pred=np.maximum(k*(D@u)+s['preload_each_N'],0);spring=.5*float(np.sum(bf**2/k));identity=2*(energy+spring)-float(a['applied_force_N']@u)-float(np.sum(s['preload_each_N']/k*bf))+float(p@a['initial_gaps_mm']);w={n:wrench(n,res,a).tolist() for n in BODIES};contact=-C.T@p;bolt=D.T@bf
 # Independent direct rigid virtual displacement including motor rotations.
 works=[]
 for j in range(6):
  v=np.zeros_like(u);translation=np.eye(3)[j] if j<3 else np.zeros(3);rotation=np.eye(3)[j-3] if j>=3 else np.zeros(3)
  for n in BODIES[:-1]:
   pts=a[n+'_points_mm']*.001;off=int(a[n+'_offset']);v[off:off+3*len(pts)]=(translation+np.cross(rotation,pts)).ravel()
  o=int(a['motor_offset']);v[o:o+3]=translation+np.cross(rotation,[0,0,.020]);v[o+3:o+6]=rotation*.001
  for label,ff in [('contact',contact),('bolts',bolt),('applied',a['applied_force_N']),('elastic',F)]:works.append(dict(motion=j,field=label,work_Nmm=float(v@ff)))
 return dict(relative_force_residual=float(np.linalg.norm(res)/max(np.linalg.norm(a['applied_force_N']),1)),body_residual_N_Nm=w,energy_Nmm=energy,relative_energy_error=abs(energy/s['elastic_energy_Nmm']-1),static_identity_relative=abs(identity)/max(energy+spring,1e-20),bolt_law_error_N=float(np.max(abs(pred-bf))),min_gap_mm=float(g.min()),max_complementarity_Nmm=float(np.max(abs(g*p))),saved_gap_error_mm=float(np.max(abs(g-a['contact_gaps_mm']))),max_vm_error_MPa=max(vmrows),virtual_work=works)
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');rows=[];assert not(ROOT/'runtime/STOP').exists()
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['field']['path']);r=reconstruct(a,s);bad=reconstruct(a,s,True);checks=dict(hashes=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ('field','producer','inputs','candidate')),force=r['relative_force_residual']<1e-8,body_force=all(np.linalg.norm(w[:3])<1e-8 for w in r['body_residual_N_Nm'].values()),body_moment=all(np.linalg.norm(w[3:])<1e-10 for w in r['body_residual_N_Nm'].values()),energy=r['relative_energy_error']<1e-8,static_identity=r['static_identity_relative']<1e-8,bolt_law=r['bolt_law_error_N']<1e-8,gap=r['min_gap_mm']>=-1e-8,complementarity=r['max_complementarity_Nmm']<1e-8,saved_gap=r['saved_gap_error_mm']<1e-12,stress=r['max_vm_error_MPa']<1e-8,rigid_work=max(abs(w['work_Nmm']) for w in r['virtual_work'])<1e-8,corrupt_force_rejected=bad['relative_force_residual']>1e-8,corrupt_energy_rejected=bad['relative_energy_error']>1e-8);rows.append(dict(source=ref(src),reconstruction=r,checks={k:bool(v) for k,v in checks.items()},negative_control=dict(force_residual=bad['relative_force_residual'],energy_error=bad['relative_energy_error'])))
 ok=all(all(r['checks'].values()) for r in rows);dump(out/'summary.json',dict(status='ACTUAL_P1_UPPER_INDEPENDENT_VERIFY_PASS' if ok else 'ACTUAL_P1_UPPER_INDEPENDENT_VERIFY_FAIL',candidate=s['candidate'],verifier=ref(out/'verifier.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=s['limitations']));print(json.dumps(dict(status=ok,checks=[r['checks'] for r in rows])));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
