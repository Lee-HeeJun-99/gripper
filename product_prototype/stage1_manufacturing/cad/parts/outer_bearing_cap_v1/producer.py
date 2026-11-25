"""Actual outer retaining plate prototype on revH left pedestal.

Only one axial direction/one bearing. Not adopted in revH assembly; no strength,
race land, shaft/inner cap or bearing preload qualification.
"""
import json,hashlib,shutil
from pathlib import Path
from build_stage1 import box,cyl,cut,fuse,volume,export,translate,solid_count
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer
ROOT=Path(__file__).resolve().parents[1]
def load(p):
 r=STEPControl_Reader();assert r.ReadFile(str(p))==IFSelect_RetDone;r.TransferRoots();return r.OneShape()
def main():
 src=ROOT/'cad/exports/revH';out=ROOT/'cad/parts/outer_bearing_cap_v1';out.mkdir(exist_ok=False)
 housing=load(src/'F0_PEDESTAL_L.step');bearing=load(src/'F0_BEARING_L.step')
 cap=cut(cyl(15,(80,-4,20),1,(0,1,0)),cyl(7,(80,-5,20),3,(0,1,0)))
 parts={}
 for x in (74,86):
  cap=cut(cap,cyl(1.7,(x,-5,10),3,(0,1,0)))
  housing=cut(housing,cyl(1.5,(x,-3,10),3,(0,1,0)))
  parts[f'CAP_BOLT_{x}']=fuse(cyl(1.5,(x,-4,10),4,(0,1,0)),cyl(2.75,(x,-7,10),3,(0,1,0)))
 parts.update(PEDESTAL_L_WITH_CAP_THREADS=housing,OUTER_CAP=cap)
 for name,s in parts.items():
  assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1;export(s,out/name)
 # Actual complete revH solids remain obstacles. Only the explicitly replaced
 # old pedestal is excluded; nothing else in the drive is hidden.
 fixed={p.stem:load(p) for p in src.glob('*.step') if p.stem not in ('ASSEMBLY','F0_PEDESTAL_L')}
 hits=[]
 for name,s in parts.items():
  for other,t in fixed.items():
   v=volume(BRepAlgoAPI_Common(s,t).Shape())
   if v>1e-7:hits.append(dict(a=name,b=other,volume_mm3=v))
 names=list(parts)
 for i,name in enumerate(names):
  for other in names[i+1:]:
   v=volume(BRepAlgoAPI_Common(parts[name],parts[other]).Shape())
   if v>1e-7:hits.append(dict(a=name,b=other,volume_mm3=v))
 stop=[]
 for dy in (0,-.5,-1,-1.1):stop.append(dict(bearing_shift_Y_mm=dy,cap_overlap_mm3=volume(BRepAlgoAPI_Common(translate(bearing,0,dy,0),cap).Shape())))
 result=dict(status='NOMINAL_OUTER_CAP_GEOMETRY_ONLY' if not hits else 'OUTER_CAP_GEOMETRY_FAIL',assembly_collisions=hits,axial_stop_geometry=stop,purchased_screw='M3x4 ISO4762 nominal major/head envelope, no helical thread',housing_thread='M3 nominal major void; shop tap drill2.5, proposed3mm engagement',cap_material='steel1mm candidate; allowable NOT MEASURED',race_contact='annulusR7to8 captures boundary envelope, exact supplier outer race/seal land NOT verified',shaft_axial_capture_complete=False,inner_cap_complete=False,adopted_in_revH=False,hardware_test=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py')
 (out/'input_sha256.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in src.glob('*.step')},indent=2))
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
