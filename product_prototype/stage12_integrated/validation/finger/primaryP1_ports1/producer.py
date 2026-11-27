"""Actual P1 root/terminal cut ports and section identities, not connector capacity."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,box,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def main():
 out=ROOT/'validation/finger'/sys.argv[1];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'cad/exports/primaryP1_open9/summary.json';cad=json.loads(src.read_text());names=('F0_ROOT_FRONT','F0_ROOT_BACK','F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_RAIL_L','F0_RAIL_R','F0_SKIN','F0_SWIVEL_AXLE');s={};inventory=[]
 for name in names:
  r=cad['part_references'][name];assert sha(REPO/r['path'])==r['SHA256'];s[name]=read(REPO/r['path']);inventory.append(dict(part=name,source=r,bounds_mm=bounds(s[name]),volume_mm3=volume(s[name])))
 root=bounds(s['F0_ROOT_FRONT'])[2];tip=bounds(s['F0_TERMINAL_BACK'])[5];sections=[]
 for name in ('F0_RAIL_L','F0_RAIL_R'):
  for z in (-8,-46,-83):
   for h in (.02,.01):
    slab=BRepAlgoAPI_Common(s[name],box(40,-30,z-h/2,20,60,h)).Shape();g=GProp_GProps();BRepGProp.VolumeProperties_s(slab,g,1e-11);a=g.Mass()/h;I=g.MatrixOfInertia();iy=(I.Value(2,2)+I.Value(3,3)-I.Value(1,1))/(2*h)
    sections.append(dict(part=name,z_mm=z,h_mm=h,A_mm2=a,Iyy_mm4=iy,centroid_x_mm=g.CentreOfMass().X()))
 checks=dict(root_cut=abs(root+7)<1e-8,terminal_cut=abs(tip+84)<1e-8,rail_A=all(abs(x['A_mm2']/.6-1)<1e-6 for x in sections),rail_I=all(abs(x['Iyy_mm4']/.002-1)<1e-6 for x in sections),PET_end=abs(bounds(s['F0_SKIN'])[2]+93.2)<1e-8)
 result=dict(status='ACTUAL_P1_GEOMETRIC_PORTS_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_PORT_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inventory=inventory,sections=sections,checks={k:bool(v) for k,v in checks.items()},root_cut_z_mm=root,terminal_cut_z_mm=tip,free_rail_length_mm=root-tip,PET_length_from_root_mm=root-bounds(s['F0_SKIN'])[2],terminal_port_offset_XZ_mm=[43-50.4,-92-tip],object_tip_offset_XZ_mm=[50-50.4,-100-tip],physical_BC='Conditional rigid grip cuts at actual envelopes; contact/preload/stiffness of clamps NOT certified. Rail continues inside finite Terminal; PET distal axial DOF stays free with actual finite unilateral walls.',historical_88mm_disposition='Endpoint datum model at-95mm is not the actual77mm free-span/rigid-terminal reduction; preserve its original outputs and do not transfer them as product demand.',whole_system_release=False)
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
