"""Original physical P/q conic primal-dual Newton in actual P1 Ritz search.
Mehrotra predictor/corrector, finite gaps and every original cone retained.
Equality coordinates are audited, not a signed replacement for inequalities.
"""
import sys,json,time,shutil,warnings
import numpy as np
from scipy import sparse
from scipy.linalg import null_space,lstsq,solve
from primary_ritz_storage import load as load_ritz
from baseline_registry import ROOT,REPO,ref,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_conic_ritz_newton1/summary.json';s=json.loads(src.read_text());r=load_ritz(s);V=r['V'];H=r['H'];g=r['g'];B=r['B'];x=r['before_x'];A=sparse.load_npz(REPO/s['physical_A']['path']);P=sparse.load_npz(REPO/s['physical_P']['path']);p=np.load(REPO/s['problem']['path']);sl=A@x-p['lower'];eq=np.isfinite(p['upper'])&(p['lower']==p['upper']);ine=~eq;rs=1/np.maximum(np.max(abs(B),axis=1),1e-15);C=rs[:,None]*B;Ce=C[eq];cp=lstsq(Ce,-rs[eq]*sl[eq],cond=1e-14)[0];N=null_space(Ce,rcond=1e-14);assert np.max(abs((Ce@cp+rs[eq]*sl[eq])/rs[eq]))<1e-10;assert np.max(abs(Ce@N))<1e-10;unit=max(float(np.max(abs(g))),1e-15);HH=N.T@H@N/unit;gg=N.T@(g+H@cp)/unit;F=C[ine]@N;b=rs[ine]*sl[ine]+C[ine]@cp;z=np.zeros(N.shape[1]);ss=np.maximum(abs(b),1e-4);lam=np.ones(len(b));hist=[];reason='80 predictor-corrector iteration limit';warn=[]
 def fraction(v,d,tau):
  mask=d<0
  return min(1.,tau*float(np.min(-v[mask]/d[mask]))) if np.any(mask) else 1.
 for it in range(80):
  if(ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-t>180:reason='180s primaldual internal budget';break
  rd=HH@z+gg-F.T@lam;rp=F@z+b-ss;mu=float(ss@lam/len(b));K=HH+F.T@((lam/ss)[:,None]*F)
  def direction(rc):
   rhs=-rd-F.T@((rc+lam*rp)/ss)
   with warnings.catch_warnings(record=True) as ws:
    warnings.simplefilter('always');dz=solve(K,rhs,assume_a='sym');warn.extend(str(w.message) for w in ws)
   ds=F@dz+rp;dl=(-rc-lam*ds)/ss;return dz,ds,dl
  try:
   da,sa,la=direction(ss*lam);ap=fraction(ss,sa,1.);ad=fraction(lam,la,1.);mua=float((ss+ap*sa)@(lam+ad*la)/len(b));sigma=min(1.,max(0.,(mua/mu)**3));dz,ds,dl=direction(ss*lam+sa*la-sigma*mu);ap=fraction(ss,ds,.995);ad=fraction(lam,dl,.995)
  except (np.linalg.LinAlgError,ValueError,FloatingPointError) as e:reason='unregularized Newton factorization rejected: '+str(e);break
  lin=float(np.max(abs(K@dz-(-rd-F.T@((ss*lam+sa*la-sigma*mu+lam*rp)/ss)))));hist.append(dict(iteration=it,primal_scaled=float(np.max(abs(rp))),dual_scaled=float(np.max(abs(rd))),mu=mu,primal_alpha=ap,dual_alpha=ad,linear_residual=lin));z+=ap*dz;ss+=ap*ds;lam+=ad*dl
  if not(np.all(np.isfinite(z)) and np.all(np.isfinite(lam)) and np.min(ss)>0 and np.min(lam)>0):reason='nonfinite or nonpositive interior state rejected';break
  if max(float(np.max(abs(rd))),float(np.max(abs(rp))),mu)<1e-11:reason='reduced primal-dual residual stop';break
  dump(out/'history.json',hist)
 coeff=cp+N@z;dx=V@coeff;proposal=x+dx;end=A@proposal-p['lower'];y=np.zeros(len(sl));y[ine]=-unit*rs[ine]*lam;yy=lstsq(B[eq].T,-(H@coeff+g+B[ine].T@y[ine]),cond=1e-14)[0];y[eq]=yy;res=P@proposal+p['q']+A.T@y;obj=lambda w:float(.5*w@(P@w)+p['q']@w);pr=max(float(np.max(np.maximum(-end[ine],0))),float(np.max(abs(end[eq]))));gt=float((P@x+p['q'])@dx);accepted=bool(np.all(np.isfinite(proposal)) and pr<1e-10 and gt<0 and obj(proposal)<=obj(x)+1e-4*gt);metrics=dict(primal_mm=pr,stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])),sign_N=float(np.max(np.maximum(y[ine],0))),complementarity_Nmm=float(np.max(abs(end[ine]*y[ine]))),reduced_stationarity=float(np.max(abs(V.T@res))),objective_before_Nmm=obj(x),objective_proposal_Nmm=obj(proposal));qualified=accepted and all(metrics[k]<1e-8 for k in ['stationarity_N','gauge_N','RootY_gamma_stationarity_N','sign_N','complementarity_Nmm']);np.savez_compressed(out/'primal_dual.npz',before_x=x,coefficients=coeff,direction=dx,proposed_x=proposal,after_x=proposal if accepted else x,physical_dual=y,physical_residual=res,interior_slack=ss,interior_lambda=lam,equality_particular=cp,equality_nullspace=N);dump(out/'history.json',hist);result=dict(status='ACTUAL_P1_RITZ_PRIMAL_DUAL_LINEAR_STEP_NOT_EQUILIBRIUM' if accepted else 'ACTUAL_P1_RITZ_PRIMAL_DUAL_REJECTED',candidate=s['candidate'],source=ref(src),source_field=s['source_field'],physical_P=s['physical_P'],physical_A=s['physical_A'],problem=s['problem'],producer=ref(out/'producer.py'),output=ref(out/'primal_dual.npz'),history=ref(out/'history.json'),reason=reason,numerical_factorization_warnings=warn,metrics=metrics,physical_KKT_qualified=bool(qualified),accepted_linear_steps=int(accepted),actual_support_updates=0,accepted_equilibria=0,physical_regularization=0.,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t,limitations=['All original finite gaps and physical cone duals retained in predictor-corrector equations. Barrier/search iterates may be infeasible; only original-unit acceptance can advance a linear seed. No physical penalty/shift/eigen clipping.','Ritz restriction is SEARCH only; physical full-space/gauges/nonlinear/source/mesh/material conditions remain mandatory. Numeric saddle conditioning and absent strict interior can reject the method; failure is not a design impossibility proof.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if accepted else 2)
if __name__=='__main__':main()
