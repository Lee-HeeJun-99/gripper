"""Independent original equation and saved trajectory audit, without producer solver."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(src.read_text());r=np.load(REPO/s['reduced']['path']);H,F,g,b=[r[k].astype(np.longdouble) for k in ['H','F','g','b']];paths=[REPO/s['output']['path']] if 'pair' in sys.argv[2] else sorted(src.parent.glob('pair*.npz'));checks={};rows=[];previous=None
 for path in paths:
  a=np.load(path);z,sl,lam=[a[k].astype(np.longdouble) for k in ['z','s','l']];rd=H@z+g-F.T@lam;rp=F@z+b-sl;errs=[]
  for prefix,rc in [('predictor_',sl*lam),('',a['rc_corrector'])]:
   dz,ds,dl=[a[prefix+k].astype(np.longdouble) for k in ['dz','ds','dl']];errs.append([float(np.max(abs(v))) for v in [H@dz-F.T@dl+rd,F@dz-ds+rp,lam*ds+sl*dl+rc]])
  da,sa,la=[a['predictor_'+k] for k in ['dz','ds','dl']]
  def frac(v,d):
   mask=d<0;return min(1.,float(np.min(-v[mask]/d[mask]))) if mask.any() else 1.
  mu=np.mean(sl*lam);sigma=np.clip((np.mean((sl+frac(sl,sa)*sa)*(lam+frac(lam,la)*la))/mu)**3,0,1);rcc=sl*lam+sa*la-sigma*mu
  equation=max(float(np.max(abs(rd-a['rd']))),float(np.max(abs(rp-a['rp']))),float(np.max(abs(rcc-a['rc_corrector']))))
  dz,ds,dl=[a[k] for k in ['dz','ds','dl']];wrong=float(np.max(abs(H@dz+F.T@dl+rd)));i=int(np.argmax(abs(dl)));omit=float(np.max(abs(H@dz-F.T@dl+rd+F[i]*dl[i])));reverse=float(np.max(abs(F@dz-ds+rp-2*b)))
  certified=max(sum(errs,[]))<1e-8;checks[path.name+'_equations']=equation<1e-8;checks[path.name+'_controls']=min(wrong,omit,reverse)>1e-8
  if previous is not None:checks[path.name+'_trajectory']=all(np.max(abs(a[k]-previous[k]))<1e-15 for k in ['z','s','l'])
  if 'accepted' in a:
   alpha=a['alpha'];zz=z+alpha*dz;ss=sl+alpha*ds;ll=lam+alpha*dl;merit=max(float(np.max(abs(rd))),float(np.max(abs(rp))),float(mu));after=max(float(np.max(abs(H@zz+g-F.T@ll))),float(np.max(abs(F@zz+b-ss))),float(np.mean(ss*ll)));accept=bool(certified and min(ss.min(),ll.min())>0 and after<=(1-1e-4*alpha)*merit);checks[path.name+'_acceptance']=accept==bool(a['accepted']);previous=dict(z=zz,s=ss,l=ll) if accept else dict(z=z,s=sl,l=lam)
  else:checks['prepared_pair_certified']=certified
  rows.append(dict(path=ref(path),errors=errs,certified=certified,controls=[wrong,omit,reverse]))

 if previous is not None:
  endpoint=np.load(REPO/s['output']['path']);checks['terminal_trajectory']=all(np.max(abs(endpoint[k]-previous[k]))<1e-15 for k in ['z','s','l']);checks['accepted_count']=sum(bool(np.load(p)['accepted']) for p in paths)==s['certified_algorithmic_steps']
 first=np.load(paths[0]);arch=np.load(ROOT/'validation/integrated/primaryP1_certified_centrality1/direction19.npz');checks['archived_start']=all(np.array_equal(first[k],arch[k]) for k in ['z','s','l'])
 checks['source_hashes']=all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ['source','reduced','output']);ok=all(checks.values());dump(out/'summary.json',dict(status='ACTUAL_P1_PAIR_AUDIT_PASS' if ok else 'ACTUAL_P1_PAIR_AUDIT_FAIL',source=ref(src),verifier=ref(out/'verifier.py'),checks=checks,directions=rows,actual_support_updates=0,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(dict(checks=checks,rows=rows)));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
