"""Bounded Boolean-stage diagnosis of actualP1 nut-thread generation."""
import sys,json,math,shutil
from primary_thread49b import ridge,INT,P
from baseline_registry import ROOT,ref,dump
from incremental_stage1 import translate,bounds,box,volume,solid_count
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49b_ridgeprobe';out.mkdir();shutil.copyfile(__file__,out/'probe.py');s=ridge(INT['minor']/2,INT['major']/2,INT['pitch']/2,-P,8.);rows=[]
 for name,shape in [('raw',s),('translated',translate(s,0,0,.8)),('clipped',BRepAlgoAPI_Common(translate(s,0,0,.8),box(-3,-3,1.3,6,6,4.7)).Shape())]:
  rows.append(dict(stage=name,volume_mm3=volume(shape),solids=solid_count(shape),bounds_mm=None if shape.IsNull() else bounds(shape)))
 dump(out/'summary.json',dict(status='ACTUAL_P1_THREAD_BOOLEAN_STAGE_DIAGNOSTIC',rows=rows));print(json.dumps(rows))
if __name__=='__main__':main()
