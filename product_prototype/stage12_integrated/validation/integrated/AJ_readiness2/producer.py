"""Fail-closed latest-candidate readiness; existing Stage2 gate remains authority.
Does not construct a fake Stage1 release package or promote bounded CAD/FEM.
"""
import argparse,json,csv,shutil,importlib.util
from baseline_registry import ROOT,S1,S2,REPO,ref,dump,sha
from integrated_release_gate import FROZEN_CRITERIA
spec=importlib.util.spec_from_file_location('existing_s2_gate',S2/'scripts/stage2_release_gate.py');s2=importlib.util.module_from_spec(spec);spec.loader.exec_module(s2)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    current=json.loads((ROOT/'CURRENT_CANDIDATE.json').read_text());source=REPO/current['definition']['path'];assert sha(source)==current['definition']['SHA256'];d=json.loads(source.read_text())
    bom=ROOT/'bom/revAJ_identity1/CANDIDATE_BOM.csv';rows=list(csv.DictReader(bom.open()));errors=[]
    if set(r['part_ID'] for r in rows)!=set(d['part_references']):errors.append('candidate BOM inventory mismatch')
    for r in rows:
        if d['part_references'][r['part_ID']]['SHA256']!=r['STEP_SHA256'] or sha(REPO/r['STEP'])!=r['STEP_SHA256']:errors.append('stale candidate STEP/BOM '+r['part_ID'])
    criteria=S2/'models/analytical/criteria.json';assert sha(criteria)==FROZEN_CRITERIA
    registry=json.loads((S2/'models/analytical/release_registry.json').read_text())
    verdict=s2.validate(registry,S2,dict(case=d['revision'],assembly_SHA256=d['assembly']['SHA256'],BOM_SHA256=sha(bom),criteria_SHA256=sha(criteria)))
    errors+=['stage2: '+e for e in verdict['errors']]
    stage1_ref=current.get('stage1_release')
    if not stage1_ref:errors.append('No same-revision full Stage1 release reference; do not reuse RevAA24/24')
    else:
        path=REPO/stage1_ref['path']
        if not path.is_file() or sha(path)!=stage1_ref['SHA256']:errors.append('Missing/stale same-revision Stage1 result')
        else:
            proof=json.loads(path.read_text())
            if proof.get('case')!=d['revision'] or proof.get('status')!='STAGE1_DESIGN_RELEASE_PASS':errors.append('Wrong Stage1 revision/status')
    if not current.get('system_evidence'):errors.append('No complete candidate-matched SYSTEM_LOAD_TRANSFER evidence references')
    # Existing gate is deliberately exercised on real candidate identity;
    # AA/coupon records cannot silently satisfy the new candidate.
    result=dict(status='INTEGRATED_NOT_QUALIFIED' if errors else 'READINESS_CLEAR_NOT_A_RELEASE',revision=d['revision'],scope='Actual latest candidate source/BOM readiness and existing Stage2 gate, NOT a release',errors=errors,stage2=verdict,
        candidate=ref(source),BOM=ref(bom),criteria=ref(criteria),producer=ref(out/'producer.py'),existing_stage2_gate=ref(S2/'scripts/stage2_release_gate.py'),official_baseline_preserved=True,hardware_status='HARDWARE_NOT_MEASURED',manufacturing_status='MANUFACTURING_PROCESS_NOT_QUALIFIED',powered_status='POWERED_OPERATION_NOT_AUTHORIZED')
    dump(out/'summary.json',result);dump(ROOT/'CANDIDATE_RELEASE_STATUS.json',result);print(json.dumps(dict(status=result['status'],revision=d['revision'],errors=len(errors),criteria_unchanged=True)))
if __name__=='__main__':main()
