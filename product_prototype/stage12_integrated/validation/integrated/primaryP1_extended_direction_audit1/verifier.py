"""Independent audit of rejected terminal direction and extended-accumulator correction."""
import sys,time,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');base=ROOT/'validation/integrated';audit=base/'primaryP1_certified_centrality_audit2/summary.json';au=json.loads(audit.read_text());assert all(au['checks'].values());rows=[];checks={}
 for tag in ['primaryP1_uneliminated_direction1','primaryP1_extended_direction1']:
  src=base/tag/'summary.json';s=json.loads(src.read_text());r=np.load(REPO/s['reduced']['path']);e=np.load(REPO/s['terminal_equation']['path']);a=np.load(REPO/s['output']['path']);H,F=r['H'].astype(np.longdouble),r['F'].astype(np.longdouble);z,sl,lam=[e[k].astype(np.longdouble) for k in ['z','s','l']];dz,ds,dl=[a[k].astype(np.longdouble) for k in ['dz','ds','dl']]
  # Equations audited without assembled/scaled K, no factorization or producer import.
  rr=[H@dz-F.T@dl+e['rd'],F@dz-ds+e['rp'],lam*ds+sl*dl+e['rc_corrector']];err=[float(np.max(abs(v))) for v in rr];cert=max(err)<1e-8;wrong=float(np.max(abs(H@dz+F.T@dl+e['rd'])));omit=int(np.argmax(abs(dl)));missing=float(np.max(abs(rr[0]+F[omit]*dl[omit])));controls=dict(reversed_dual=wrong,omitted_original_row=missing,reversed_finite_gap=float(np.max(abs(rr[1]-2*r['b']))));rd=H@z+r['g'].astype(np.longdouble)-F.T@lam;rp=F@z+r['b'].astype(np.longdouble)-sl
  checks[tag]=bool(np.allclose(err,s['first_order_errors'],rtol=1e-10,atol=1e-14) and cert==s['direction_certified'] and all(v>1e-8 for v in controls.values()) and s['actual_iterate_updates']==0 and s['actual_support_updates']==0 and max(float(np.max(abs(rd-e['rd']))),float(np.max(abs(rp-e['rp']))))<1e-8 and all(sha(REPO/s[k]['path'])==s[k]['SHA256'] for k in ['source','terminal_equation','reduced','output']))
  rows.append(dict(source=ref(src),errors=err,certified=cert,dtype=str(a['dz'].dtype),negative_controls=controls))
 checks['double_rejected_extended_certified']=not rows[0]['certified'] and rows[1]['certified'];checks['same_original_terminal']=json.loads((base/'primaryP1_uneliminated_direction1/summary.json').read_text())['terminal_equation']==json.loads((base/'primaryP1_extended_direction1/summary.json').read_text())['terminal_equation'];ok=all(checks.values());dump(out/'summary.json',dict(status='ACTUAL_P1_EXTENDED_DIRECTION_AUDIT_PASS' if ok else 'ACTUAL_P1_EXTENDED_DIRECTION_AUDIT_FAIL',source=ref(audit),verifier=ref(out/'verifier.py'),checks=checks,directions=rows,actual_iterate_updates=0,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t));print(json.dumps(dict(checks=checks,directions=rows)));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
