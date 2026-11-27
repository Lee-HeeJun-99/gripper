"""Actual P1 extended first-order continuation; original physical operators unchanged."""
import sys,time,json,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.linalg import lstsq
from baseline_registry import ROOT,REPO,ref,dump
from primary_augmented_saddle import setup
from primary_certified_centrality import errors,frac

def direction(H,F,sl,lam,rd,rp,rc):
 n,m=H.shape[0],len(sl)
 K=sparse.bmat([[sparse.csc_matrix(H),None,sparse.csc_matrix(-F.T)],[sparse.csc_matrix(F),-sparse.eye(m),None],[None,sparse.diags(np.asarray(lam,dtype=float)),sparse.diags(np.asarray(sl,dtype=float))]],format='csc');rhs=np.asarray(np.r_[-rd,-rp,-rc],dtype=float);left=np.ones(len(rhs));right=left.copy();M=K.copy()
 for i in range(10):
  row=np.asarray(abs(M).max(axis=1).toarray()).ravel();rr=1/np.sqrt(np.maximum(row,1e-300));left*=rr;M=sparse.diags(rr)@M;col=np.asarray(abs(M).max(axis=0).toarray()).ravel();cc=1/np.sqrt(np.maximum(col,1e-300));right*=cc;M=M@sparse.diags(cc)
 lu=splu(M.tocsc(),permc_spec='COLAMD',diag_pivot_thresh=1.);sol=(right*lu.solve(left*rhs)).astype(np.longdouble)
 def residual(w):
  dz,ds,dl=w[:n].astype(np.longdouble),w[n:n+m].astype(np.longdouble),w[n+m:].astype(np.longdouble)
  return np.r_[-rd.astype(np.longdouble)-H.astype(np.longdouble)@dz+F.T.astype(np.longdouble)@dl,-rp.astype(np.longdouble)-F.astype(np.longdouble)@dz+ds,-rc.astype(np.longdouble)-lam.astype(np.longdouble)*ds-sl.astype(np.longdouble)*dl]
 history=[]
 for i in range(12):
  rr=residual(sol);history.append(float(np.max(abs(rr))));trial=sol+right*lu.solve(left*np.asarray(rr,dtype=float))
  if np.max(abs(residual(trial)))>=np.max(abs(rr)):break
  sol=trial
 return sol[:n],sol[n:n+m],sol[n+m:]

