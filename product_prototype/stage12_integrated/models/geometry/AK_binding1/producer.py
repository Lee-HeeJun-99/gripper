"""Bind actual AK assembly to same-case tests, never transfer system approval."""
import argparse,json,shutil
from baseline_registry import ROOT,REPO,ref,dump,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'models/geometry'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(src.read_text())
    refs=d['part_references'];assert len(refs)==d['parts']==235
    tests={}
    for rel,expected in [('stage1/AK_geometry2','PASS'),('transmission/AK_support2','INTEGRAL_SUPPORT_GEOMETRY_PASS'),('stage1/AK_drive_motion2','SAMPLED_DRIVE_CLEARANCE_PASS'),('stage1/AK_wire_motion2','WIRE_RIGID_HARDWARE_SCREEN_PASS')]:
        path=ROOT/'validation'/rel/'summary.json';v=json.loads(path.read_text());assert v['candidate']==ref(src) and v['status']==expected
        tests[rel]=ref(path)
    old=json.loads((ROOT/'cad/exports/revAJ_idler1/summary.json').read_text());identical=[]
    for n,r in refs.items():
        assert sha(REPO/r['path'])==r['SHA256']
        if n in old['part_references'] and old['part_references'][n]['SHA256']==r['SHA256']:identical.append(n)
    assert all(f'F{i}_IDLER_AXLE' in identical for i in range(3))
    result=dict(status='PART_MODEL_IDENTITY_BINDING_PASS',candidate=ref(src),same_case_geometry_tests=tests,unchanged_from_AJ=identical,
        scope='Identity and bounded geometry only; no inherited complete Stage1/Stage2 approval',
        invalidated=['Motor/support mounting and structural strength','Collet preload, actual contact, axial/torsional retention','Entire Palm support/load and manufacturing/tolerance definition','Full system mass and maximum protected transient load'],producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result)
    dump(ROOT/'CURRENT_CANDIDATE.json',dict(revision=d['revision'],adopted=False,definition=ref(src),model_binding=ref(out/'summary.json'),parts=d['parts'],official_baseline_unchanged='revAA_heel_relief2',release='CANDIDATE_ONLY_INTEGRATED_NOT_QUALIFIED',hardware='HARDWARE_NOT_MEASURED',powered_operation='NOT_AUTHORIZED'))
    print(json.dumps(dict(parts=d['parts'],unchanged=len(identical),status=result['status'])))
if __name__=='__main__':main()
