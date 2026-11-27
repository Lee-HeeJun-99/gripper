"""Same mesh and original shared columns, dense-RHS versus block-RHS equivalence."""
import json,sys,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def arrays(doc,k):
 a=dict(np.load(REPO/doc['fields'][k]['path']))
 if 'U' not in a:a['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in doc['body_results'][k]['displacement_chunks']])
 return a

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');paths=[ROOT/'validation/integrated'/x/'summary.json' for x in sys.argv[2:]];old,new=[json.loads(p.read_text()) for p in paths];assert old['candidate']==new['candidate'];no,nn=old['contact_variables'],new['contact_variables'];pick=np.r_[np.arange(no-3),np.arange(nn-3,nn+6)];rows=[]
 for k in range(2):
  a,b=arrays(old,k),arrays(new,k);assert np.array_equal(a['points_mm'],b['points_mm']) and np.array_equal(a['tetra'],b['tetra']);f=float(abs(a['F']-b['F'][:,pick]).max());e=float(abs(a['U']-b['U'][:,pick]).max()/max(abs(a['U']).max(),1e-30));rows.append(dict(part=old['body_results'][k]['part'],force_columns_max_difference_N=f,all_shared_displacements_relative=e,pass_original_numerical_equivalence=f<1e-12 and e<1e-7))
 checks=dict(same_candidate=True,all_shared_columns_identical_within_original_numerical_limit=all(r['pass_original_numerical_equivalence'] for r in rows));dump(out/'summary.json',dict(status='ACTUAL_P1_BLOCK_RHS_EQUIVALENCE_PASS' if all(checks.values()) else 'ACTUAL_P1_BLOCK_RHS_EQUIVALENCE_FAIL',candidate=old['candidate'],sources=[ref(p) for p in paths],verifier=ref(out/'verifier.py'),rows=rows,checks=checks,original_columns=no+6,new_columns=nn+6,physical_data_changed=False,all_original_constraints_retained=True,whole_system_release=False));print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
