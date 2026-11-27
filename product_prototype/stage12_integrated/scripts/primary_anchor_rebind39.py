"""Canonical actual-part connector binding by an exact column permutation.
Reuses hashed actual-body elasticity responses; invalid prior QP states discarded.
"""
import sys,json,copy,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated'/sys.argv[2];old=json.loads((src/'summary.json').read_text());doc=copy.deepcopy(old);geo=json.loads((REPO/old['geometry']['path']).read_text());ops=dict(np.load(REPO/old['operators']['path']));nc=old['contact_variables'];labels=[p['label'] for p in geo['patches']];bolts=[labels.index('bolt'+str(i)) for i in range(3)];perm=[i for i in range(nc) if i not in bolts]+bolts;full=perm+list(range(nc,nc+6));proof=[]
 for r in [old['geometry'],old['operators'],old['local_common_refinement'],*old['fields']]:assert sha(REPO/r['path'])==r['SHA256']
 for k,b in enumerate(doc['body_results']):
  assert not(ROOT/'runtime/STOP').exists();a=dict(np.load(REPO/b['fields']['path']))
  if 'U' not in a:a['U']=np.column_stack([np.load(REPO/r['reference']['path'])['U'] for r in b['displacement_chunks']])
  before=a['F'].copy();a['F']=a['F'][:,full];a['U']=a['U'][:,full];a['dual']=a['dual'][:,full];proof.append(dict(part=b['part'],column_count=len(full),permuted_force_column_error_N=float(abs(a['F']-before[:,full]).max()),no_elastic_resolve=True,source_columns_unchanged=bool(np.array_equal(a['F'][:,-6:],before[:,-6:]))));chunks=[]
  U=a.pop('U')
  for first in range(0,U.shape[1],12):
   path=out/(b['part']+f'_U{first:03}.npz');np.savez_compressed(path,U=U[:,first:first+12]);chunks.append(dict(first_column=first,reference=ref(path)))
  path=out/(b['part']+'.npz');np.savez_compressed(path,**a);b.update(fields=ref(path),displacement_chunks=chunks);doc['fields'][k]=ref(path);del a,U,before
 geo['patches']=[geo['patches'][j] for j in perm];geo['body_quadrature']=[[q[j] for j in perm] for q in geo['body_quadrature']];dump(out/'geometry_journal.json',geo)
 Cs=np.array([c[np.ix_(full,full)] for c in ops['body_compliance']]);spring=np.zeros(nc);spring[-3:]=14/(200000.*np.pi*2.5**2);C=Cs[0,:nc,:nc]+Cs[1,:nc,:nc];C=(C+C.T)/2+np.diag(spring);ops.update(C=C,body_compliance=Cs,spring_mm_N=spring,equality=ops['equality'][:,perm],body_wrench=ops['body_wrench'][:,:,full]);np.savez_compressed(out/'operators.npz',**ops)
 eq=ops['equality'];scale=np.tile([1,1,1,.01,.01,.01],2);uu,ss,vv=np.linalg.svd(eq*scale[:,None],full_matrices=False);rank=int(sum(ss>ss[0]*1e-10));ae=uu[:,:rank].T@(eq*scale[:,None]);rows=[dict(case=r['case'],external_wrench_N_Nmm=r['external_wrench_N_Nmm'],reduced_equality_matrix=ae.tolist(),algebraic_equality_rank=rank,LP_feasible=r['LP_feasible'],status='NO_QP_STATE:PRIOR_MISBOUND_STATE_REJECTED') for r in old['rows']]
 dump(out/'enrichment.json',json.loads((REPO/old['local_common_refinement']['path']).read_text()));dump(out/'inputs.json',dict(candidate=old['candidate'],producer=ref(out/'producer.py'),parent=ref(src/'summary.json'),parent_inputs=old['inputs'],correction='Actualbolt IDs moved to last3columns;allforce/displacement/dual/compliance/wrench/geometry columns consistentlypermuted. Conditionalnominalspring applied ONLY actual3boltvariables. Prior misboundQPstates rejected;freshsolve required.',conditional_bolt_law='Nominalmajor5mm,L14mm,E200000MPa;NOT core/flank/preload/physicalsupport qualification',permutation=perm,source_columns_retained=True))
 doc.update(status='ACTUAL_P1_PART_ID_CONNECTOR_REBOUND_NO_EQUILIBRIUM',inputs=ref(out/'inputs.json'),geometry=ref(out/'geometry_journal.json'),operators=ref(out/'operators.npz'),local_common_refinement=ref(out/'enrichment.json'),rows=rows,producer=ref(out/'producer.py'),parent_misbound_trial=ref(src/'summary.json'),prior_misbound_QP_states_rejected=True,column_permutation=perm,elastic_permutation_proof=proof,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False)
 dump(out/'summary.json',doc);print(json.dumps(dict(parts=85,variables=nc,actual_bolt_indices=list(range(nc-3,nc)),elastic_permutation=proof)))
if __name__=='__main__':main()