def pair(H,F,g,b,z,s,l):
 rd=H.astype(np.longdouble)@z+g-F.T.astype(np.longdouble)@l;rp=F.astype(np.longdouble)@z+b-s;rc=s*l
 da,sa,la=direction(H,F,s,l,rd,rp,rc);ea=errors(H,F,s,l,rd,rp,rc,da,sa,la)
 mu=np.mean(rc);mua=np.mean((s+frac(s,sa)*sa)*(l+frac(l,la)*la));sigma=np.clip((mua/mu)**3,0,1);rcc=rc+sa*la-sigma*mu
 dz,ds,dl=direction(H,F,s,l,rd,rp,rcc);ec=errors(H,F,s,l,rd,rp,rcc,dz,ds,dl)
 return dict(z=z,s=s,l=l,rd=rd,rp=rp,rc_predictor=rc,rc_corrector=rcc,predictor_dz=da,predictor_ds=sa,predictor_dl=la,dz=dz,ds=ds,dl=dl,sigma=sigma),ea,ec

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_certified_centrality1/summary.json';sour=json.loads(src.read_text());r=np.load(REPO/sour['reduced']['path']);e=np.load(src.parent/'direction19.npz');H,F,g,b=[r[k] for k in ['H','F','g','b']];z,s,l=[e[k].astype(np.longdouble) for k in ['z','s','l']]
 if sys.argv[2]=='prepare':
  a,ea,ec=pair(H,F,g,b,z,s,l);np.savez_compressed(out/'pair.npz',**a);dump(out/'summary.json',dict(status='ACTUAL_P1_EXTENDED_PAIR',candidate=sour['candidate'],source=ref(src),reduced=sour['reduced'],output=ref(out/'pair.npz'),predictor_errors=ea,corrector_errors=ec,certified=max(ea+ec)<1e-8,actual_iterate_updates=0));return
 audit=json.loads((ROOT/'validation/integrated/primaryP1_extended_pair_audit1/summary.json').read_text());assert all(audit['checks'].values())
 hist=[];reason='40 extended iteration limit';steps=0
 for it in range(40):
  if (ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-start>240:reason='240s internal budget';break
  a,ea,ec=pair(H,F,g,b,z,s,l);cert=max(ea+ec)<1e-8;alpha=min(frac(s,a['ds'],.995),frac(l,a['dl'],.995));merit=max(float(np.max(abs(a['rd']))),float(np.max(abs(a['rp']))),float(np.mean(s*l)));accepted=False;after=None
  if cert:
   for bt in range(30):
    zz=z+alpha*a['dz'];ss=s+alpha*a['ds'];ll=l+alpha*a['dl'];after=max(float(np.max(abs(H.astype(np.longdouble)@zz+g-F.T.astype(np.longdouble)@ll))),float(np.max(abs(F.astype(np.longdouble)@zz+b-ss))),float(np.mean(ss*ll)))
    if min(ss.min(),ll.min())>0 and after<=(1-1e-4*alpha)*merit:accepted=True;break
    alpha*=.5
  np.savez_compressed(out/('pair%02d.npz'%it),**a,alpha=alpha,accepted=accepted);hist.append(dict(iteration=it,predictor_errors=ea,corrector_errors=ec,certified=cert,alpha=alpha,merit=merit,merit_after=after,accepted=accepted));dump(out/'history.json',hist)
  if not cert:reason='uncertified extended pair rejected';break
  if not accepted:reason='merit guard rejected';break
  z,s,l=zz,ss,ll;steps+=1
  if after<1e-11:reason='reduced residual stop; physical audit required';break
 c=setup();v=r['probe'];V=np.column_stack([c['V'],v]);P,A,p,x=c['P'],c['A'],c['p'],c['x'];eq,ine=c['eq'],c['ine'];B=A@V;fullH=V.T@(P@V);gphys=V.T@(P@x+p['q']);cp,N,rs,unit=[r[k] for k in ['cp','N','rs','unit']]
 coeff=cp+N@z;proposal=x+V@coeff;y=np.zeros(A.shape[0],dtype=np.longdouble);y[ine]=-unit*rs[ine]*l;y[eq]=lstsq(B[eq].T,np.asarray(-(fullH@coeff+gphys+B[ine].T@y[ine]),dtype=float),cond=1e-14)[0];res=P@proposal+p['q']+A.T@y;sl=A@proposal-p['lower'];obj=lambda w:float(.5*w@(P@w)+p['q']@w);gt=float((P@x+p['q'])@(proposal-x));pr=max(float(np.max(np.maximum(-sl[ine],0))),float(np.max(abs(sl[eq]))));accepted=bool(pr<1e-10 and gt<0 and obj(proposal)<=obj(x)+1e-4*gt)
 m=dict(primal_mm=pr,stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])),sign_N=float(np.max(np.maximum(y[ine],0))),complementarity_Nmm=float(np.max(abs(sl[ine]*y[ine]))),objective_before_Nmm=obj(x),objective_proposal_Nmm=obj(proposal),reduced_stationarity=float(np.max(abs(V.T@res))))
 scaled=np.asarray(res*c['scale'] if 'scale' in c else res,dtype=float);W=np.asarray(V,dtype=float);proj=W@lstsq(W,scaled,cond=1e-14)[0];m['full_residual_l2_N']=float(np.linalg.norm(scaled));m['orthogonal_residual_l2_N']=float(np.linalg.norm(scaled-proj))
 np.savez_compressed(out/'endpoint.npz',z=z,s=s,l=l,coefficients=coeff,proposed_x=proposal,physical_dual=y,physical_residual=res)
 dump(out/'summary.json',dict(status='ACTUAL_P1_EXTENDED_CONTINUATION_PHYSICAL_AUDIT',candidate=sour['candidate'],source=ref(src),reduced=sour['reduced'],source_field=sour['source_field'],output=ref(out/'endpoint.npz'),precontinuation_audit=ref(ROOT/'validation/integrated/primaryP1_extended_pair_audit1/summary.json'),history=ref(out/'history.json'),metrics=m,reason=reason,certified_algorithmic_steps=steps,endpoint_finitegap_armijo_accepted=accepted,physical_KKT_qualified=bool(accepted and all(m[k]<1e-8 for k in ['stationarity_N','gauge_N','RootY_gamma_stationarity_N','sign_N','complementarity_Nmm'])),actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start));print(json.dumps(m))
if __name__=='__main__':main()
