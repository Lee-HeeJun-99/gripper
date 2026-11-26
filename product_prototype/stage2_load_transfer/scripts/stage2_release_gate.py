"""Fail-closed Stage2 evidence gate. Coupon PASS is NOT a system release.
This verifies evidence consistency, not truth of an unreviewed certificate.
"""
import argparse,hashlib,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REQUIRED={
 'cad_model_match':'ANALYTICAL','physical_mass_inertia':'ANALYTICAL',
 'tendon_force_stroke':'ANALYTICAL','motor_running_torque_speed':'ANALYTICAL',
 'shaft_strength':'ANALYTICAL','coupling_capacity':'ANALYTICAL',
 'pin_drum_strength':'ANALYTICAL','bearing_ratings_reactions':'ANALYTICAL',
 'housing_shoulder_retention':'ANALYTICAL','tendon_stiffness_strength':'ANALYTICAL',
 'terminal_retention':'ANALYTICAL','idler_load_drag':'ANALYTICAL',
 'finger_structure':'ANALYTICAL','root_palm_strength':'ANALYTICAL',
 'continuous_load_path':'NUMERICAL','static_dynamic_consistency':'NUMERICAL',
 'numerical_convergence':'NUMERICAL','qualified_worst_case':'ANALYTICAL',
 'changed_stage1_revalidation':'ANALYTICAL','stage3_handoff':'ANALYTICAL'}
CASE='revAA_heel_relief2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(doc,root,expected,allow_test=False):
    errors=[]
    if doc.get('test_only') and not allow_test:errors.append('synthetic test fixture cannot release product')
    if doc.get('baseline')!=expected:errors.append('baseline CAD/model hash mismatch')
    if doc.get('collision_models_removed') is not False or doc.get('qv_forced') is not False:errors.append('missing/invalid physical-preservation declaration')
    records=doc.get('records',{})
    if set(records)!=set(REQUIRED):errors.append('required criterion set missing/extra')
    for key,domain in REQUIRED.items():
        rec=records.get(key,{})
        if rec.get('status')!='PASS':errors.append(key+': not qualified');continue
        if rec.get('domain')!=domain or rec.get('scope')!='SYSTEM_LOAD_TRANSFER':errors.append(key+': coupon/wrong domain')
        if rec.get('material_basis') not in ('manufacturer_minimum','certified_lot','not_material_dependent'):errors.append(key+': unsupported allowable basis')
        for group in ('evidence','source','model'):
            refs=rec.get(group,{})
            if not refs:errors.append(key+': absent '+group)
            for relative,digest in refs.items():
                path=Path(relative)
                if path.is_absolute() or '..' in path.parts:errors.append(key+': unsafe evidence path');continue
                if not (root/path).is_file() or sha(root/path)!=digest:errors.append(key+': missing/stale '+group+' '+relative)
        metrics=rec.get('metrics',[])
        if not metrics:errors.append(key+': absent quantitative checks')
        for m in metrics:
            value,limit=m.get('value'),m.get('maximum')
            if not isinstance(value,(int,float)) or not isinstance(limit,(int,float)) or not math.isfinite(value) or not math.isfinite(limit) or value<0 or limit<0 or value>limit or not m.get('unit'):
                errors.append(key+': failed/nonfinite/absent metric')
        if key=='numerical_convergence':
            mm={x.get('name'):x for x in metrics}
            for name,maxval in [('time_relative',.001),('mesh_relative',.01)]:
                if name not in mm or mm[name].get('maximum',float('inf'))>maxval:errors.append(key+': absent/relaxed '+name)
    global_error=any(e.split(':')[0] not in REQUIRED for e in errors)
    return dict(status='STAGE2_DIGITAL_RELEASE_PASS' if not errors else 'STAGE2_NOT_QUALIFIED',
        analytical_pass=not global_error and not any(e.split(':')[0] in {k for k,v in REQUIRED.items() if v=='ANALYTICAL'} for e in errors),
        numerical_pass=not global_error and not any(e.split(':')[0] in {k for k,v in REQUIRED.items() if v=='NUMERICAL'} for e in errors),
        hardware_status='NOT MEASURED; never inferred by digital validator',errors=errors)
def expected_baseline():
    s1=ROOT.parent/'stage1_manufacturing'
    return dict(case=CASE,assembly_SHA256=sha(s1/'cad/assembly/revAA_mbd1/ASSEMBLY.step'),
        BOM_SHA256=sha(s1/'bom/revAA_mbd1/STAGE1_BOM.csv'),criteria_SHA256=sha(ROOT/'models/analytical/criteria.json'))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    registry=ROOT/'models/analytical/release_registry.json'
    result=validate(json.loads(registry.read_text()),ROOT,expected_baseline())
    result.update(source_SHA256=sha(Path(__file__)),registry_SHA256=sha(registry),command='python scripts/stage2_release_gate.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='STAGE2_DIGITAL_RELEASE_PASS' else 2)
if __name__=='__main__':main()
