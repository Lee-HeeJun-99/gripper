"""Independent actual M3 Idler stack/neck inventory; not loaded free-spin."""
import argparse,json,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,cyl
from fastener_joint_contract import cylinders,project_interval
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAJ_idler1/summary.json';d=json.loads(src.read_text());r=d['part_references']
    names=['IDLER_AXLE','IDLER','IDLER_SPACER_L','IDLER_SPACER_R','IDLER_CLAMP_WASHER','IDLER_NUT','IDLER_BRACKET'];s={n:read(REPO/r['F0_'+n]['path']) for n in names};bb={n:bounds(v) for n,v in s.items()}
    cs=cylinders(s['IDLER_AXLE'])
    journal=[project_interval(c,[0,1,0]) for c in cs if abs(c['r']-1.5)<1e-6 and project_interval(c,[0,1,0])[0]>-2.500001]
    collar=[project_interval(c,[0,1,0]) for c in cs if abs(c['r']-2.5)<1e-6]
    neck=[project_interval(c,[0,1,0]) for c in cs if abs(c['r']-1.19)<1e-6]
    assert len(journal)==len(collar)==len(neck)==1,(journal,collar,neck)
    column=BRepAlgoAPI_Common(s['IDLER_BRACKET'],cyl(2.5,(44,-5.8,25),3.2,(0,1,0))).Shape();bc=bounds(column)
    width=lambda n:bb[n][4]-bb[n][1]
    gap=journal[0][1]-journal[0][0]-width('IDLER')-width('IDLER_SPACER_L')-width('IDLER_SPACER_R')
    contacts=[bb['IDLER_NUT'][4]-bb['IDLER_CLAMP_WASHER'][1],bb['IDLER_CLAMP_WASHER'][4]-bc[1],bc[4]-collar[0][0]]
    checks=dict(integral_metal_contact_planes=all(abs(v)<1e-6 for v in contacts),nominal_running_gap=abs(gap-.03)<1e-6,old_loose_shoulder_washer_removed='F0_IDLER_SHOULDER_WASHER' not in r,
        nut_within_declared_full_thread=bb['IDLER_NUT'][1]>=-8.2 and bb['IDLER_NUT'][4]<=-3.5)
    result=dict(status='IDLER_INTEGRAL_STACK_GEOMETRY_PASS' if all(checks.values()) else 'FAIL',scope='Actual native STEP neck/journal/metal stack only, not strength, actual thread fit or loaded free spin',candidate=ref(src),producer=ref(out/'producer.py'),feature_reader=ref(S1/'scripts/fastener_joint_contract.py'),journal_Y_mm=journal[0],collar_Y_mm=collar[0],neck_Y_mm=neck[0],actual_neck_diameter_mm=2.38,bracket_column_bounds_mm=bc,nominal_running_gap_mm=gap,contact_plane_errors_mm=contacts,checks=checks,
        part_count=d['parts'],removed_part_count=3,physical_hardware='NOT MEASURED',remaining=['Thread root and actual6g/6H gauge','Material/certified minimum strength, notch, fatigue','Loaded deformation and matched shims/free-spin','Actual maximum protected tension and friction'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
