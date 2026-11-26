"""Fail-closed cross-stage audit. No automatic promotion of bounded studies."""
import argparse,importlib.util,json,math,sys
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,S2,sha,ref,dump,integrity
spec=importlib.util.spec_from_file_location('s2gate',S2/'scripts/stage2_release_gate.py')
s2=importlib.util.module_from_spec(spec);spec.loader.exec_module(s2)
FROZEN_CRITERIA='f7d850c52e0ec9082f01fb3f81bee979ece9ade4f4b5ce2c274e9c0aa4ed3baa'
def finite(x):
    if isinstance(x,float):return math.isfinite(x)
    if isinstance(x,dict):return all(finite(v) for v in x.values())
    if isinstance(x,list):return all(finite(v) for v in x)
    return True
def check_contract(doc):
    errors=[]
    if not finite(doc):errors.append('nonfinite data')
    if not doc.get('revision') or doc.get('stage1_revision')!=doc.get('revision') or doc.get('stage2_revision')!=doc.get('revision'):errors.append('different revision')
    if doc.get('hardware_status')!='HARDWARE_NOT_MEASURED':errors.append('unsupported hardware claim')
    if doc.get('powered_status')!='POWERED_OPERATION_NOT_AUTHORIZED':errors.append('unsupported powered claim')
    evidence=doc.get('system_evidence',[])
    seen=set()
    for r in evidence:
        identity=(r.get('path'),r.get('SHA256'))
        if identity in seen:errors.append('duplicate evidence')
        seen.add(identity)
        if r.get('scope')!='SYSTEM_LOAD_TRANSFER':errors.append('coupon promotion')
        if r.get('executed') is not True:errors.append('unrun test')
        if r.get('material_basis') not in ('manufacturer_minimum','certified_lot','not_material_dependent'):errors.append('unsupported material')
        if r.get('revision')!=doc.get('revision'):errors.append('stale evidence revision')
        p=Path(r.get('path',''))
        if p.is_absolute() or '..' in p.parts or not (REPO/p).is_file() or sha(REPO/p)!=r.get('SHA256'):errors.append('missing/stale system evidence')
    if not evidence:errors.append('missing system evidence')
    return errors
