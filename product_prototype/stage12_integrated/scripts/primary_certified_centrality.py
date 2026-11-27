"""P1 actual support: certified first-order directions and one elastic enrichment.
Algorithmic infeasible interior start is not physical contact penetration acceptance.
"""
import sys,time,json,shutil
import numpy as np
from scipy.linalg import null_space,lstsq
from baseline_registry import ROOT,REPO,ref,dump
from primary_augmented_saddle import setup,saddle

def errors(H,F,s,l,rd,rp,rc,dz,ds,dl):
 H,F,s,l,rd,rp,rc,dz,ds,dl=[np.asarray(v,dtype=np.longdouble) for v in (H,F,s,l,rd,rp,rc,dz,ds,dl)]
 return [float(np.max(abs(v))) for v in (H@dz-F.T@dl+rd,F@dz-ds+rp,l*ds+s*dl+rc)]
def frac(v,d,tau=1.):
 m=d<0
 return min(1.,tau*float(np.min(-v[m]/d[m]))) if m.any() else 1.
def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');c=setup()
 # Reconstruct actual archived FIRST corrector, not just the endpoint predictor.
 H,F,z,s,l=[c[k].copy() for k in ['HH','F','z','ss','lam']];rd=H@z+c['gg']-F.T@l;rp=F@z+c['b']-s;rc=s*l
 da,sa,la,_=saddle(H,F,s,l,rd,rp,rc);mu=float(s@l/len(s));mua=float((s+frac(s,sa)*sa)@(l+frac(l,la)*la)/len(s));sigma=float(np.clip((mua/mu)**3,0,1));rcc=s*l+sa*la-sigma*mu;dz,ds,dl,_=saddle(H,F,s,l,rd,rp,rcc)
 np.savez_compressed(out/'archived_first_corrector.npz',H=H,F=F,s=s,l=l,z=z,g=c['gg'],b=c['b'],rd=rd,rp=rp,rc=rcc,predictor_dz=da,predictor_ds=sa,predictor_dl=la,dz=dz,ds=ds,dl=dl,sigma=sigma)
 archived=dict(predictor_errors=errors(H,F,s,l,rd,rp,rc,da,sa,la),corrector_errors=errors(H,F,s,l,rd,rp,rcc,dz,ds,dl));archived['corrector_certified']=max(archived['corrector_errors'])<1e-8
 # Append the previously measured orthogonal physical elastic vector; no physical P change.
 partsrc=ROOT/'validation/integrated/primaryP1_saddle_partition1/summary.json';part=json.loads(partsrc.read_text());probe=np.load(REPO/part['output']['path']);v=probe['physical_probe'];V=np.column_stack([c['V'],v]);P,A,p,x=c['P'],c['A'],c['p'],c['x'];B=A@V;fullH=V.T@(P@V);g=V.T@(P@x+p['q']);eq,ine=c['eq'],c['ine'];E=B[eq];rhs=(p['lower']-A@x)[eq];cp=lstsq(E,rhs,cond=1e-14)[0];N=null_space(E,rcond=1e-14);unit=max(float(np.max(abs(g))),1e-15);rs=1/np.maximum(np.max(abs(B),axis=1),1e-15);H=N.T@fullH@N/unit;gg=N.T@(g+fullH@cp)/unit;F=(rs[ine,None]*B[ine])@N;b=rs[ine]*((A@x-p['lower'])[ine]+B[ine]@cp)
 old=c['a']['coefficients'];coeff0=np.r_[old,0.];z=N.T@(coeff0-cp)
 # Infeasible-start interior point: choose positive algorithmic s,l with uniform product.
 # Actual constraints remain Fz+b; rp explicitly retains mismatch.
 floor=max(1e-3,float(np.max(abs(F@z+b)))*.01);s=np.maximum(F@z+b,floor);mu0=max(1e-3,float(np.max(abs(H@z+gg))));l=mu0/s
 np.savez_compressed(out/'reduced.npz',H=H,F=F,g=gg,b=b,cp=cp,N=N,rs=rs,unit=unit,z0=z,s0=s,l0=l,probe=v)
 hist=[];reason='60 certified centrality iteration limit';cert_steps=0
 for it in range(60):
  if (ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-start>240:reason='240s budget';break
  rd=H@z+gg-F.T@l;rp=F@z+b-s;mu=float(s@l/len(s));rc=s*l
  da,sa,la,diagA=saddle(H,F,s,l,rd,rp,rc);ea=errors(H,F,s,l,rd,rp,rc,da,sa,la)
  sigma=0.;rcc=rc.copy();dz=da;ds=sa;dl=la;ec=ea;diagC={}
  if max(ea)<1e-8:
   mua=float((s+frac(s,sa)*sa)@(l+frac(l,la)*la)/len(s));sigma=float(np.clip((mua/mu)**3,0,1));rcc=rc+sa*la-sigma*mu;dz,ds,dl,diagC=saddle(H,F,s,l,rd,rp,rcc);ec=errors(H,F,s,l,rd,rp,rcc,dz,ds,dl)
  certified=max(ea+ec)<1e-8
  alpha=min(frac(s,ds,.995),frac(l,dl,.995));merit=max(float(np.max(abs(rd))),float(np.max(abs(rp))),mu);accepted=False;merit1=None
  if certified:
   for bt in range(30):
    zz=z+alpha*dz;ss=s+alpha*ds;ll=l+alpha*dl;merit1=max(float(np.max(abs(H@zz+gg-F.T@ll))),float(np.max(abs(F@zz+b-ss))),float(ss@ll/len(ss)))
    if np.min(ss)>0 and np.min(ll)>0 and merit1 <= (1-1e-4*alpha)*merit:accepted=True;break
    alpha*=.5
  np.savez_compressed(out/('direction%02d.npz'%it),z=z,s=s,l=l,rd=rd,rp=rp,rc_predictor=rc,rc_corrector=rcc,predictor_dz=da,predictor_ds=sa,predictor_dl=la,dz=dz,ds=ds,dl=dl,sigma=sigma,alpha=alpha,accepted=accepted)
  hist.append(dict(iteration=it,predictor_errors=ea,corrector_errors=ec,certified=certified,accepted=accepted,alpha=alpha,merit=merit,merit_after=merit1,mu=mu,predictor_diagnostic=diagA,corrector_diagnostic=diagC));dump(out/'history.json',hist)
  if not certified:reason='uncertified direction REJECTED before iterate';break
  if not accepted:reason='merit backtracking REJECTED before iterate';break
  z,s,l=zz,ss,ll;cert_steps+=1
  if merit1<1e-11:reason='reduced numerical residual stop; fullphysical audit required';break
 coeff=cp+N@z;proposal=x+V@coeff;y=np.zeros(A.shape[0]);y[ine]=-unit*rs[ine]*l;y[eq]=lstsq(B[eq].T,-(fullH@coeff+g+B[ine].T@y[ine]),cond=1e-14)[0];res=P@proposal+p['q']+A.T@y;sl=A@proposal-p['lower'];obj=lambda w:float(.5*w@(P@w)+p['q']@w);gt=float((P@x+p['q'])@(proposal-x));pr=max(float(np.max(np.maximum(-sl[ine],0))),float(np.max(abs(sl[eq]))));accepted=bool(pr<1e-10 and gt<0 and obj(proposal)<=obj(x)+1e-4*gt);m=dict(primal_mm=pr,stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])),sign_N=float(np.max(np.maximum(y[ine],0))),complementarity_Nmm=float(np.max(abs(sl[ine]*y[ine]))),objective_before_Nmm=obj(x),objective_proposal_Nmm=obj(proposal),reduced_stationarity=float(np.max(abs(V.T@res))))
 np.savez_compressed(out/'endpoint.npz',coefficients=coeff,proposed_x=proposal,physical_dual=y,physical_residual=res,z=z,s=s,l=l)
 qualified=accepted and all(m[k]<1e-8 for k in ['stationarity_N','gauge_N','RootY_gamma_stationarity_N','sign_N','complementarity_Nmm']);dump(out/'summary.json',dict(status='ACTUAL_P1_CERTIFIED_CENTRALITY_TRIAL',candidate=c['s']['candidate'],source=ref(c['src']),source_field=c['s']['source_field'],physical_P=c['s']['physical_P'],physical_A=c['s']['physical_A'],problem=c['s']['problem'],partition_source=ref(partsrc),producer=ref(out/'producer.py'),reduced=ref(out/'reduced.npz'),output=ref(out/'endpoint.npz'),archived_corrector=ref(out/'archived_first_corrector.npz'),archived_metrics=archived,history=ref(out/'history.json'),reason=reason,algorithmic_start=dict(slack_floor=floor,mu=mu0),certified_algorithmic_steps=cert_steps,physical_KKT_qualified=bool(qualified),endpoint_finitegap_armijo_accepted=accepted,metrics=m,actual_support_updates=0,accepted_equilibria=0,physical_regularization=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start));print(json.dumps(dict(reason=reason,steps=cert_steps,archived=archived,metrics=m)))
if __name__=='__main__':main()
