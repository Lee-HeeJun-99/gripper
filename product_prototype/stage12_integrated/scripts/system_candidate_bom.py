"""Complete same-candidate part identity/BOM, never a manufacturing release."""
import argparse,csv,json,shutil
from baseline_registry import ROOT,S1,REPO,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--geometry',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'bom'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text())
    gs=ROOT/'validation/stage1'/a.geometry/'summary.json';g=json.loads(gs.read_text());assert g['candidate']==ref(src)
    geom={r['part_ID']:r for r in json.loads((REPO/g['parts']['path']).read_text())}
    old={r['part_ID']:r for r in csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open())};rows=[]
    for n,r in d['part_references'].items():
        assert geom[n]['STEP']==r
        previous=old.get(n,{})
        material=previous.get('material','CUSTOM candidate material/specification NOT QUALIFIED')
        process=previous.get('manufacturing_process',previous.get('process','CAD candidate: machining/process qualification required'))
        if 'CLUTCH_BEARING' in n:material='NSK688A interface candidate8x16x4; actual bearing procurement/grade certificate pending'
        if 'CLUTCH_SPRING' in n:material='CUSTOM DISC SPRING: material, force/deflection, fatigue/temperature NOT QUALIFIED'
        if 'CLUTCH_LINER' in n:material='FRICTION LINER NOT SELECTED; no coefficient/rating invented'
        if 'CLUTCH_INPUT_HUB' in n or 'CLUTCH_GROUND_SPINDLE' in n:material='Machined metal candidate; grade/certificate/strength pending'
        is_changed=not previous or previous.get('STEP_SHA256')!=r['SHA256']
        if is_changed:process='REDEFINE from actual STEP and candidate definition; prior-revision process is NOT released for this changed shape'
        if d.get('geometry',{}).get('thread','').startswith('M3'):
            if n.endswith('IDLER_AXLE'):
                process='Custom turn integral shoulder and0.1mm runout fillets; M3x0.5-6g actual thread/core/gauge qualification pending; '+json.dumps(d['geometry'])
            elif n.endswith('IDLER_NUT'):
                material='M3 nut grade/supplier NOT QUALIFIED';process='M3x0.5-6H; AF5.5xheight2.4 nominal envelope, not old M2 nut'
            elif n.endswith('IDLER_CLAMP_WASHER'):
                material='Custom metal washer grade NOT QUALIFIED';process='Turn OD5.5/ID3.1/thickness0.5mm; nominal actual STEP, not old M2 clearance washer'
        rows.append(dict(part_ID=n,quantity=1,revision=a.candidate,STEP=r['path'],STEP_SHA256=r['SHA256'],STL=str((REPO/r['path']).with_suffix('.stl').relative_to(REPO)),volume_m3=geom[n]['volume_m3'],material_requirement=material,material_certificate='',process_requirement=process,changed_from_AA=is_changed,
            interface_qualification='Changed part/interface NOT QUALIFIED' if is_changed else 'Geometry identity only; changed system loads/contacts invalidate old physical conclusions',physical_mass_kg='',release='CANDIDATE_ONLY_NOT_MANUFACTURING_RELEASE'))
    assert len(rows)==len(set(r['part_ID'] for r in rows))==len(d['part_references'])
    with (out/'CANDIDATE_BOM.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    dump(out/'summary.json',dict(status='COMPLETE_CANDIDATE_IDENTITY_BOM_CREATED',scope='Actual parts and material requirements only, no certified procurement or manufacturing/physical release',revision=a.candidate,parts=len(rows),candidate=ref(src),geometry=ref(gs),BOM=ref(out/'CANDIDATE_BOM.csv'),producer=ref(out/'producer.py'),whole_system_release=False))
    print(json.dumps(dict(parts=len(rows),revision=a.candidate)))
if __name__=='__main__':main()
