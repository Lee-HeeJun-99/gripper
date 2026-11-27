"""Fresh tightly solved QP on hashed actual-body elasticity/contact operators.
No force clipping, inequality removal or changed physical data. Old solves preserved.
"""
import sys,json,shutil,copy
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
import osqp
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated'/sys.argv[2];old=json.loads((src/'summary.json').read_text());doc=copy.deepcopy(old)
 for r in [old['inputs'],old['geometry'],old['operators'],*old['fields']]:assert sha(REPO/r['path'])==r['SHA256']
 ops=dict(np.load(REPO/old['operators']['path']));C=ops['C'];Cs=ops['body_compliance'];nc=old['contact_variables'];eq=ops['equality'];spring=ops['spring_mm_N'];scale=np.tile([1,1,1,.01,.01,.01],2);rows=[]
 for prior in old['rows']:
  assert not(ROOT/'runtime/STOP').exists();w=np.array(prior['external_wrench_N_Nmm']);d=Cs[0][:nc,nc:]@w-Cs[1][:nc,nc:]@w;ae=np.array(prior['reduced_equality_matrix']);uu,ss,vv=np.linalg.svd(eq*scale[:,None],full_matrices=False);rank=int(sum(ss>ss[0]*1e-10));be=uu[:,:rank].T@(np.r_[-w,w]*scale);cscale=max(abs(C).max(),1e-12)
  qp=osqp.OSQP();qp.setup(P=sparse.csc_matrix(C/cscale),q=d/cscale,A=sparse.vstack([sparse.csc_matrix(ae),sparse.eye(nc)],format='csc'),l=np.r_[be,np.zeros(nc)],u=np.r_[be,np.full(nc,np.inf)],eps_abs=1e-13,eps_rel=1e-13,max_iter=200000,polishing=True,verbose=False);result=qp.solve();p=result.x;g=C@p+d;active=p>max(p.max()*1e-8,1e-10);gs=max(abs(g).max(),1e-15);at=ae.T;ga=g/gs;dual=linprog(np.r_[np.zeros(rank),1.],A_ub=np.vstack([np.c_[-at,-np.ones(nc)],np.c_[at[active],-np.ones(active.sum())]]),b_ub=np.r_[ga,-ga[active]],bounds=[(None,None)]*rank+[(0,None)],method='highs');assert dual.success;lm=dual.x[:rank]*gs;gap=g+at@lm;energy=[float(np.r_[p,w if k==0 else -w]@Cs[k]@np.r_[p,w if k==0 else -w]) for k in range(2)]
  row=copy.deepcopy(prior);row.pop('full_body_equilibrium',None);row.update(status='CONDITIONAL_VARIATIONAL_SENSITIVITY_ONLY' if result.info.status_val==1 else 'QP_NUMERICAL_FAIL',optimizer_success=result.info.status_val==1,optimizer_message=result.info.status,iterations=int(result.info.iter),dual_feasible=True,dual_residual_mm=float(dual.x[-1]*gs),equality_multiplier=lm.tolist(),contact_gap_mm=gap.tolist(),contact_forces_N=p.tolist(),force_per_tributary_area_MPa_NOT_pressure=None,bolt_tension_N=p[-3:].tolist(),nominal_major_shank_extension_mm=(p[-3:]*spring[-3:]).tolist(),maximum_negative_gap_mm=float(max(0,-gap.min())),active_stationarity_mm=float(abs(gap[active]).max()) if active.any() else 0.,maximum_complementarity_Nmm=float(abs(p*gap).max()),body_strain_work_Nmm=energy,bolt_strain_work_Nmm=float(np.dot(p*p,spring)),total_strain_work_Nmm=float(sum(energy)+np.dot(p*p,spring)),full_equality_residual_N_Nmm=(eq@p-np.r_[-w,w]).tolist(),raw_solver_primal_residual=result.info.prim_res,raw_solver_dual_residual=result.info.dual_res)
  rows.append(row);print(json.dumps(dict(case=row['case'],status=row['optimizer_message'],iterations=row['iterations'],minimum_force=float(p.min()))),flush=True)
 dump(out/'inputs.json',dict(candidate=old['candidate'],producer=ref(out/'producer.py'),parent=ref(src/'summary.json'),parent_inputs=old['inputs'],eps_abs=1e-13,eps_rel=1e-13,max_iter=200000,criteria_unchanged=True,method='Fresh full QP on exact hashed saved actual elasticity/contact operators;retain all inequalities and full original equilibrium rank. No force clipping.'))
 doc.update(rows=rows,inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),parent_conditional_trial=ref(src/'summary.json'),fresh_QP_only=True,all_physical_operators_unchanged=True,force_clipping=False)
 dump(out/'summary.json',doc)
if __name__=='__main__':main()
