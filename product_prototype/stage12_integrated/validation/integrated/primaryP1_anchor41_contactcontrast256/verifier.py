"""Same actual product, load and contact-space compliance contrast, no stiffness ratio."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');paths=[ROOT/'validation/integrated'/x/'summary.json' for x in sys.argv[2:]];docs=[json.loads(p.read_text()) for p in paths];base=docs[0];rows=[]
 assert all(d['candidate']==base['candidate'] for d in docs)
 for d,path in zip(docs[1:],paths[1:]):
  for a,b in zip(base['rows'],d['rows']):
   assert a['case']==b['case'] and a['external_wrench_N_Nmm']==b['external_wrench_N_Nmm']
   x=a['total_strain_work_Nmm'];y=b['total_strain_work_Nmm'];aa=np.array(a['bolt_tension_N']);bb=np.array(b['bolt_tension_N']);rows.append(dict(source=ref(path),case=a['case'],both_optimizer_success=bool(a['optimizer_success'] and b['optimizer_success']),original_work_Nmm=x,new_work_Nmm=y,relative_work_change=abs(y-x)/max(abs(x),abs(y),1e-30),relative_bolt_vector_change=float(np.linalg.norm(bb-aa)/max(np.linalg.norm(aa),np.linalg.norm(bb),1e-30)),maximum_bolt_tension_N=float(bb.max()),minimum_force_N=min(b['contact_forces_N'])))
 checks=dict(all_optimizer_success=all(r['both_optimizer_success'] for r in rows),original_force_nonnegative=all(r['minimum_force_N']>-1e-10 for r in rows),response_within_original_one_percent=all(max(r['relative_work_change'],r['relative_bolt_vector_change'])<.01 for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_CONDITIONAL_RESPONSE_CONTRAST_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_CONDITIONAL_RESPONSE_CONTRAST_FAIL',candidate=base['candidate'],sources=[ref(p) for p in paths],verifier=ref(out/'verifier.py'),checks=checks,rows=rows,maximum_work_change=max(r['relative_work_change'] for r in rows),maximum_bolt_vector_change=max(r['relative_bolt_vector_change'] for r in rows),newly_qualified_system_gate_ids=[],whole_system_release=False,limitation='Same product conditional sensitivity;not bulk mesh convergence,physical thread-stack qualification,physical pressure,operating load or strength. Original failed sources retained.'));print(json.dumps(checks))
if __name__=='__main__':main()
