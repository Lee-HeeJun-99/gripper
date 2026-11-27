"""Normalized-affine feasible primal working-set physical Newton on SAME actual Ritz search space.
No augmented physical stiffness or cone row deletion; every original row limits step.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.linalg import null_space,eigh,lstsq
from baseline_registry import ROOT,REPO,ref,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_conic_ritz_newton1/summary.json';s=json.loads(src.read_text());c=np.load(REPO/s['output']['path']);V=c['V'];H=c['H'];g=c['g'];B=c['B'];x=c['before_x'];A=sparse.load_npz(REPO/s['physical_A']['path']);P=sparse.load_npz(REPO/s['physical_P']['path']);p=np.load(REPO/s['problem']['path']);eq=np.isfinite(p['upper'])&(p['lower']==p['upper']);ine=~eq;sl=A@x-p['lower'];rs=1/np.maximum(np.max(abs(B),axis=1),1e-15);C=rs[:,None]*B;ss=rs*sl;z=np.zeros(V.shape[1]);working=list(np.flatnonzero(eq));history=[];reason='finite working-set limit';dual=np.zeros(len(sl));accepted_count=0
 # Active rows added by original finite-gap blocking. Dependent rows stay in
 # ALL-row acceptance and KKT; null_space is equality SEARCH coordinates only.
 for iteration in range(400):
  if(ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-t>220:reason='220s feasible Ritz internal budget';break
  W=np.array(working,dtype=int);CW=C[W];Z=null_space(CW,rcond=1e-14);grad=H@z+g;Hr=Z.T@H@Z;gr=Z.T@grad
  if Z.shape[1]:
   w,U=eigh(.5*(Hr+Hr.T));cut=max(float(np.max(abs(w)))*1e-13,1e-18);pos=w>cut;ng=U[:,~pos].T@gr
   if np.linalg.norm(ng)>1e-11:d=-Z@(U[:,~pos]@ng);kind='affine_null'
   else:d=-Z@(U[:,pos]@((U[:,pos].T@gr)/w[pos]));kind='range_Newton'
  else:d=np.zeros_like(z);kind='full_working_rank'
  if kind=='affine_null' and np.max(abs(d))>0:
   d*=1e-4/max(float(np.max(abs(V@d))),1e-30)
  if np.max(abs(d))<1e-12:
   yd=lstsq(CW.T,-grad,cond=1e-14)[0];bad=[j for j,row in enumerate(W) if ine[row] and yd[j]>1e-10]
   if bad:j=max(bad,key=lambda j:yd[j]);history.append(dict(iteration=iteration,event='release',row=int(W[j]),search_dual=float(yd[j])));working.pop(j);continue
   dual[:]=0;dual[W]=rs[W]*yd;reason='reduced working stationarity reached';break
  bd=C@d;gap=ss+C@z;mask=ine&(bd<-1e-16);mask[W]=False;ids=np.flatnonzero(mask);alpha=1.;block=None
  if len(ids):
   ratios=np.maximum(gap[ids],0)/(-bd[ids]);k=int(np.argmin(ratios));limit=float(ratios[k]);
   if limit<alpha or kind=='affine_null':alpha=limit;block=int(ids[k])
  elif kind=='affine_null':reason='unblocked reduced affine descent';break
  # exact reduced physical energy line minimization, then original-unit guard.
  gd=float(grad@d);hd=float(d@(H@d));opt=-gd/hd if gd<0 and hd>0 else alpha
  if opt<alpha:alpha=opt;block=None
  proposed=z+alpha*d;full=x+V@proposed;gapfull=A@full-p['lower'];pr=max(float(np.max(np.maximum(-gapfull[ine],0))),float(np.max(abs(gapfull[eq]))));before=float(.5*z@(H@z)+g@z);after=float(.5*proposed@(H@proposed)+g@proposed);accept=pr<1e-10 and gd<0 and after<=before+1e-4*alpha*gd
  history.append(dict(iteration=iteration,event=kind,working_rows=len(W),search_null_dimension=Z.shape[1],alpha=alpha,blocking_row=block,original_primal_mm=pr,directional_work_Nmm=gd,physical_energy_change_Nmm=after-before,accepted=bool(accept)))
  if not accept:reason='original feasibility/Armijo rejected';break
  z=proposed;accepted_count+=1
  if block is not None and block not in working:working.append(block)
  if iteration%10==0:dump(out/'history.json',history)
 W=np.array(working);grad=H@z+g;yd=lstsq(C[W].T,-grad,cond=1e-14)[0];dual[:]=0;dual[W]=rs[W]*yd;new=x+V@z;end=A@new-p['lower'];res=P@new+p['q']+A.T@dual;metrics=dict(primal_mm=max(float(np.max(np.maximum(-end[ine],0))),float(np.max(abs(end[eq])))),stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(dual[eq]))),sign_N=float(np.max(np.maximum(dual[ine],0))),complementarity_Nmm=float(np.max(abs(end[ine]*dual[ine]))),RootY_gamma_stationarity_N=float(abs(dual[2175])),reduced_stationarity=float(np.max(abs(V.T@res))),objective_before_Nmm=float(.5*x@(P@x)+p['q']@x),objective_after_Nmm=float(.5*new@(P@new)+p['q']@new));qualified=all(metrics[k]<1e-8 for k in ['primal_mm','stationarity_N','gauge_N','sign_N','complementarity_Nmm','RootY_gamma_stationarity_N']);np.savez_compressed(out/'feasible.npz',before_x=x,after_x=new,coefficients=z,physical_dual=dual,physical_residual=res,working=W,terminal_search_direction=d,terminal_original_direction=V@d);dump(out/'history.json',history);result=dict(status='ACTUAL_P1_FEASIBLE_RITZ_LINEAR_SEARCH_NOT_EQUILIBRIUM',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],producer=ref(out/'producer.py'),output=ref(out/'feasible.npz'),history=ref(out/'history.json'),reason=reason,metrics=metrics,accepted_linear_steps=accepted_count,physical_KKT_qualified=bool(qualified),actual_support_updates=0,accepted_equilibria=0,physical_regularization=0.,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t,limitations=['Ritz search restriction, not full physical equivalence. Full2208row feasibility/objective guard retained. Equality nullspace/range splits only generate search directions; actual P/q and residuals unchanged.','Working search duals may have wrong signs or large full residual; do not interpret as physical pressures or accept nonlinear update. Original full physical KKT remains mandatory.']);dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
