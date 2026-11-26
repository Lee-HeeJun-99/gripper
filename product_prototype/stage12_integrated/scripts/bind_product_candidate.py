"""Bind unchanged drive/Finger geometry to a new Palm-only candidate.
No prior loaded result or release is copied; kinematic subset scope is explicit.
"""
import argparse,json,shutil
from baseline_registry import ROOT,REPO,ref,dump,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'models/geometry'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAI_tabs1/summary.json';parent=ROOT/'cad/exports/revAH_pilot2/summary.json';s=json.loads(source.read_text());d=json.loads(parent.read_text())
    assert s['parent']==ref(parent);assert set(s['part_references'])==set(d['part_references'])
    unchanged=[]
    for n,r in s['part_references'].items():
        assert sha(REPO/r['path'])==r['SHA256']
        if n!='PALM':assert r==d['part_references'][n];unchanged.append(n)
    assert all(s['checks'].values()) and s['new_minus_old_volume_mm3']==0 and not s['interferences']
    result=dict(status='PART_MODEL_IDENTITY_BINDING_PASS',scope='Actual unchanged geometry identities and declared interfaces only, not a physical release',candidate=ref(source),drive_definition=ref(parent),unchanged_part_IDs=unchanged,
        drive_model=d['torque_model'],register_design=d['register_requirement'],
        permitted_reuse=['Unchanged component geometric identities','Prescribed AH drive/wire collision screens: unchanged non-Palm geometry, new Palm subset of old Palm'],
        forbidden_reuse=['Loaded whole-Palm/support stiffness','Actual loaded Finger trajectories or forces','Material/strength/protected torque or system PASS','Unmeasured manufacturing or hardware capability'],
        producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result)
    dump(ROOT/'CURRENT_CANDIDATE.json',dict(revision='revAI_tabs1',adopted=False,definition=ref(source),model_binding=ref(out/'summary.json'),official_baseline_unchanged='revAA_heel_relief2',release='CANDIDATE_ONLY_INTEGRATED_NOT_QUALIFIED',hardware='HARDWARE_NOT_MEASURED',powered_operation='NOT_AUTHORIZED'))
    print(json.dumps(dict(status=result['status'],unchanged_parts=len(unchanged),revision='revAI_tabs1')))
if __name__=='__main__':main()
