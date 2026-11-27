"""One measured elastic enrichment of actual P1; original-unit feasible segment guard.
Interior-point trajectories are algorithmic only. No nonlinear support update.
"""
import sys,time,json,shutil
import numpy as np
from scipy.linalg import lstsq,null_space
from baseline_registry import ROOT,REPO,ref,dump
from primary_augmented_saddle import setup
from primary_extended_continuation import direction as extended_direction
from primary_certified_centrality import frac,errors

def direction(H,F,s,l,rd,rp,rc):
 dz,ds,dl=extended_direction(H,F,s,l,rd,rp,rc)
 # Exact original primal equation, evaluated in the retained extended accumulator.
 # This is a variable back-substitution; all three equations remain certified.
 ds=F.astype(np.longdouble)@dz+rp
 return dz,ds,dl

def pair(H,F,g,b,z,s,l):
 rd=H.astype(np.longdouble)@z+g-F.T.astype(np.longdouble)@l;rp=F.astype(np.longdouble)@z+b-s;rc=s*l
 da,sa,la=direction(H,F,s,l,rd,rp,rc);ea=errors(H,F,s,l,rd,rp,rc,da,sa,la)
 mu=np.mean(rc);mua=np.mean((s+frac(s,sa)*sa)*(l+frac(l,la)*la));sigma=np.clip((mua/mu)**3,0,1);rcc=rc+sa*la-sigma*mu
 dz,ds,dl=direction(H,F,s,l,rd,rp,rcc);ec=errors(H,F,s,l,rd,rp,rcc,dz,ds,dl)
 return dict(z=z,s=s,l=l,rd=rd,rp=rp,rc_predictor=rc,rc_corrector=rcc,predictor_dz=da,predictor_ds=sa,predictor_dl=la,dz=dz,ds=ds,dl=dl,sigma=sigma),ea,ec

def build():
 c=setup();oldsrc=ROOT/'validation/integrated/primaryP1_certified_centrality1/summary.json';old=json.loads(oldsrc.read_text());rd=np.load(REPO/old['reduced']['path']);msrc=ROOT/'validation/integrated/primaryP1_extended_endpoint_audit1/summary.json';ms=json.loads(msrc.read_text());md=np.load(REPO/ms['output']['path']);v=md['physical_probe'];V=np.column_stack([c['V'],rd['probe'],v]);P,A,p,x=[c[k] for k in ['P','A','p','x']];eq,ine=c['eq'],c['ine'];B=A@V;Q=V.T@(P@V);g=V.T@(P@x+p['q']);E=B[eq];cp=lstsq(E,(p['lower']-A@x)[eq],cond=1e-14)[0];N=null_space(E,rcond=1e-14);unit=max(float(np.max(abs(g))),1e-15);rs=1/np.maximum(np.max(abs(B),axis=1),1e-15);H=N.T@Q@N/unit;gg=N.T@(g+Q@cp)/unit;F=(rs[ine,None]*B[ine])@N;b=rs[ine]*((A@x-p['lower'])[ine]+B[ine]@cp)
 end=np.load(ROOT/'validation/integrated/primaryP1_extended_continuation1/endpoint.npz');z=np.zeros(N.shape[1],dtype=np.longdouble);floor=max(1e-3,float(np.max(abs(F@z+b)))*.01);s=np.maximum(F@z+b,floor);mu=max(1e-3,float(np.max(abs(H@z+gg))));l=mu/s
 return locals()

def physical(c,z,l):
 P,A,p,x,V,B,Q,g,cp,N,rs,unit,eq,ine=[c[k] for k in ['P','A','p','x','V','B','Q','g','cp','N','rs','unit','eq','ine']];coeff=cp+N@z;proposal=x+V@coeff;y=np.zeros(A.shape[0],dtype=np.longdouble);y[ine]=-unit*rs[ine]*l;y[eq]=lstsq(B[eq].T,np.asarray(-(Q@coeff+g+B[ine].T@y[ine]),dtype=float),cond=1e-14)[0];res=P@proposal+p['q']+A.T@y;sl=A@proposal-p['lower'];obj=lambda w:float(.5*w@(P@w)+p['q']@w);dx=proposal-x;gt=float((P@x+p['q'])@dx);gap0=A@x-p['lower'];motion=A@dx
 # Segment from original feasible state; all original finite-gap rows retained.
 # Exact boundary rows with negative motion block at alpha=0 (never clipped).
 neg=ine&(motion<0);bounds=np.maximum(gap0[neg],0)/(-motion[neg]);alpha=min(1.,.995*float(np.min(bounds))) if len(bounds) else 1.;alpha=max(0.,alpha);feasible=x+alpha*dx;slf=A@feasible-p['lower'];pr=lambda sl:max(float(np.max(np.maximum(-sl[ine],0))),float(np.max(abs(sl[eq]))));accepted=bool(alpha>0 and pr(slf)<1e-10 and gt<0 and obj(feasible)<=obj(x)+1e-4*alpha*gt)
 m=dict(primal_mm=pr(sl),stationarity_N=float(np.max(abs(res))),gauge_N=float(np.max(abs(y[eq]))),RootY_gamma_stationarity_N=float(abs(y[2175])),sign_N=float(np.max(np.maximum(y[ine],0))),complementarity_Nmm=float(np.max(abs(sl[ine]*y[ine]))),reduced_stationarity=float(np.max(abs(V.T@res))),objective_before_Nmm=obj(x),objective_proposal_Nmm=obj(proposal))
 gm=dict(alpha=alpha,primal_mm=pr(slf),objective_Nmm=obj(feasible),directional_work_Nmm=gt,accepted=accepted,blocking_original_row=int(np.flatnonzero(neg)[np.argmin(bounds)]) if len(bounds) else None,minimum_start_gap_mm=float(np.min(gap0[ine])),maximum_segment_increment_mm_rad=float(np.max(abs(alpha*dx))))
 # Segment guard is a primal/objective check only; it never certifies dual equilibrium.
 return dict(coefficients=coeff,proposed_x=proposal,physical_dual=y,physical_residual=res,segment_x=feasible),m,gm

