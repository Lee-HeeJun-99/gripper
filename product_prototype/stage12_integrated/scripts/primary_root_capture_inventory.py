"""Read actual P1 bolt/bore finite surfaces before a capture design decision."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,translate
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_seated22/summary.json';s=json.loads(src.read_text());refs=s['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());names=['F0_ROOT_BACK','OPEN_FRAME']+[f'F0_RF{i}_{k}' for i in range(2) for k in ['BOLT','NUT']];parts={n:read(REPO/refs[n]['path']) for n in names};surfaces={}
 for name,shape in parts.items():
  rows=[];it=TopExp_Explorer(shape,TopAbs_FACE)
  while it.More():
   face=TopoDS.Face_s(it.Current());a=BRepAdaptor_Surface(face)
   if a.GetType()==GeomAbs_Cylinder:
    c=a.Cylinder();p=c.Location();d=c.Axis().Direction();rows.append(dict(radius_mm=c.Radius(),axis_point_mm=[p.X(),p.Y(),p.Z()],axis_direction=[d.X(),d.Y(),d.Z()],bounds_mm=bounds(face)))
   it.Next()
  surfaces[name]=rows
 rows=[]
 for shift in [0,.19,.2,.21,.39,.4,.41,-.21,-.41,-99.536999856]:
  moved=translate(parts['F0_ROOT_BACK'],0,shift,0);rows.append(dict(root_Y_shift_mm=shift,Root_Frame_common_mm3=common(moved,parts['OPEN_FRAME']),Root_bolt_common_mm3=[common(moved,parts[f'F0_RF{i}_BOLT']) for i in range(2)]))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_BOLT_CAPTURE_INVENTORY',candidate=ref(src),parts={n:refs[n] for n in names},cylinders=surfaces,translation_queries=rows,actual_changed_CAD=[],newly_qualified_system_gate_ids=[],whole_system_release=False,conclusion='Existing finite RF shanks and bores provide omitted potential lateral bearing, NOT a frictionless freeY product. Axial-only connectors omit this. Smooth nominal shaft envelope does not certify thread flank/core/material or tilt/compliance. Positive integral Frame shoulders can transfer Y outside flexible span without relying on threaded shear.',limitations=['Translation samples against stationary actual bolt solids only; bolts have clearance and may move/tilt. Not CCD, stress, thread engagement or elastic equilibrium.','Far endpoint no collision does not prove a feasible path through bolts; first local collision matters.']))
if __name__=='__main__':main()
