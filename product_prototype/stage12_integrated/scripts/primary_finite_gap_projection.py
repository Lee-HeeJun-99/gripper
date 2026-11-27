"""Actual P1 finite-gap projection of an audited feasible descent ray.
Search metric projection only. ALL original physical rows decide acceptance.
No physical regularization/fixation or nonlinear support update.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.optimize import minimize
import pyamg
from baseline_registry import ROOT,REPO,ref,dump

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_freeY_corrected1/summary.json';s=json.loads(src.read_text());audit=json.loads((ROOT/'validation/integrated/primaryP1_freeY_audit_corrected1/summary.json').read_text());assert all(audit['checks'].values());c=np.load(REPO/s['output']['path']);x=c['before_x'].copy();desired=c['direction_physical'].copy();P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);a=np.load(REPO/s['source_field']['path']);q=p['q'];lo=p['lower'];hi=p['upper'];D=p['D'].copy();E=p['E'];D[-1]=s['direction_scaling_gamma'];n=len(D);N=n-15;eq=np.isfinite(hi)&(lo==hi);ineq=~eq;ee=np.flatnonzero(eq);Ps=(sparse.diags(D)@P@sparse.diags(D)).tocsr();As=(sparse.diags(E)@A@sparse.diags(D)).tocsr();sl=A@x-lo;d0=desired/D
 local=json.loads((ROOT/'validation/integrated/primaryP1_local_surface2/summary.json').read_text());diag=Ps.diagonal();Pr=Ps+sparse.diags(1e-6*np.maximum(diag,1.));modes=[]
 for name in local['elastic_bodies']:
  X=a[name+'_points_mm'];o=int(a[name+'_offset']);Xc=X-X.mean(axis=0)
  for j in range(6):
   v=np.zeros_like(X)
   if j<3:v[:,j]=1
   else:v=np.cross(np.eye(3)[j-3],Xc)
   z=np.zeros(n);z[o:o+3*len(X)]=v.ravel();modes.append(z/D)
 for j in list(range(N-6,N))+[n-1]:z=np.zeros(n);z[j]=1/D[j];modes.append(z)
 B=np.column_stack(modes);B/=np.maximum(np.linalg.norm(B,axis=0),1e-30);ml=pyamg.smoothed_aggregation_solver(Pr,B=B,symmetry='symmetric',max_levels=10,max_coarse=120,presmoother=('gauss_seidel',{'sweep':'symmetric'}),postsmoother=('gauss_seidel',{'sweep':'symmetric'}),coarse_solver='pinv');M=ml.aspreconditioner(cycle='V');cache={};active=np.union1d(ee,np.flatnonzero(ineq&((sl+A@desired<-1e-12)|(sl<1e-12))));history=[];accepted=False;reason='finite4 batch generation limit';last=None
 class Budget(Exception):pass
 def budget():
  if(ROOT/'runtime/STOP').exists():raise Budget('STOP')
  if time.monotonic()-start>300:raise Budget('300s finiteprojection internal budget')
 try:
  for k in range(4):
   budget();Ar=As[active]
   for row in active:
    budget()
    if int(row) not in cache:cache[int(row)]=M@As.getrow(row).toarray().ravel()
   V=np.column_stack([cache[int(row)] for row in active]);actual_S=np.asarray(Ar@V);S=.5*(actual_S+actual_S.T);rs=1/np.sqrt(np.maximum(np.diag(S),1e-30));Sn=rs[:,None]*S*rs[None,:];h=rs*(Ar@d0+E[active]*sl[active]);unit=max(float(np.max(abs(h))),1e-15);hn=h/unit
   def fun(y):return float(.5*y@(Sn@y)-hn@y)
   def jac(y):budget();return Sn@y-hn
   bounds=[(None,0.) if ineq[row] else (None,None) for row in active];r=minimize(fun,np.zeros(len(active)),jac=jac,bounds=bounds,method='SLSQP',options=dict(maxiter=200,ftol=1e-14,disp=False));yy=rs*unit*r.x;direction=d0-V@yy;dx=D*direction;end_sl=A@(x+dx)-lo;finitepr=max(float(np.max(np.maximum(-end_sl[ineq],0))),float(np.max(abs(end_sl[eq]))));ys=np.zeros(len(lo));ys[active]=yy;dual=E*ys;searchsign=float(np.max(np.maximum(dual[ineq],0)));searchcomp=float(np.max(abs(end_sl[ineq]*dual[ineq])));gt=float((P@x+q)@dx);curv=float(dx@(P@dx));alpha=min(1.,-gt/curv) if gt<0 and curv>0 else 1.;before=float(.5*x@(P@x)+q@x);new=x+alpha*dx;newsl=A@new-lo;after=float(.5*new@(P@new)+q@new);newpr=max(float(np.max(np.maximum(-newsl[ineq],0))),float(np.max(abs(newsl[eq]))));accepted=finitepr<1e-10 and searchsign<1e-8 and searchcomp<1e-8 and gt<0 and newpr<1e-10 and after<=before+1e-4*alpha*gt;violated=np.flatnonzero(ineq&(end_sl<-1e-10));newrows=np.setdiff1d(violated,active);last=out/f'batch{k}.npz';np.savez_compressed(last,before_x=x,desired_direction=desired,direction_physical=dx,after_x=new if accepted else x,projection_dual=dual,endpoint_slack_mm=end_sl,after_slack_mm=newsl if accepted else sl,active=active,small_S=Sn,small_h=hn,small_y=r.x,small_row_scale=rs,small_unit=unit,actual_S_asymmetry=actual_S-actual_S.T)
   row=dict(batch=k,active_original_rows=active.tolist(),active_rows=len(active),SLSQP_status=int(r.status),SLSQP_message=r.message,SLSQP_iterations=int(r.nit),maximum_S_asymmetry=float(np.max(abs(actual_S-actual_S.T))),finite_endpoint_primal_mm=finitepr,projection_dual_sign_N=searchsign,projection_complementarity_Nmm=searchcomp,physical_directional_objective_Nmm=gt,physical_curvature_Nmm=curv,accepted_alpha=alpha,physical_objective_before_Nmm=before,physical_objective_after_Nmm=after if accepted else before,after_physical_primal_mm=newpr if accepted else max(float(np.max(np.maximum(-sl[ineq],0))),float(np.max(abs(sl[eq])))),accepted_linear_step=bool(accepted),violated_original_rows=violated.tolist(),batch_add_original_rows=newrows.tolist(),output=ref(last),elapsed_s=time.monotonic()-start);history.append(row);dump(out/'history.json',history)
   if accepted:reason='finite-gap projected physical-objective descent accepted; NOT equilibrium';break
   if not len(newrows):reason='all generated original rows present but finite projection/KKT/Armijo failed';break
   active=np.union1d(active,newrows)
 except Budget as e:reason=str(e)
 result=dict(status='ACTUAL_P1_FINITE_GAP_PROJECTED_STEP_ACCEPTED_NOT_EQUILIBRIUM' if accepted else 'ACTUAL_P1_FINITE_GAP_PROJECTION_REJECTED',candidate=s['candidate'],source_field=s['source_field'],source=ref(src),source_ray=s['output'],source_audit=ref(ROOT/'validation/integrated/primaryP1_freeY_audit_corrected1/summary.json'),producer=ref(out/'producer.py'),physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],batches=history,history=ref(out/'history.json') if history else None,output=ref(last) if last else None,accepted_linear_steps=int(accepted),reason=reason,all_original_inequalities_retained=True,physical_regularization=0.,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Finite-gap search-metric projection changes numerical direction only. Its multipliers are NOT physical equilibrium pressures. Final physical P/q objective and every original gap/gauge/sign/complementarity are independently checked.','Original-source linear trial, not updated attached-load nonlinear equilibrium. No stress/strength/globalenergy or whole-system qualification. All2169contacts/14branches/original MotorY/other gauges retained; RootY gamma unpenalized in physical P/q.','At most4 finite-gap batch generations/300s, not a repeated separator release/equality scan or solver-budget extension. No dropped physical row/physical spring/new gap.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if accepted else 2)
if __name__=='__main__':main()
