"""Actual BRep thin-slice net section audit. Polar area moment != torsion J."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from extract_geometry import ROOT,S1,sha,load,properties
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
def section(shape,y,h):
    slab=BRepPrimAPI_MakeBox(gp_Pnt(60,y-h/2,0),40,h,40).Shape()
    s=BRepAlgoAPI_Common(shape,slab).Shape();v,c,j=properties(s)
    return dict(area_m2=v/(h*.001),centroid_m=c.tolist(),polar_area_m4=j[1,1]/(h*.001))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/shaft'/a.tag;out.mkdir(parents=True,exist_ok=False)
    part=S1/'cad/parts/revAA_mbd1/F0_SHAFT.step';s=load(part);rows=[]
    for label,y in [('grip_flats',-16),('left_runout',-8.75),('left_journal',-6),('pin_hole_centre',2.5),('shoulder_clear',5),('right_runout',14.25)]:
        samples=[dict(slice_mm=h,**section(s,y,h)) for h in (.02,.01,.005)]
        ae=abs(samples[-1]['area_m2']/samples[-2]['area_m2']-1)
        je=abs(samples[-1]['polar_area_m4']/samples[-2]['polar_area_m4']-1)
        rows.append(dict(label=label,y_mm=y,samples=samples,area_refinement_relative=ae,polar_refinement_relative=je,
            status='PASS' if max(ae,je)<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',case='revAA_heel_relief2',
        scope='ACTUAL SHAFT NET SECTIONS, NOT NOTCH STRESS OR TORSIONAL STRENGTH',rows=rows,
        source_SHA256=sha(Path(__file__)),STEP_SHA256=sha(part),
        warning='Polar area moment of a perforated/non-circular section is NOT Saint-Venant torsion constant; no torque capacity certified',
        command='PYTHONPATH=/tmp/regrip_stage1_ocp python scripts/shaft_sections.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
