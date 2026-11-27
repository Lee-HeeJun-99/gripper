"""Independent direct affine-tetra force/energy verifier; never imports solver/kernel."""
import json,shutil,sys
import numpy as np
from scipy import sparse
from baseline_registry import ROOT,REPO,ref,sha,dump

def reconstruct(a,summary,perturb=False):
 u=a['u_mm'].copy();ng=int(a['G_ndof']);F=np.zeros_like(u);energy=0;rows=[]
 if perturb:u[np.argmax(abs(u))]+=1e-5
 for name,off,E,nu in [('G',0,200000,.3),('B',ng,68900,.33)]:
  p=a[name+'_points_mm'];t=a[name+'_tetra'];uu=u[off:off+3*len(p)].reshape(-1,3);dx=p[t[:,1:]]-p[t[:,0,None]];du=uu[t[:,1:]]-uu[t[:,0,None]];grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu));stress=2*mu*eps+lam*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);vol=abs(np.linalg.det(dx))/6
  gradN=np.empty((len(t),4,3));gradN[:,1:,:]=np.linalg.inv(dx).transpose(0,2,1);gradN[:,0,:]=-gradN[:,1:,:].sum(axis=1);fe=np.einsum('eij,ekj,e->eki',stress,gradN,vol)
  for j in range(4):
   for k in range(3):np.add.at(F,off+3*t[:,j]+k,fe[:,j,k])
  en=float(np.sum(.5*np.einsum('eij,eij->e',eps,stress)*vol));energy+=en;rows.append(dict(body=name,energy_Nmm=en,mesh_volume_mm3=float(vol.sum())))
 C=sparse.csr_matrix((a['contact_C_data'],a['contact_C_indices'],a['contact_C_indptr']),shape=tuple(a['contact_C_shape']));D=a['bolt_D'];lam=a['contact_dual_N'];res=F-a['applied_force_N']-C.T@lam+D.T@a['bolt_force_N'];gap=C@u+a['initial_gaps_mm'];k=summary['bolt_k_N_mm'];pre=summary['preload_each_N'];pred=np.maximum(k*(D@u)+pre,0);enbolt=.5*float(np.sum(a['bolt_force_N']**2/k));identity=2*(energy+enbolt)-float(a['applied_force_N']@u)-float(pre/k*np.sum(a['bolt_force_N']))+float(lam@a['initial_gaps_mm']);W=np.zeros(6)
 for name,off in [('G',0),('B',ng)]:
  p=a[name+'_points_mm'];ff=a['applied_force_N'][off:off+3*len(p)].reshape(-1,3);W[:3]+=ff.sum(axis=0);W[3:]+=np.cross(p*.001,ff).sum(axis=0)
 return dict(relative_force_residual=float(np.linalg.norm(res)/max(np.linalg.norm(a['applied_force_N']),1)),max_bolt_law_error_N=float(np.max(abs(pred-a['bolt_force_N']))),energy_Nmm=energy,relative_energy_error=abs(energy/summary['elastic_energy_Nmm']-1),static_identity_relative=abs(identity)/max(abs(energy+enbolt),1e-20),min_gap_mm=float(gap.min()),max_complementarity_Nmm=float(np.max(abs(gap*lam))),external_wrench_N_Nm=W.tolist(),saved_gap_error_mm=float(np.max(abs(gap-a['contact_gaps_mm']))),rows=rows)

def main():
 tags=sys.argv[2:];out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();rows=[]
 for tag in tags:
  src=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['field']['path']);r=reconstruct(a,s);bad=reconstruct(a,s,True);checks=dict(hashes=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ('field','producer','inputs','candidate')),independent_force=r['relative_force_residual']<1e-8,independent_energy=r['relative_energy_error']<1e-8,independent_static_identity=r['static_identity_relative']<1e-8,bolt_law=r['max_bolt_law_error_N']<1e-8,normal_gap=r['min_gap_mm']>=-1e-8,complementarity=r['max_complementarity_Nmm']<1e-8,external_force=np.linalg.norm(r['external_wrench_N_Nm'][:3])<1e-8,external_moment=np.linalg.norm(r['external_wrench_N_Nm'][3:])<1e-10,perturbed_force_rejected=bad['relative_force_residual']>1e-8,perturbed_energy_rejected=bad['relative_energy_error']>1e-8);rows.append(dict(source=ref(src),reconstruction=r,checks={k:bool(v) for k,v in checks.items()}))
 nominal=[json.loads((ROOT/'validation/integrated'/t/'summary.json').read_text()) for t in tags[:3]];mesh=[]
 for lo,hi in zip(nominal[:-1],nominal[1:]):
  values={}
  for j in range(2):
   for k in ('peak_unsmoothed_vm_MPa','max_motion_mm'):values[lo['stresses'][j]['part']+'_'+k]=abs(lo['stresses'][j][k]/hi['stresses'][j][k]-1)
  values['elastic_energy']=abs(lo['elastic_energy_Nmm']/hi['elastic_energy_Nmm']-1);values['bolt_force_max']=float(np.max(abs(np.array(lo['bolt_force_N'])/hi['bolt_force_N']-1)));mesh.append(dict(h_pair=[lo['h_mm'],hi['h_mm']],relative=values,pass_1pct=max(values.values())<=.01))
 ok=all(all(r['checks'].values()) for r in rows);dump(out/'summary.json',dict(status='ACTUAL_P1_COMPLIANT_STATES_INDEPENDENTLY_VERIFIED' if ok else 'ACTUAL_P1_COMPLIANT_STATE_VERIFICATION_FAIL',candidate=s['candidate'],verifier=ref(out/'verifier.py'),rows=rows,mesh=mesh,mesh_1pct_pass=all(m['pass_1pct'] for m in mesh),newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Independent saved-state direct tetra forces/energy/bolt law/contact gaps and perturbation controls. Does not qualify source minimum,physical anchor,averaged connector or sharp stress singularity.'));print(json.dumps(dict(verified=ok,checks=[r['checks'] for r in rows],mesh=mesh)));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
