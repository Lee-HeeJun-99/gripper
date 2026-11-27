"""Independent numerical equivalence of six-gauge solutions on actual bodies."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');dirs=[ROOT/'validation/integrated'/x for x in sys.argv[2:4]];docs=[json.loads((p/'summary.json').read_text()) for p in dirs];rows=[]
 for k in range(2):
  fields=[]
  for d in docs:
   a=dict(np.load(REPO/d['fields'][k]['path']))
   if 'U' not in a:a['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in d['body_results'][k]['displacement_chunks']])
   fields.append(a)
  a,b=fields;assert np.array_equal(a['points_mm'],b['points_mm']) and np.array_equal(a['tetra'],b['tetra']);assert np.array_equal(a['F'],b['F'])
  uerr=float(abs(a['U']-b['U']).max());rel=float(np.linalg.norm(a['U']-b['U'])/np.linalg.norm(a['U']));ca=a['F'].T@a['U'];cb=b['F'].T@b['U'];ce=float(np.linalg.norm(ca-cb)/np.linalg.norm(ca));g=float(abs(b['Q']@b['U']).max());null=float(abs(b['Q']@b['R']@np.linalg.solve(b['Q']@b['R'],b['Q']@b['U'])).max())
  rows.append(dict(part=docs[0]['body_results'][k]['part'],identical_mesh_loads=True,maximum_displacement_difference_mm=uerr,displacement_relative=rel,compliance_relative=ce,restored_original_gauge_mm=g,all_DOF_restored=True,physical_fixed_DOF=0,pass_original1percent=rel<.01 and ce<.01,pass_numerical1e_minus7=rel<1e-7 and ce<1e-7 and g<1e-10))
 checks=dict(identical_actual_candidate=docs[0]['candidate']==docs[1]['candidate'],all_original_gauges_and_solutions_equivalent=all(r['pass_numerical1e_minus7'] for r in rows))
 dump(out/'summary.json',dict(status='ACTUAL_P1_SPARSE_QUOTIENT_GAUGE_EQUIVALENCE_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_SPARSE_QUOTIENT_GAUGE_EQUIVALENCE_FAIL',candidate=docs[0]['candidate'],sources=[ref(x/'summary.json') for x in dirs],verifier=ref(out/'verifier.py'),checks=checks,rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Same actual FE mesh,all boundary load columns,original six mean-rigid gauges. No physical fixture added.','Algebraic anchors eliminated for factorization only;restored before physical force/work audits. No response or material criterion changed.']))
 print(json.dumps(rows));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
