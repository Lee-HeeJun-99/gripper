"""Same actual body/source identities and response contrasts, no mesh certificate."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'reviewer.py');paths=[ROOT/'validation/integrated'/x for x in sys.argv[2:]];docs=[json.loads((p/'summary.json').read_text()) for p in paths];identities=[];arrays=[]
 for d in docs:
  arrays.append([dict(np.load(REPO/r['path'])) for r in d['fields']])
 for k in range(2):
  base=arrays[0][k]
  for i,a in enumerate(arrays[1:],1):
   b=a[k];identities.append(dict(source=ref(paths[i]/'summary.json'),part=docs[i]['body_results'][k]['part'],same_points=bool(np.array_equal(base['points_mm'],b['points_mm'])),same_tetra=bool(np.array_equal(base['tetra'],b['tetra'])),same_actual_source_columns=bool(np.array_equal(base['F'][:,-6:],b['F'][:,-6:]))))
 comparisons=[]
 for i in range(1,len(docs)):
  rows=[]
  for a,b in zip(docs[i-1]['rows'],docs[i]['rows']):
   assert a['case']==b['case'] and a['external_wrench_N_Nmm']==b['external_wrench_N_Nmm'];work=abs(b['total_strain_work_Nmm']/a['total_strain_work_Nmm']-1);bolt=float(np.linalg.norm(np.array(a['bolt_tension_N'])-b['bolt_tension_N'])/max(np.linalg.norm(b['bolt_tension_N']),1e-30));rows.append(dict(case=a['case'],relative_conditional_work_change=work,relative_bolt_vector_change=bolt,original1percent_work_and_bolt_only=work<.01 and bolt<.01))
  comparisons.append(dict(from_source=ref(paths[i-1]/'summary.json'),to_source=ref(paths[i]/'summary.json'),rows=rows,maximum_work_change=max(r['relative_conditional_work_change'] for r in rows),maximum_bolt_vector_change=max(r['relative_bolt_vector_change'] for r in rows),all14_original1percent_work_and_bolt_only=all(r['original1percent_work_and_bolt_only'] for r in rows),physical_pressure_convergence=None,full_contact_convergence=False))
 dump(out/'summary.json',dict(status='ACTUAL_P1_LOCAL_CONTACT_ENRICHMENT_RESPONSE_CONTRAST_NOT_CONVERGENCE',candidate=docs[0]['candidate'],reviewer=ref(out/'reviewer.py'),sources=[ref(p/'summary.json') for p in paths],actual_parts=85,actual_bulk_source_identities=identities,all_bulk_source_identical=all(all(r[k] for k in ['same_points','same_tetra','same_actual_source_columns']) for r in identities),comparisons=comparisons,newly_qualified_system_gate_ids=[],whole_system_release=False,accepted_physical_product_equilibria=0,limitations=['Identical bulk FE mesh and actual signed source columns;only local unilateral contact spaces change. Not a bulk mesh refinement or time experiment.','Uniform-cell and vertex-force spaces differ;nodelumped force/area cannot certify physical pressure convergence or thread/head contact.','All original work/bolt1percent thresholds retained;partial response agreement cannot qualify all response/pointwise/strength/energy gates.']))
 print(json.dumps([dict(work=x['maximum_work_change'],bolt=x['maximum_bolt_vector_change']) for x in comparisons]))
if __name__=='__main__':main()
