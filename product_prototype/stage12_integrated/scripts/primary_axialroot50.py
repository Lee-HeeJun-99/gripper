"""First actual P1 pair axial volume threshold roots; no capacity inference."""
import json,sys,shutil,time,os,math
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from scipy.optimize import brentq

def main():
 out=ROOT/'validation/integrated/primaryP1_axialroot50';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';cad=json.loads(cp.read_text());br=cad['part_references']['BENCH_MOUNT_BOLT_0'];nr=cad['part_references']['BENCH_MOUNT_NUT_0'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [br,nr]);b=read(REPO/br['path']);n=read(REPO/nr['path']);rows=[];roots=[]
 for sign in [-1,1]:
  for tol in [1e-8,1e-10]:
   def f(z):
    assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
    with (out/'journal.jsonl').open('a') as log:log.write(json.dumps(dict(event='START',sign=sign,tol=tol,z=z))+'\n');log.flush();os.fsync(log.fileno())
    v=common(translate(b,0,0,sign*z),n);r=dict(sign=sign,threshold_mm3=tol,z_mm=z,common_mm3=v,elapsed_s=time.monotonic()-t);rows.append(r)
    with (out/'journal.jsonl').open('a') as log:log.write(json.dumps(dict(event='COMPLETE',**r))+'\n');log.flush();os.fsync(log.fileno())
    print(json.dumps(r),flush=True);return v-tol
   # Finite bracket, bounded root iterations; no unbounded retry.
   z=brentq(f,.04,.05,xtol=2e-6,maxiter=20);roots.append(dict(sign=sign,threshold_mm3=tol,root_mm=z))
 analytical=(4.605-4.456)/(2*math.sqrt(3));checks=dict(both_signs_and_thresholds=len(roots)==4,nominal_profile_agreement=all(abs(r['root_mm']-analytical)<.001 for r in roots),threshold_stability=all(abs(roots[j]['root_mm']-roots[j+1]['root_mm'])<.001 for j in [0,2]))
 dump(out/'summary.json',dict(status='ACTUAL_P1_AXIAL_ROOT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_AXIAL_ROOT_FAIL',candidate=ref(cp),bolt=br,nut=nr,producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks=checks,roots=roots,rows=rows,independent_analytic_clearance_mm=analytical,accepted_product_equilibria=0,newly_qualified_system_gate_ids=[],installed_capacity_N=None,whole_system_release=False,limitations=['Intersection-volume threshold roots are geometric capture,NOT material contact pressure/strength','Relative rotation held for query only;actual nut/head/key/cage/pin DOFs and ultimate host remain unqualified']))
 raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
