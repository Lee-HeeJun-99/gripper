"""Extract an actual RevAI distal tab; root cut is an explicit test boundary."""
import argparse,json,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,export,volume,bounds,solid_count
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'models/fem'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAI_tabs1/summary.json';d=json.loads(source.read_text());part=d['part_references']['PALM']
    s=BRepAlgoAPI_Common(read(REPO/part['path']),box(105,-18,-13,35,22,7)).Shape()
    assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
    export(s,out/'TAB')
    dump(out/'summary.json',dict(status='ACTUAL_TAB_SUBMODEL_CREATED',source=ref(source),Palm=part,STEP=ref(out/'TAB.step'),STL=ref(out/'TAB.stl'),volume_mm3=volume(s),bounds_mm=bounds(s),producer=ref(out/'producer.py'),boundary='Explicit clamped cut X105mm, Y[-18,4], Z[-12,-7]; NOT actual whole-Palm stiffness',load='1N downward on actual annular washer footprint radius1.7..4mm about X127/Y-6.5 at topZ-7mm',material='Assumed E70GPa nu0.33; no actual grade/lot qualification',whole_system_release=False))
    print('Actual finite tab extracted; no strength release')
if __name__=='__main__':main()