def audit(baseline,contract):
    errors=integrity(baseline)+check_contract(contract)
    if contract.get('revision')!=baseline['revision']:errors.append('contract/baseline revision mismatch')
    stage1=json.loads((REPO/baseline['stage1_release']['path']).read_text())
    if stage1.get('case')!=baseline['revision'] or stage1.get('status')!='STAGE1_DESIGN_RELEASE_PASS':errors.append('stage1 wrong revision/status')
    if len(stage1.get('criteria',[]))!=24 or not all(x.get('passed') is True for x in stage1.get('criteria',[])):errors.append('stage1 missing/failed criteria')
    # Reuse Stage1 proof chain and actual package hashes, without regenerating CAD.
    for evidence in stage1.get('evidence',[]):
        p=S1/evidence['path']
        if not p.is_file() or sha(p)!=evidence['sha256']:errors.append('stage1 stale proof '+evidence['path'])
    package=S1/'cad/assembly'/baseline['package']/'summary.json'
    pkg=json.loads(package.read_text())
    if sha(package)!=stage1.get('package_SHA256'):errors.append('stage1 stale package')
    if pkg.get('case')!=baseline['revision']:errors.append('stage1 package wrong revision')
    if sha(S1/pkg['assembly_STEP'])!=baseline['assembly']['SHA256']:errors.append('stage1 assembly differs from baseline')
    if sha(S1/pkg['BOM'])!=baseline['BOM']['SHA256']:errors.append('stage1 BOM differs from baseline')
    case=S1/'cad/exports'/baseline['revision']/'summary.json'
    if not case.is_file() or sha(case)!=stage1.get('source_case_SHA256') or sha(case)!=pkg.get('source_case_SHA256'):errors.append('stage1 stale case definition')
    for name in ('STAGE1_CURRENT_ASSEMBLY_GUIDE.md','STAGE1_CURRENT_MANUFACTURING_DATUMS.md'):
        if sha(S1/'reports'/name)!=sha(S1/'cad/drawings'/baseline['package']/name):errors.append('stage1 changed authority '+name)
    for evidence in stage1.get('evidence',[]):
        proof=json.loads((S1/evidence['path']).read_text());inputs=proof.get('input_sha256',{})
        if isinstance(inputs,dict):
            for name,digest in inputs.items():
                path=Path(name);path=path if path.is_absolute() else S1/path
                if not path.is_file() or sha(path)!=digest:errors.append('stage1 stale proof input '+name)
    for r in pkg['part_files']:
        p=S1/r['path']
        if not p.is_file() or sha(p)!=r['sha256']:errors.append('stage1 missing/stale part '+r['path'])
    registry=json.loads((REPO/baseline['stage2_registry']['path']).read_text())
    if registry.get('hardware_executed') is not False:errors.append('unsupported registry hardware claim')
    verdict=s2.validate(registry,S2,dict(case=baseline['revision'],assembly_SHA256=baseline['assembly']['SHA256'],BOM_SHA256=baseline['BOM']['SHA256'],criteria_SHA256=baseline['criteria']['SHA256']))
    errors+=['stage2: '+e for e in verdict['errors']]
    # Pin method criteria to the inherited frozen values; never trust a new registry maximum.
    criteria=json.loads((REPO/baseline['criteria']['path']).read_text())
    if sha(REPO/baseline['criteria']['path'])!=FROZEN_CRITERIA:errors.append('inherited criteria changed')
    if criteria.get('numerical_time_convergence_relative_max')!=.001 or criteria.get('numerical_mesh_convergence_relative_max')!=.01:errors.append('relaxed inherited convergence criteria')
    # System records must be backed by matching actual result metadata, not
    # merely by manually relabelling a coupon entry in a release registry.
    coverage=set()
    for r in contract.get('system_evidence',[]):
        criterion=r.get('criterion');path=REPO/r.get('path','')
        if criterion not in s2.REQUIRED:errors.append('missing/unknown system criterion');continue
        coverage.add(criterion)
        if not path.is_file():continue
        try:actual=json.loads(path.read_text())
        except (ValueError,OSError):errors.append('system result is not inspectable JSON');continue
        if not finite(actual):errors.append('nonfinite actual result')
        if actual.get('test_only') or actual.get('scope')!='SYSTEM_LOAD_TRANSFER' or actual.get('status')!='PASS' or actual.get('revision')!=baseline['revision']:errors.append('coupon/stale/synthetic actual system result')
        execution=actual.get('execution',{})
        if execution.get('exit_code')!=0 or not execution.get('command') or execution.get('actually_executed') is not True:errors.append('unrun actual system result')
        record=registry.get('records',{}).get(criterion,{})
        if actual.get('material_basis') not in ('manufacturer_minimum','certified_lot','not_material_dependent'):errors.append('unsupported actual material basis')
        for group in ('source','model'):
            actual_refs=actual.get(group,{})
            if not isinstance(actual_refs,dict) or not actual_refs:errors.append('missing actual '+group+' fingerprints');continue
            for p,digest in actual_refs.items():
                relative=Path(p)
                if relative.is_absolute() or '..' in relative.parts or not (REPO/relative).is_file() or sha(REPO/relative)!=digest:errors.append('missing/stale actual '+group)
                if not any((S2/q).resolve()==(REPO/relative).resolve() and value==digest for q,value in record.get(group,{}).items()):errors.append('actual/registry '+group+' mismatch')
        if not any((S2/p).resolve()==path.resolve() and digest==r.get('SHA256') for p,digest in record.get('evidence',{}).items()):errors.append('contract/registry evidence mismatch')
    if coverage!=set(s2.REQUIRED):errors.append('missing full system evidence coverage')
    return dict(status='STAGE1_STAGE2_INTEGRATED_DIGITAL_RELEASE_PASS' if not errors else 'INTEGRATED_NOT_QUALIFIED',
        revision=baseline['revision'],errors=errors,stage2=verdict,hardware_status='HARDWARE_NOT_MEASURED',
        manufacturing_status='MANUFACTURING_PROCESS_NOT_QUALIFIED',powered_status='POWERED_OPERATION_NOT_AUTHORIZED',
        scope='Consistency audit only. Unreviewed evidence cannot establish physical truth.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    b=json.loads((ROOT/'CURRENT_BASELINE.json').read_text());c=json.loads((ROOT/'models/integrated_contract.json').read_text())
    result=audit(b,c);result.update(producer=ref(Path(__file__)),baseline=ref(ROOT/'CURRENT_BASELINE.json'),contract=ref(ROOT/'models/integrated_contract.json'),stage2_gate=ref(S2/'scripts/stage2_release_gate.py'))
    dump(out/'summary.json',result);dump(ROOT/'RELEASE_STATUS.json',result)
    print(json.dumps(result,indent=2));sys.exit(0 if not result['errors'] else 2)
if __name__=='__main__':main()