def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');mode=sys.argv[2];c=build();H,F,g,b=[c[k] for k in ['H','F','gg','b']];z,s,l=[c[k].copy().astype(np.longdouble) for k in ['z','s','l']]
 if mode=='prepare':
  np.savez_compressed(out/'reduced.npz',H=H,F=F,g=g,b=b,cp=c['cp'],N=c['N'],rs=c['rs'],unit=c['unit'],z0=z,s0=s,l0=l,probe=c['v']);a,ea,ec=pair(H,F,g,b,z,s,l);np.savez_compressed(out/'pair.npz',**a);dump(out/'summary.json',dict(status='ACTUAL_P1_132COLUMN_ENRICHED_PAIR',candidate=c['c']['s']['candidate'],source_field=c['c']['s']['source_field'],source=ref(c['msrc']),reduced=ref(out/'reduced.npz'),output=ref(out/'pair.npz'),predictor_errors=ea,corrector_errors=ec,certified=max(ea+ec)<1e-8,actual_iterate_updates=0,algorithmic_start='original sourcefield affine particular, z=0; positive slack/dual are algorithmic only'));return
 prep=ROOT/'validation/integrated/primaryP1_measured_enrichment_pair3/summary.json';pre=json.loads(prep.read_text());aud=ROOT/'validation/integrated/primaryP1_measured_enrichment_pre_audit3/summary.json';assert all(json.loads(aud.read_text())['checks'].values());r=np.load(REPO/pre['reduced']['path']);assert all(np.array_equal(r[k],v) for k,v in [('H',H),('F',F),('g',g),('b',b)])
 hist=[];steps=0;reason='60 enriched iteration limit';best=None
 for it in range(60):
  if(ROOT/'runtime/STOP').exists():reason='STOP';break
  if time.monotonic()-start>240:reason='240s internal budget';break
  a,ea,ec=pair(H,F,g,b,z,s,l);cert=max(ea+ec)<1e-8;alpha=min(frac(s,a['ds'],.995),frac(l,a['dl'],.995));merit=max(float(np.max(abs(a['rd']))),float(np.max(abs(a['rp']))),float(np.mean(s*l)));accepted=False;after=None
  if cert:
   for bt in range(30):
    zz=z+alpha*a['dz'];ss=s+alpha*a['ds'];ll=l+alpha*a['dl'];after=max(float(np.max(abs(H.astype(np.longdouble)@zz+g-F.T.astype(np.longdouble)@ll))),float(np.max(abs(F.astype(np.longdouble)@zz+b-ss))),float(np.mean(ss*ll)))
    if min(ss.min(),ll.min())>0 and after<=(1-1e-4*alpha)*merit:accepted=True;break
    alpha*=.5
  np.savez_compressed(out/('pair%02d.npz'%it),**a,alpha=alpha,accepted=accepted)
  ep,mm,gm=physical(c,zz if accepted else z,ll if accepted else l)
  if gm['accepted'] and (best is None or gm['objective_Nmm']<best[0]):best=(gm['objective_Nmm'],it,gm)
  hist.append(dict(iteration=it,predictor_errors=ea,corrector_errors=ec,certified=cert,alpha=alpha,merit=merit,merit_after=after,accepted=accepted,physical_segment=gm));dump(out/'history.json',hist)
  if not cert:reason='uncertified enriched pair rejected';break
  if not accepted:reason='algorithmic merit rejected';break
  z,s,l=zz,ss,ll;steps+=1
  if after<1e-11:reason='reduced residual stop; fullphysical audit required';break
 ep,m,gm=physical(c,z,l);np.savez_compressed(out/'endpoint.npz',**ep,z=z,s=s,l=l)
 qualified=bool(gm['accepted'] and gm['alpha']==1 and m['primal_mm']<1e-10 and all(m[k]<1e-8 for k in ['stationarity_N','gauge_N','RootY_gamma_stationarity_N','sign_N','complementarity_Nmm']))
 dump(out/'summary.json',dict(status='ACTUAL_P1_MEASURED_ENRICHMENT_PHYSICAL_TRIAL',candidate=pre['candidate'],source_field=pre['source_field'],source=ref(prep),reduced=pre['reduced'],precontinuation_audit=ref(aud),output=ref(out/'endpoint.npz'),history=ref(out/'history.json'),metrics=m,segment_guard=gm,best_primal_segment=best,reason=reason,certified_algorithmic_steps=steps,physical_KKT_qualified=qualified,actual_support_updates=0,accepted_equilibria=0,whole_system_release=False,newly_qualified_system_gate_ids=[],elapsed_s=time.monotonic()-start));print(json.dumps(dict(metrics=m,segment=gm,steps=steps,reason=reason)))
if __name__=='__main__':main()
