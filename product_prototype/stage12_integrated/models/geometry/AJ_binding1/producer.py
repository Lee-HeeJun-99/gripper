"""Bind the latest actual product without combining different-revision PASSs."""
import json,shutil
from baseline_registry import ROOT,REPO,ref,dump,sha
def main():
    out=ROOT/'models/geometry/AJ_binding1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAJ_idler1/summary.json';drive=ROOT/'cad/exports/revAH_pilot2/summary.json';finger=ROOT/'cad/exports/revAD_funnel1/summary.json'
    d=json.loads(source.read_text());old=json.loads(drive.read_text());ad=json.loads(finger.read_text());same_drive=[];same_finger=[]
    for n,r in d['part_references'].items():
        assert sha(REPO/r['path'])==r['SHA256']
        if n[3:].startswith(('MOTOR','CLUTCH','DRUM')):
            assert r==old['part_references'][n];same_drive.append(n)
        if n[3:].startswith(('SKIN','RAIL_','ROOT_','TERMINAL_')):
            assert r==ad['part_references'][n];same_finger.append(n)
    ai=ROOT/'cad/exports/revAI_tabs1/summary.json';aid=json.loads(ai.read_text())
    assert d['part_references']['PALM']==aid['part_references']['PALM']
    result=dict(status='PART_MODEL_IDENTITY_BINDING_PASS',scope='Actual part identity and model definitions only; no loaded/system approval inheritance',candidate=ref(source),drive_definition=ref(drive),finger_definition=ref(finger),Palm_definition=ref(ai),same_drive_part_IDs=same_drive,same_finger_part_IDs=same_finger,
        torque_model=d['torque_model'],register_requirements=d['register_requirement'],
        changed_idler='New M3/2.38mm-neck integral shoulder/washer/nut; actual strength, preload and fatigue must be revalidated',
        invalidated=['Full Palm/support/Finger loaded response','Idler strength/thread/preload/contact/drag','Complete mass/inertia and protected maximum','Full Stage1 motion/tolerance/manufacturing/assembly and Stage2 system release'],producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result)
    dump(ROOT/'CURRENT_CANDIDATE.json',dict(revision='revAJ_idler1',adopted=False,definition=ref(source),model_binding=ref(out/'summary.json'),parts=d['parts'],official_baseline_unchanged='revAA_heel_relief2',release='CANDIDATE_ONLY_INTEGRATED_NOT_QUALIFIED',hardware='HARDWARE_NOT_MEASURED',powered_operation='NOT_AUTHORIZED'))
    print(json.dumps(dict(parts=d['parts'],same_drive_parts=len(same_drive),same_finger_parts=len(same_finger),adopted=False)))
if __name__=='__main__':main()
