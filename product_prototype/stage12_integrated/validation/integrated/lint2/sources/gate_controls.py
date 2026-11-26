"""Corrupt copies in memory only; never change historical evidence."""
import argparse,copy,json
from pathlib import Path
from baseline_registry import ROOT,S2,ref,dump,invalidated
from integrated_release_gate import audit,check_contract,s2
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    b=json.loads((ROOT/'CURRENT_BASELINE.json').read_text());c=json.loads((ROOT/'models/integrated_contract.json').read_text())
    file=ref(S2/'validation/convergence/torsion1/summary.json')
    # Isolated schema control: deliberately NOT eligible to release a product.
    fixture=copy.deepcopy(c);fixture['system_evidence']=[dict(file,scope='SYSTEM_LOAD_TRANSFER',executed=True,material_basis='not_material_dependent',revision=b['revision'])]
    assert not check_contract(fixture)
    rows=[]
    def test(name,doc,needle,full=False):
        errors=audit(doc,c)['errors'] if full else check_contract(doc)
        passed=any(needle in e for e in errors);rows.append(dict(name=name,rejected=passed,expected_error=needle));assert passed,(name,errors)
    x=copy.deepcopy(fixture);x['stage2_revision']='revAB_sliding_pet1';test('different_revision_PASS',x,'different revision')
    x=copy.deepcopy(b);x['parts'][0]['STEP']['SHA256']='0'*64;test('changed_STEP',x,'geometry invalidated',True)
    x=copy.deepcopy(fixture);x['system_evidence'][0]['path']='absent_fem.npz';test('missing_FEM',x,'missing/stale')
    for v in (float('nan'),float('inf')):
        x=copy.deepcopy(fixture);x['metric']=v;test('NaN_or_Inf_'+str(v),x,'nonfinite')
    x=copy.deepcopy(fixture);x['system_evidence'][0]['material_basis']='typical';test('unsupported_material',x,'unsupported material')
    x=copy.deepcopy(fixture);x['system_evidence'][0]['executed']=False;test('unrun_test',x,'unrun test')
    x=copy.deepcopy(fixture);x['system_evidence'][0]['scope']='COUPON';test('coupon_promotion',x,'coupon promotion')
    x=copy.deepcopy(fixture);x['hardware_status']='HARDWARE_PASS';test('fake_hardware',x,'hardware claim')
    x=copy.deepcopy(fixture);x['system_evidence']*=2;test('duplicate_evidence',x,'duplicate')
    x=copy.deepcopy(fixture);x['stage1_revision']='revH';test('stale_stage1',x,'different revision')
    # Exercise inherited Stage2 convergence logic directly with complete synthetic
    # records. Synthetic fixtures are explicitly barred by its normal CLI.
    registry=dict(test_only=True,baseline={},collision_models_removed=False,qv_forced=False,records={})
    for key,domain in s2.REQUIRED.items():
        registry['records'][key]=dict(status='PASS',scope='SYSTEM_LOAD_TRANSFER',domain=domain,material_basis='not_material_dependent',evidence={'scripts/stage2_release_gate.py':s2.sha(S2/'scripts/stage2_release_gate.py')},source={'scripts/stage2_release_gate.py':s2.sha(S2/'scripts/stage2_release_gate.py')},model={'scripts/stage2_release_gate.py':s2.sha(S2/'scripts/stage2_release_gate.py')},metrics=[dict(name='zero',value=0.,maximum=0.,unit='N')])
    rec=registry['records']['numerical_convergence'];rec['metrics']=[dict(name='time_relative',value=0.,maximum=.001,unit='1'),dict(name='mesh_relative',value=0.,maximum=.01,unit='1')]
    assert not s2.validate(registry,S2,{},allow_test=True)['errors']
    rec['metrics'][0]['maximum']=.002
    errors=s2.validate(registry,S2,{},allow_test=True)['errors'];assert any('relaxed' in e for e in errors)
    rows.append(dict(name='relaxed_convergence',rejected=True,errors=errors))
    x=copy.deepcopy(b);x['parts'][0]['material_requirement']='changed material'
    assert 'material_requirement' in invalidated(b,x)['PALM']
    assert audit(b,c)['status']=='INTEGRATED_NOT_QUALIFIED'
    actual=ROOT/'cad/exports/revAD_funnel1/ASSEMBLY.step'
    if actual.exists():
        x=copy.deepcopy(b);x['assembly']=ref(actual);test('actual_mixed_assembly_with_AA_release',x,'stage1 assembly differs',True)
    frozen=copy.deepcopy(json.loads((S2/'models/analytical/criteria.json').read_text()));frozen['static_force_balance_N_max']=1e-6
    changed=out/'test_only_relaxed_criteria.json';dump(changed,frozen)
    x=copy.deepcopy(b);x['criteria']=ref(changed);test('actual_changed_force_criterion',x,'inherited criteria changed',True)
    x=copy.deepcopy(fixture);x['system_evidence'][0]['criterion']='shaft_strength'
    errors=audit(b,x)['errors'];assert 'coupon/stale/synthetic actual system result' in errors
    rows.append(dict(name='actual_coupon_cannot_be_relabelled_system',rejected=True))
    unrun=out/'test_only_unrun_result.json';dump(unrun,dict(test_only=True,scope='SYSTEM_LOAD_TRANSFER',status='PASS',revision=b['revision'],execution=dict(exit_code=0,command='NOT_EXECUTED_TEST_FIXTURE',actually_executed=False)))
    x['system_evidence'][0].update(ref(unrun));errors=audit(b,x)['errors'];assert 'unrun actual system result' in errors
    rows.append(dict(name='actual_unrun_test_metadata_rejected',rejected=True))
    nonfinite=ROOT/'validation/integrated/negative_nonfinite_actual.json'
    x['system_evidence'][0].update(ref(nonfinite));errors=audit(b,x)['errors'];assert 'nonfinite actual result' in errors
    rows.append(dict(name='actual_NaN_result_rejected',rejected=True))
    dump(out/'summary.json',dict(status='PASS',scope='SOFTWARE NEGATIVE CONTROLS ONLY',controls=rows,part_material_change_invalidated=True,product_release=False,producer=ref(Path(__file__))))
    print(json.dumps(dict(controls=len(rows),status='PASS',product_release=False)))
if __name__=='__main__':main()
