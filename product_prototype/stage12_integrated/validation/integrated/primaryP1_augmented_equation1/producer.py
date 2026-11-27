"""Actual P1 rigid/elastic Ritz search: unsquared physical-cone Newton saddle.
Congruence equilibration changes coordinates only. No physical regularization.
"""
import sys,json,time,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import lstsq
from baseline_registry import ROOT,REPO,ref,dump
from primary_ritz_storage import load as load_ritz

def setup():
 src=ROOT/'validation/integrated/primaryP1_ritz_primaldual1/summary.json';s=json.loads(src.read_text());a=np.load(REPO/s['output']['path']);parent=json.loads((REPO/s['source']['path']).read_text());r=load_ritz(parent);V=r['V'];H=r['H'];g=r['g'];B=r['B'];x=a['before_x'];P=sparse.load_npz(REPO/s['physical_P']['path']);A=sparse.load_npz(REPO/s['physical_A']['path']);p=np.load(REPO/s['problem']['path']);eq=np.isfinite(p['upper'])&(p['lower']==p['upper']);ine=~eq;rs=1/np.maximum(np.max(abs(B),axis=1),1e-15);cp=a['equality_particular'];N=a['equality_nullspace'];unit=max(float(np.max(abs(g))),1e-15);HH=N.T@H@N/unit;gg=N.T@(g+H@cp)/unit;F=(rs[ine,None]*B[ine])@N;b=rs[ine]*(A@x-p['lower'])[ine]+(rs[ine,None]*B[ine])@cp;z=N.T@(a['coefficients']-cp);ss=a['interior_slack'];lam=a['interior_lambda'];return locals()

