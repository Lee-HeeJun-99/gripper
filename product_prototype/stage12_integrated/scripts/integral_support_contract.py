"""Actual one-piece register/journal, shaft coverage and entire foot support."""
import argparse,json,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,translate,volume,common
from fastener_joint_contract import cylinders,project_interval
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',default='revAK_integral1');a=p.parse_args()
    out=ROOT/'validation/transmission'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());assert d['integrated_motor_support'];refs=d['part_references'];palm=read(REPO/refs['PALM']['path']);plate=read(REPO/refs['F0_MOTOR_PLATE']['path']);cs=cylinders(plate)
    intervals=lambda radius:[project_interval(c,[0,1,0]) for c in cs if abs(c['r']-radius)<1e-6]
    well=intervals(11.01);journal=intervals(4);abutment=intervals(4.8);passage=intervals(2.65)
    assert well and journal and abutment and passage
    coverage=any(v[0]<=-1+1e-6 and v[1]>=3-1e-6 for v in journal)
    rows=[]
    for i in range(3):
        n=f'F{i}_MOTOR_PLATE';s=read(REPO/refs[n]['path']);slab=BRepAlgoAPI_Common(s,box(-160,-160,-7,320,320,.001)).Shape();probe=translate(slab,0,0,-.001);area=volume(slab)/.001;supported=common(palm,probe)/.001
        rows.append(dict(part=n,footprint_area_mm2=area,supported_area_mm2=supported,relative_missing=abs(area-supported)/area))
    checks=dict(actual_pilot_well=any(abs(v[0]+8.5)<1e-6 and abs(v[1]+5.8)<1e-6 for v in well),bearing_journal_covered=coverage,rear_shoulder_diameter=bool(abutment),shaft_passage=bool(passage),entire_feet_supported=all(r['relative_missing']<1e-8 for r in rows),no_obsolete_ground_hardware=not any(n[3:].startswith('CLUTCH_GROUND_') for n in refs),minimum_shaft_covers_clamp_zone=d['minimum_shaft_coverage_margin_mm']>0)
    result=dict(status='INTEGRAL_SUPPORT_GEOMETRY_PASS' if all(checks.values()) else 'INTEGRAL_SUPPORT_GEOMETRY_FAIL',scope='Actual one-piece support, nominal full footprint and supplier minimum shaft coverage only; no loaded strength/material/fit release',candidate=ref(src),producer=ref(out/'producer.py'),checks=checks,pilot_well_Y_mm=well,journal_Y_mm=journal,abutment_Y_mm=abutment,shaft_passage_Y_mm=passage,footprints=rows,nominal_minimum_pilot_tip_gap_mm=.2,proposed_well_depth_tolerance_min_gap_mm=.18,minimum_shaft_coverage_margin_mm=d['minimum_shaft_coverage_margin_mm'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
