"""Actual changed P1 spool floor, source-profile tool reach and additive-only audit.
A turned replacement from stock; this is not a purchased tool/process certificate.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,fuse,cut,translate,export,common,volume,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder,GeomAbs_Torus
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'cad/exports/primaryP1_seated22/summary.json';cad=json.loads(src.read_text());oldsrc=ROOT/'cad/exports/primaryP1_retention20/summary.json';old=json.loads(oldsrc.read_text());spool=read(REPO/cad['part_references']['F0_SPOOL']['path']);original=read(REPO/old['part_references']['F0_SPOOL']['path']);removed=volume(cut(original,spool));added=volume(cut(spool,original));surfaces=[];it=TopExp_Explorer(spool,TopAbs_FACE)
 while it.More():
  f=TopoDS.Face_s(it.Current());ad=BRepAdaptor_Surface(f)
  if ad.GetType()==GeomAbs_Cylinder and 10<ad.Cylinder().Radius()<11.2:surfaces.append(dict(type='Cylinder',radius_mm=ad.Cylinder().Radius(),bounds_mm=bounds(f)))
  if ad.GetType()==GeomAbs_Torus:surfaces.append(dict(type='Torus',major_mm=ad.Torus().MajorRadius(),minor_mm=ad.Torus().MinorRadius(),bounds_mm=bounds(f)))
  it.Next()
 # Reuse the historical .90 flat /R.10 /1.10 overall source form-tool geometry.
 floor=31.;tool=fuse(box(-.5,-.45,floor,1,.9,8),box(-.5,-.55,floor+.1,1,1.1,7.9))
 for y in (-.45,.45):tool=fuse(tool,cyl(.1,(-.5,y,floor+.1),1,(1,0,0)))
 tool=fuse(tool,box(-2.5,-2,floor+8,5,4,30));tooldir=ROOT/'cad/exports/primaryP1_seated_tool1';tooldir.mkdir(exist_ok=False);export(tool,tooldir/'FORM_TOOL');rows=[]
 for dz in (0,.1,.5,1,2,4,8,15):rows.append(dict(radial_withdrawal_mm=dz,retained_material_common_mm3=common(spool,translate(tool,0,0,dz))))
 deeper=common(spool,translate(tool,0,0,-.02));unchanged=sum(cad['part_references'][n]==r for n,r in old['part_references'].items());checks=dict(valid=bool(BRepCheck_Analyzer(spool).IsValid()),only_one_part_changed=unchanged==77,original_pocket_material_preserved=removed<1e-8,positive_floor_addition=added>0,nominal_floor=any(q['type']=='Cylinder' and abs(q['radius_mm']-11)<1e-9 for q in surfaces),tool_reach=max(q['retained_material_common_mm3'] for q in rows)<1e-7,negative_cut=deeper>1e-7)
 result=dict(status='ACTUAL_P1_SEATED_SPOOL_TOOL_AND_GEOMETRY_PASS' if all(checks.values()) else 'ACTUAL_P1_SEATED_SPOOL_TOOL_GEOMETRY_FAIL',candidate=ref(src),parent=ref(oldsrc),producer=ref(out/'producer.py'),tool_STEP=ref(tooldir/'FORM_TOOL.step'),tool_STL=ref(tooldir/'FORM_TOOL.stl'),source_profile=ref(S1/'scripts/broad_groove_tool.py'),checks=checks,added_mm3=added,removed_mm3=removed,unchanged_STEP_parts=unchanged,surfaces=surfaces,approach=rows,deeper_point02_mm3=deeper,nominal_wire_seated_center_radius_mm=11.25,nominal_nipple_outlet_radius_mm=11.25,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Nominalunassembledturningprofile/reachonly; customgroundform-toolgeometryreused,nopurchasedSKU/actualtoolstiffness/finish/processcapability.','Historicalradial.045/axial.155combinedplayclearanceisNOTtransferred; .48...52wireandtolerance/sourcebearingplaymustberechecked.','Nominalfinitewirebending/friction/fatigue/strength/full3FingerStage1notqualified.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
