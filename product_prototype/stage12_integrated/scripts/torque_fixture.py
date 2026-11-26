"""Counterbalanced bench torque-arm candidate with positive pin transmission.
Not an installed production part; proof strength/sensor adapters unqualified.
"""
import argparse,json,sys,math,shutil
from pathlib import Path
from baseline_registry import ROOT,S1,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import box,cut,fuse,export,common,volume,bounds,solid_count,read,translate
from build_stage1 import compound
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Ax1,gp_Pnt,gp_Dir,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def cylinder(x,y,z,r,l,d=(0,1,0)):return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x,y,z),gp_Dir(*d)),r,l).Shape()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--z-pin',action='store_true');a=p.parse_args();out=ROOT/'hardware_test/fixtures'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    lever=fuse(box(-23,-.5,17,206,6,6),cylinder(80,-.5,20,11,6))
    lever=cut(lever,cylinder(80,-1,20,4.05,7))
    for x in (-20,180):lever=cut(lever,cylinder(x,-1,20,2.25,7))
    axis=(0,0,1) if a.z_pin else (1,0,0)
    lever=cut(lever,cylinder(80,2.5,8,.755,24,axis) if a.z_pin else cylinder(68,2.5,20,.755,24,axis))
    # Explicit M2 major thread envelopes at both ends; not tap drill holes.
    for v in ((9,27) if a.z_pin else (69,87)):
        lever=cut(lever,cylinder(80,2.5,v,1.,4,axis) if a.z_pin else cylinder(v,2.5,20,1.,4,axis))
    sources={}
    if a.z_pin:
        T=gp_Trsf();T.SetRotation(gp_Ax1(gp_Pnt(80,0,20),gp_Dir(0,1,0)),math.pi/2)
        plugs={}
        for label,dx in [('L',6),('R',-6)]:
            path=S1/'cad/parts/revAA_mbd1'/('F0_DRUM_PIN_PLUG_'+label+'.step');plugs['PLUG_'+label]=BRepBuilderAPI_Transform(translate(read(path),dx,0,0),T,True).Shape();sources[label]=ref(path)
        shapes=dict(TORQUE_ARM=lever,TORQUE_PIN=cylinder(80,2.5,13,.745,14,axis),**plugs)
    else:shapes=dict(TORQUE_ARM=lever,TORQUE_PIN=cylinder(73,2.5,20,.745,14,axis),PLUG_L=cylinder(69,2.5,20,1.,4,axis),PLUG_R=cylinder(87,2.5,20,1.,4,axis))
    checks=[]
    for n,s in shapes.items():
        ok=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0;export(s,out/n)
        checks.append(dict(part=n,valid_single_positive=ok,volume_mm3=volume(s),STEP=ref(out/(n+'.step')),STL=ref(out/(n+'.stl'))))
    hits=[];names=list(shapes)
    for i,n in enumerate(names):
        for m in names[i+1:]:
            v=common(shapes[n],shapes[m])
            if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(shapes.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    # Smooth constant-section beam screen only; not hub/pin/notch proof.
    I=.006*.006**3/12;torque=.45;F=torque/.100;stress=torque*.003/I
    result=dict(status='FIXTURE_GEOMETRY_PASS' if not hits and all(r['valid_single_positive'] for r in checks) else 'FAIL',
        scope='FOUR FINITE BENCH FIXTURE PARTS / NOMINAL COMMON ONLY, NOT PROOF LOAD OR PURCHASED SENSOR ADAPTER',parts=checks,hits=hits,assembly=ref(out/'ASSEMBLY.step'),
        nominal_force_arm_m=.100,reference_torque_Nm=torque,reference_force_N=F,gross_arm_bending_reference_Pa=stress,pin_axis=list(axis),shaft_install_rotation_deg=90 if a.z_pin else 0,actual_stock_plug_sources=sources,
        load_cell_requirement=dict(range_N=[-20,20],resolution_N=.001,lever_measurement_resolution_mm=.01),
        required_test_cutset=['Drum','Drum nipple cap and3bolts','Production crosspin and plugs','Idler/other obstructing production hardware; use separate supported bench shaft module'],
        interfaces=['8.10mm bore on existing8mm shaft shoulder','1.49mmx14custom pin in1.51bore across shaft/pin axisY2.5','M2x0.4-6H threaded4mm ends; nominal major CAD is NOT tap-drill'],
        warning='Simple plug cylinders are thread envelopes, not socket/tool models. Sensor end link and bench support must be selected/modelled. No powered calibration, proof capacity, fatigue or exact clamp clearance certification.',
        physical_records_measured=False,powered_authorization=False,producer=ref(out/'producer.py'))
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
