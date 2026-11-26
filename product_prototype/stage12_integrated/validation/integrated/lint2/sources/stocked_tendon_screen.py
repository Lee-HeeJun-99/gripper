"""Discrete actual supplier constructions, not a diameter/force parameter scan.
No 1x19 rating or solid-rod EA is transferred to a7x7 stranded rope.
"""
import argparse,json,math,sys,shutil
from pathlib import Path
from baseline_registry import ROOT,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/tendon'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    rows=[];checks=[];source='https://www.carlstahl-technocables.com/gb/en/products/wire-ropes-and-strands/stainless-steel-wire-rope/'
    for item,diameter,breaking,kg_km in [('SE000005',.45,151.,.8),('SE000006',.54,235.,1.2)]:
        radius=10.93+diameter/2
        for part,x,z in [('F0_DRUM',80,20),('F0_IDLER',44,25)]:
            path=S1/'cad/parts/revAA_mbd1'/(part+'.step');shape=read(path)
            wire=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),radius,diameter/2).Shape()
            v=common(wire,shape);checks.append(dict(item=item,part=ref(path),nominal_full_seated_torus_common_mm3=v,status='PASS' if abs(v)<1e-8 else 'FAIL'))
        rows.append(dict(item=item,construction='AISI3166x7-WSC',nominal_diameter_mm=diameter,manufacturer_minimum_breaking_N=breaking,
            catalog_nominal_linear_mass_kg_m=kg_km/1000,design_length_bare_rope_nominal_mass_kg=kg_km/1000*.190809325,
            bare_rope_arithmetic_half_minimum_N=breaking/2,minimum_floor_42d_margin_mm=21.85-42*diameter,
            zero_stiffness_seated_radius_interval_mm=[10.925+diameter/2,10.93+diameter/2],
            compatible_with_CURRENT_incoming_diameter_acceptance=.48<=diameter<=.52,
            unknown=['actual supplied diameter tolerance','finished NI000032 compatibility/pullout','EA, fatigue, friction and bending loss'],
            disposition='INVESTIGATE_SMALLER_STOCK_VARIANT_NOT_ADOPTED' if diameter==.45 else 'REQUIRES_LARGER_PULLEYS_TO_MEET42d_RECOMMENDATION'))
    result=dict(status='SCREEN_COMPLETE_NOT_A_RELEASE',scope='DISCRETE SUPPLIER STOCK / NOMINAL SEATED GEOMETRY ONLY',supplier_source=source,
        source_read_date='2026-11-26',rows=rows,geometry_checks=checks,producer=ref(out/'producer.py'),adopted=False,criteria_changed=False,
        warning='Half minimum breaking force is NOT a certified working load. Published bare rope rating excludes finished ends/bending/fatigue. No diameter tolerance or EA invented. Current0.50custom rope design unchanged.')
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
