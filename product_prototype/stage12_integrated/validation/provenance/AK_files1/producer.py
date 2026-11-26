"""Actual final-candidate file/hash audit; never promotes CAD/FEM to release."""
import argparse,json,shutil
from pathlib import Path
from baseline_registry import ROOT,REPO,ref,dump,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--profile',choices=['AJ','AK'],default='AJ');a=p.parse_args()
    out=ROOT/'validation/provenance'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    paths={
        'candidate':'cad/exports/revAJ_idler1/summary.json',
        'geometry':'validation/stage1/AJ_geometry1/summary.json',
        'wire':'validation/stage1/AJ_wire_motion1/summary.json',
        'drive':'validation/stage1/AJ_drive_motion1/summary.json',
        'stack':'validation/transmission/AJ_idler_stack1/summary.json',
        'footprint':'validation/stage1/AJ_footprints1/summary.json',
        'BOM':'bom/revAJ_identity1/summary.json',
        'binding':'models/geometry/AJ_binding1/summary.json',
        'readiness':'validation/integrated/AJ_readiness2/summary.json',
        'FEM_convergence':'validation/convergence/AI_tab_convergence2/summary.json',
        'tolerance':'validation/alignment/AH_pilot_bounds2/summary.json'}
    if a.profile=='AK':
        paths=dict(candidate='cad/exports/revAK_integral2/summary.json',geometry='validation/stage1/AK_geometry2/summary.json',wire='validation/stage1/AK_wire_motion2/summary.json',drive='validation/stage1/AK_drive_motion2/summary.json',footprint='validation/transmission/AK_support2/summary.json',BOM='bom/revAK_identity1/summary.json',binding='models/geometry/AK_binding1/summary.json',readiness='validation/integrated/AK_readiness1/summary.json',collet='validation/transmission/AK_collet_requirements1/summary.json',bypass='validation/overload/AK_bypass1/summary.json',FEM_convergence='validation/convergence/AI_tab_convergence2/summary.json')
    docs={k:json.loads((ROOT/v).read_text()) for k,v in paths.items()};errors=[];checked={}
    def walk(value):
        if isinstance(value,dict):
            if isinstance(value.get('path'),str) and 'SHA256' in value:
                path=Path(value['path'])
                if path.is_absolute():
                    if not any(path.is_relative_to(Path(base)) for base in ('/tmp/regrip_stage1_ocp','/tmp/regrip_stage2_fem')):
                        errors.append('unapproved external reference');return
                else:
                    if '..' in path.parts:errors.append('unsafe relative reference');return
                    path=REPO/path
                if not path.is_file():errors.append('missing '+str(path));return
                digest=checked.setdefault(str(path),sha(path))
                if digest!=value['SHA256']:errors.append('stale '+str(path))
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    for d in docs.values():walk(d)
    expected=ref(ROOT/paths['candidate'])
    for key in (('geometry','wire','drive','stack','footprint','BOM','binding','readiness') if a.profile=='AJ' else ('geometry','wire','drive','footprint','BOM','binding','readiness','collet','bypass')):
        if docs[key].get('candidate')!=expected:errors.append(key+' wrong candidate')
    inventory=250 if a.profile=='AJ' else 235
    if docs['candidate']['parts']!=inventory or len(docs['candidate']['part_references'])!=inventory:errors.append('wrong final inventory')
    if docs['readiness']['status']!='INTEGRATED_NOT_QUALIFIED':errors.append('unexpected release promotion')
    if docs['FEM_convergence']['stress_converged'] is not False:errors.append('lost stress FAIL')
    count=len(errors)
    walk(dict(expected,SHA256='0'*64));wrong_hash_rejected=len(errors)>count;errors=errors[:count]
    walk(dict(path='product_prototype/stage12_integrated/NO_SUCH_EXECUTED_RESULT.json',SHA256='0'*64));missing_rejected=len(errors)>count;errors=errors[:count]
    if not wrong_hash_rejected or not missing_rejected:errors.append('negative controls failed')
    result=dict(status='FILE_AND_SCOPE_AUDIT_PASS' if not errors else 'FILE_AND_SCOPE_AUDIT_FAIL',scope='Actual file identity and honest bounded scope only, NOT integrated release',errors=errors,checked_files=len(checked),inputs={k:ref(ROOT/v) for k,v in paths.items()},producer=ref(out/'producer.py'),controls=dict(wrong_hash_rejected=wrong_hash_rejected,missing_result_rejected=missing_rejected),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],errors=errors,checked_files=len(checked)),indent=2))
    raise SystemExit(0 if not errors else 2)
if __name__=='__main__':main()
