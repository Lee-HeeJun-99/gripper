"""Rank-aware bound QP: retain affine nullspace descent and original cone signs.
Numerical working sets only; full original KKT, never rank alone, certifies output.
"""
import numpy as np
from scipy.linalg import eigh

def solve(S,h,inequality,max_steps=3000):
    n=len(h); y=np.zeros(n); free=~inequality.copy(); history=[]; reason='working-set limit'
    for iteration in range(max_steps):
        g=S@y-h; ids=np.flatnonzero(free); p=np.zeros(n); nullnorm=0.; rank=0
        if len(ids):
            H=S[np.ix_(ids,ids)]; w,U=eigh(H); cut=max(abs(w[-1])*1e-12,1e-14); positive=w>cut; rank=int(sum(positive)); gf=g[ids]; ng=U[:,~positive].T@gf; nullnorm=float(np.linalg.norm(ng))
            if nullnorm>1e-10:
                # Do not discard affine components outside the resolved range.
                # Follow their nullspace descent until a cone bound blocks it.
                p[ids]=-U[:,~positive]@ng
                scale=np.max(abs(p)); p/=max(scale,1e-30); kind='affine_null_descent'
            else:
                p[ids]=-U[:,positive]@((U[:,positive].T@gf)/w[positive]); kind='range_newton'
        else:kind='empty'
        if np.max(abs(p))<1e-10:
            bound=inequality&~free; violation=np.where(bound,g,-np.inf); j=int(np.argmax(violation))
            if violation[j]<=1e-9: reason='original bound KKT converged';break
            free[j]=True;history.append(dict(iteration=iteration,event='release',row=j,gradient=float(g[j]),rank=rank,null_affine_norm=nullnorm));continue
        blocking=np.flatnonzero(free&inequality&(p>1e-14)); alpha=1.;block=None
        if len(blocking):
            ratios=-y[blocking]/p[blocking]; k=int(np.argmin(ratios)); candidate=max(0.,float(ratios[k]))
            if candidate<alpha or kind=='affine_null_descent':alpha=candidate;block=int(blocking[k])
        elif kind=='affine_null_descent':reason='unblocked affine null descent: no finite minimizer certified';break
        y+=alpha*p
        if block is not None:y[block]=0.;free[block]=False
        history.append(dict(iteration=iteration,event=kind,alpha=alpha,blocked=block,rank=rank,free=len(ids),null_affine_norm=nullnorm,objective=float(.5*y@(S@y)-h@y)))
    g=S@y-h; mask=inequality&(y>=-1e-10); residual=max(float(np.max(abs(g[~mask]))) if np.any(~mask) else 0.,float(np.max(np.maximum(g[mask],0))) if np.any(mask) else 0.)
    return y,dict(reason=reason,iterations=iteration+1,KKT=residual,sign=float(np.max(np.maximum(y[inequality],0))),complementarity=float(np.max(abs(y[inequality]*g[inequality]))),history=history)

if __name__=='__main__':
    import sys,json,shutil,time
    from baseline_registry import ROOT,REPO,ref,dump
    start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/integrated/primaryP1_finite_gap_projection1/summary.json';s=json.loads(src.read_text());problem=np.load(REPO/s['problem']['path']);eq=np.isfinite(problem['upper'])&(problem['lower']==problem['upper']);records=[]
    for row in s['batches']:
        c=np.load(REPO/row['output']['path']);S=c['small_S'];h=c['small_h'];mask=~eq[c['active']];y,r=solve(S,h,mask);f=out/('batch'+str(row['batch'])+'.npz');np.savez_compressed(f,S=S,h=h,y=y,inequality=mask,active=c['active'],gradient=S@y-h)
        dump(out/('history'+str(row['batch'])+'.json'),r.pop('history'));records.append(dict(batch=row['batch'],source=row['output'],output=ref(f),**r))
    ok=all(r['KKT']<1e-8 and r['sign']<1e-10 and r['complementarity']<1e-8 for r in records)
    dump(out/'summary.json',dict(status='ACTUAL_P1_AFFINE_CONE_SMALL_KKT_PASS' if ok else 'ACTUAL_P1_AFFINE_CONE_SMALL_KKT_REJECTED',candidate=s['candidate'],source=ref(src),producer=ref(out/'producer.py'),batches=records,elapsed_s=time.monotonic()-start,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Actual archived search-metric QPs only; not physical P/q equilibrium. Numerical eigenspace split retains affine null descent and requires original KKT; no physical row deletion or regularization.']))
    print(records);raise SystemExit(0 if ok else 2)