def saddle(H,F,s,l,rd,rp,rc):
 # H dz - F^T dl = -rd; -F dz -diag(s/l)dl = rp+rc/l.
 K=sparse.bmat([[sparse.csc_matrix(H),sparse.csc_matrix(-F.T)],[sparse.csc_matrix(-F),sparse.diags(-s/l)]],format='csc');rhs=np.r_[-rd,rp+rc/l];d=np.ones(K.shape[0]);E=K.copy()
 for _ in range(8):
  mx=np.asarray(abs(E).max(axis=1).toarray()).ravel();v=1/np.sqrt(np.maximum(mx,1e-300));d*=v;E=sparse.diags(v)@E@sparse.diags(v)
 lu=splu(E.tocsc(),permc_spec='COLAMD',diag_pivot_thresh=1.);sol=d*lu.solve(d*rhs);n=len(rd);history=[]
 def residual(w):
  dz=w[:n].astype(np.longdouble);dl=w[n:].astype(np.longdouble)
  return np.r_[-rd.astype(np.longdouble)-H.astype(np.longdouble)@dz+F.T.astype(np.longdouble)@dl,(rp+rc/l).astype(np.longdouble)+F.astype(np.longdouble)@dz+(s/l).astype(np.longdouble)*dl]
 for _ in range(6):
  rr=residual(sol);history.append(float(np.max(abs(rr))));corr=d*lu.solve(d*np.asarray(rr,dtype=float));trial=sol+corr
  if np.max(abs(residual(trial)))>=np.max(abs(rr)):break
  sol=trial
 dz=sol[:n];dl=sol[n:];ds=F@dz+rp
 return dz,ds,dl,dict(refinement_residuals=history,final_augmented_residual=float(np.max(abs(residual(sol)))),matrix_shape=K.shape,equilibration_min=float(d.min()),equilibration_max=float(d.max()))

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();tag=sys.argv[1];mode=sys.argv[2];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');c=setup();locals_=['HH','gg','F','b','z','ss','lam'];HH,gg,F,b,z,ss,lam=[c[k].copy() for k in locals_];hist=[];reason='60 augmented predictor-corrector iteration limit';first=None
 def fraction(v,d,tau):
  m=d<0;return min(1.,tau*float(np.min(-v[m]/d[m]))) if m.any() else 1.
 for it in range(1 if mode=='equation' else 60):
  if(ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-t>240:reason='240s augmented internal budget';break
  rd=HH@z+gg-F.T@lam;rp=F@z+b-ss;mu=float(ss@lam/len(ss));rc=ss*lam
  da,sa,la,diag=saddle(HH,F,ss,lam,rd,rp,rc)
  if first is None:
   np.savez_compressed(out/'equation.npz',H=HH,F=F,g=gg,b=b,z=z,s=ss,l=lam,rd=rd,rp=rp,rc=rc,dz=da,ds=sa,dl=la);first=ref(out/'equation.npz')
  if mode=='equation':hist.append(diag);reason='saved endpoint predictor equation only';break
  ap=fraction(ss,sa,1.);ad=fraction(lam,la,1.);mua=float((ss+ap*sa)@(lam+ad*la)/len(ss));sigma=np.clip((mua/mu)**3,0.,1.);dz,ds,dl,diag=saddle(HH,F,ss,lam,rd,rp,ss*lam+sa*la-sigma*mu);ap=fraction(ss,ds,.995);ad=fraction(lam,dl,.995);hist.append(dict(iteration=it,primal_scaled=float(np.max(abs(rp))),dual_scaled=float(np.max(abs(rd))),mu=mu,primal_alpha=ap,dual_alpha=ad,**diag));z+=ap*dz;ss+=ap*ds;lam+=ad*dl;dump(out/'history.json',hist)
  if not(np.all(np.isfinite(z)) and np.all(np.isfinite(lam)) and np.min(ss)>0 and np.min(lam)>0):reason='nonfinite/nonpositive rejected';break
  if max(float(np.max(abs(rd))),float(np.max(abs(rp))),mu)<1e-11:reason='reduced residual stop';break
 coeff=c['cp']+c['N']@z;dx=c['V']@coeff;proposal=c['x']+dx;A=c['A'];P=c['P'];p=c['p'];eq=c['eq'];ine=c['ine'];end=A@proposal-p['lower'];y=np.zeros(len(end));y[ine]=-c['unit']*c['rs'][ine]*lam;y[eq]=lstsq(c['B'][eq].T,-(c['H']@coeff+c['g']+c['B'][ine].T@y[ine]),cond=1e-14)[0];res=P@proposal+p['q']+A.T@y;obj=lambda w:float(.5*w@(P@w)+p['q']@w);pr=max(float(np.max(np.maximum(-end[ine],0))),float(np.max(abs(end[eq]))));gt=float((P@c['x']+p['q'])@dx);accepted=bool(mode!='equation' and pr<1e-10 and gt<0 and obj(proposal)<=obj(c['x'])+1e-4*gt);metrics=dict(primal_mm=pr,stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])),sign_N=float(np.max(np.maximum(y[ine],0))),complementarity_Nmm=float(np.max(abs(end[ine]*y[ine]))),reduced_stationarity=float(np.max(abs(c['V'].T@res))),objective_before_Nmm=obj(c['x']),objective_proposal_Nmm=obj(proposal));qualified=accepted and all(metrics[k]<1e-8 for k in ['stationarity_N','gauge_N','RootY_gamma_stationarity_N','sign_N','complementarity_Nmm']);np.savez_compressed(out/'proposal.npz',coefficients=coeff,proposed_x=proposal,physical_dual=y,physical_residual=res,interior_slack=ss,interior_lambda=lam);dump(out/'history.json',hist);result=dict(status='ACTUAL_P1_AUGMENTED_EQUATION_RECORDED' if mode=='equation' else 'ACTUAL_P1_AUGMENTED_LINEAR_SEARCH_NOT_EQUILIBRIUM',candidate=c['s']['candidate'],source=ref(c['src']),source_field=c['s']['source_field'],physical_P=c['s']['physical_P'],physical_A=c['s']['physical_A'],problem=c['s']['problem'],producer=ref(out/'producer.py'),equation=first,output=ref(out/'proposal.npz'),history=ref(out/'history.json'),reason=reason,metrics=metrics,physical_KKT_qualified=bool(qualified),accepted_linear_steps=int(accepted),actual_support_updates=0,accepted_equilibria=0,physical_regularization=0.,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t,mode=mode);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if mode=='equation' or accepted else 2)
if __name__=='__main__':main()
