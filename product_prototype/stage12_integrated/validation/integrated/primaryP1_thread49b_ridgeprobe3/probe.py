"""Bounded Boolean-stage diagnosis of actualP1 nut-thread generation."""
import sys,json,math,shutil
from primary_thread49b import ridge,INT,P
from baseline_registry import ROOT,ref,dump
from incremental_stage1 import translate,bounds,box,volume,solid_count,read,fuse,canonical,cut
from baseline_registry import REPO
from validate_thread49 import classification
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49b_ridgeprobe3';out.mkdir();shutil.copyfile(__file__,out/'probe.py');s=ridge(INT['minor']/2,INT['major']/2,INT['pitch']/2,-P,8.);rows=[]
 for name,shape in [('raw',s),('translated',translate(s,0,0,.8)),('clipped',BRepAlgoAPI_Common(translate(s,0,0,.8),box(-3,-3,1.3,6,6,4.7)).Shape())]:
  rows.append(dict(stage=name,volume_mm3=volume(shape),solids=solid_count(shape),bounds_mm=None if shape.IsNull() else bounds(shape)))
 d=json.loads((ROOT/'cad/exports/primaryP1_profilepin48b/summary.json').read_text());n=translate(read(REPO/d['part_references']['BENCH_MOUNT_NUT_0']['path']),59,58,-54);inside=BRepAlgoAPI_Common(translate(s,0,0,.8),box(-3,-3,1.3,6,6,4.7)).Shape();u=canonical(fuse(n,inside));co=BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(0,0,1.3),gp_Dir(0,0,1)),2.6,2.167,.433).Shape();cu=canonical(cut(u,co))
 for name,shape in [('oldnut',n),('inside',inside),('union_raw',fuse(n,inside)),('union',u),('cutlower',cu)]:
  rows.append(dict(stage=name,volume_mm3=volume(shape),solids=solid_count(shape),zprobe=[dict(z=z,state=classification(shape,[2.3,0,z])) for z in [1.6+j*.05 for j in range(17)]]))
 dump(out/'summary.json',dict(status='ACTUAL_P1_THREAD_BOOLEAN_STAGE_DIAGNOSTIC',rows=rows));print(json.dumps(rows))
if __name__=='__main__':main()
