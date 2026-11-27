"""Bounded actual local trimmed face pair offaxis takeup;no wholethread root."""
import json,sys,math,time,os,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds
from validate_nutseat46c import rotate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.TopoDS import TopoDS
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRepLProp import BRepLProp_SLProps

def faces(s):
 ff=[];ex=TopExp_Explorer(s,TopAbs_FACE)
 while ex.More():ff.append(TopoDS.Face_s(ex.Current()));ex.Next()
 return ff

def main():
 out=ROOT/'validation/integrated/primaryP1_partial54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_offaxis54/summary.json';src=json.loads(sp.read_text());cp=REPO/src['candidate']['path'];assert sha(cp)==src['candidate']['SHA256'];cad=json.loads(cp.read_text());r=src['rows'][0];x,y=-59.,-58.;off=r['relative_transverse_offset_mm'];bolt=translate(rotate(read(REPO/r['bolt_reference']['path']),x,y,r['bolt_yaw_rad']),*off,r['opening_mm']);nut=rotate(read(REPO/r['nut_reference']['path']),x,y,r['nut_yaw_rad']);bf=faces(bolt)[r['bolt_face_index']];p=np.array(r['nut_material_point_mm']);v=BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex();nf=None
 for i,f in enumerate(faces(nut)):
  bb=np.array(bounds(f))
  if np.linalg.norm(np.maximum(np.maximum(bb[:3]-p,p-bb[3:]),0))>1e-6:continue
  d=BRepExtrema_DistShapeShape(v,f);d.Perform()
  if d.Value()<1e-7:nf=f;nfi=i;break
 assert nf is not None
 def journal(row):
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 rows=[]
 def query(opening,label):
  assert not(ROOT/'runtime/STOP').exists();journal(dict(state='START',operation='ONE_LOCAL_TRIMMED_FACE_PAIR_DISTANCE',opening_mm=opening,label=label));t=time.monotonic();b=translate(bf,0,0,opening-r['opening_mm']);d=BRepExtrema_DistShapeShape(b,nf);d.Perform();assert d.IsDone();pa=d.PointOnShape1(1);pb=d.PointOnShape2(1);a=np.array([pa.X(),pa.Y(),pa.Z()]);bpt=np.array([pb.X(),pb.Y(),pb.Z()]);row=dict(state='COMPLETE',opening_mm=opening,label=label,distance_mm=d.Value(),bolt_nearest_mm=a.tolist(),nut_nearest_mm=bpt.tolist(),bolt_support=str(d.SupportTypeShape1(1)),nut_support=str(d.SupportTypeShape2(1)),elapsed_s=time.monotonic()-t,solutions=d.NbSolution());rows.append(row);journal(row);return row
 lo=.015;hi=.055;query(lo,'initial');query(hi,'upper')
 if rows[0]['distance_mm']>1e-7 and rows[-1]['distance_mm']<1e-7:
  for k in range(18):
   m=(lo+hi)/2;r0=query(m,f'bisection{k}')
   if r0['distance_mm']>1e-7:lo=m
   else:hi=m
  query(lo,'last_separated');query(hi,'first_local_touch')
 result=dict(status='ACTUAL_P1_OFFAXIS_LOCAL_PARTIAL_FLANK_TAKEUP_BRACKET_NOT_EQUILIBRIUM',candidate=ref(cp),source=ref(sp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),bolt_part=r['bolt_reference'],nut_part=r['nut_reference'],bolt_face_index=r['bolt_face_index'],nut_face_index=nfi,relative_transverse_offset_mm=off,bolt_yaw_rad=r['bolt_yaw_rad'],nut_yaw_rad=r['nut_yaw_rad'],initial_actual_face_gap_mm=rows[0]['distance_mm'],local_touch_bracket_mm=[lo,hi],bracket_width_mm=hi-lo,rows=rows,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ONE actual trimmed flank pair only;otherturns,crest/root,endchamfer,bore/cage/pin/guide may contact earlier','Bisection threshold1e-7mm is numerical gap threshold,not material tolerance or pressurecapacity','Distance zero cannot distinguish crossing from valid common-normal contact;must bind supportfeatures and admissible contact normalcones','No wholethread Booleanroot orfull128partassembly/operatingstatics/convergence/energycertification'])
 dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ['status','initial_actual_face_gap_mm','local_touch_bracket_mm','bracket_width_mm']}))
if __name__=='__main__':main()
