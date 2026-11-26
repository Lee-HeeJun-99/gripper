"""RevAF packaging correction from actual AE failures, not a released limiter.

Move the complete motor/drum cartridge outward, extend the Palm, move its
real base fasteners, and rebuild the finite tendon to the unchanged idler.
This deliberately changes footprint and finished cable length; old PASSs invalid.
"""
import argparse,csv,json,math,shutil,sys,itertools
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,translate,export,volume,bounds,overlap,common,solid_count
from build_stage1 import compound
from wire_cad_stage1 import curved
import wire_motion as wm
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCP.gp import gp_Pnt,gp_Circ,gp_Ax2,gp_Dir
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def wire():
    wm.DRUM_R=wm.IDLER_R=11.25;wm.START_PHI=-math.pi/2
    g=wm.path(0);u=np.array([-66.,5.]);u=u/np.linalg.norm(u);n=np.array([-u[1],u[0]])
    if n[1]<0:n=-n
    phi=math.atan2(n[1],n[0]);A=np.array([110+11.25*n[0],0,20+11.25*n[1]])
    B=np.array([44+11.25*n[0],0,25+11.25*n[1]])
    end=g['end']
    while end<phi:end+=2*math.pi
    t=np.array([math.sin(g['beta']),0,math.cos(g['beta'])]);tip=g['P']+16*t
    w=BRepBuilderAPI_MakeWire();w.Add(curved((110,20),11.25,-math.pi/2,phi))
    w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*A),gp_Pnt(*B)).Edge());w.Add(curved((44,25),11.25,phi,end))
    w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(*g['Q']),gp_Pnt(*tip)).Edge())
    profile=BRepBuilderAPI_MakeFace(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(gp_Circ(gp_Ax2(gp_Pnt(110,0,8.75),gp_Dir(1,0,0)),.25)).Edge()).Wire()).Face()
    s=BRepOffsetAPI_MakePipe(w.Wire(),profile).Shape()
    L=11.25*(phi+math.pi/2)+np.linalg.norm(A-B)+11.25*(end-phi)+np.linalg.norm(g['Q']-tip)
    assert abs(volume(s)/(math.pi*.25**2*L)-1)<1e-6
    return s,dict(free_length_mm=float(L),diameter_mm=.5,drum_center_mm=[110,0,20],idler_center_mm=[44,0,25],upper_tangent_A_mm=A.tolist(),upper_tangent_B_mm=B.tolist(),scope='Finite nominal installed wire, no stress-free shape, friction or fatigue claim')

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAE_direct_clutch2/summary.json';d=json.loads(source.read_text())
    refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()};changes={}
    # Radius bounds derive from the retained nipple capture and cap screws.
    for n in d['changed_parts']:
        if not n.startswith('F0_'):continue
        s=parts[n];suffix=n[3:]
        if suffix in ('CLUTCH_PRESSURE','CLUTCH_LINER_L','CLUTCH_LINER_R'):
            s=cut(s,cut(cyl(20,(80,-4,20),11,(0,1,0)),cyl(9.6,(80,-4.1,20),11.2,(0,1,0))))
        if suffix=='CLUTCH_SPRING':
            s=cut(s,cut(cyl(20,(80,5.9,20),1,(0,1,0)),cyl(9.5,(80,5.8,20),1.2,(0,1,0))))
        if suffix=='CLUTCH_INPUT_HUB':s=cut(s,cyl(1.5,(85,-8,12),7.7))
        changes[suffix]=translate(s,30,0,0)
    for suffix in ('DRUM_NIPPLE_CAP','DRUM_FACTORY_NIPPLE'):
        s=parts['F0_'+suffix]
        if suffix=='DRUM_NIPPLE_CAP':s=cut(s,cyl(10.1,(80,4.4,20),3.2,(0,1,0)))
        changes[suffix]=translate(s,30,0,0)
    for n in parts:
        if n.startswith('F0_DRUM_CAP_BOLT_'):changes[n[3:]]=translate(parts[n],30,0,0)
        if n.startswith(('F0_MF0_','F0_MF1_')):changes[n[3:]]=translate(parts[n],30,30,0)
    tendon,route=wire();changes['TENDON_WIRE']=tendon
    palm=fuse(parts['PALM'],cut(cyl(145,(0,0,-12),5),cyl(114.9,(0,0,-12.1),5.2)))
    for i in range(3):
        for x in (93,127):palm=cut(palm,rotate(cyl(1.7,(x,-6.5,-13),7),120*i))
    todo={'PALM':palm}
    for i in range(3):
        for suffix,s in changes.items():todo[f'F{i}_{suffix}']=rotate(s,120*i)
    rows=[];changed=[]
    for n,s in todo.items():
        assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
        export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
        rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),volume_mm3=volume(s),bounds_mm=bounds(s)))
    bb={n:bounds(s) for n,s in parts.items()};hits=[]
    for n,m in itertools.combinations(parts,2):
        if n not in changed and m not in changed:continue
        if overlap(bb[n],bb[m]):
            v=common(parts[n],parts[m])
            if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    # Complete candidate identity inventory, not a manufacturing release BOM.
    with (out/'CANDIDATE_INVENTORY.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=['part_ID','STEP','STEP_SHA256','qualification']);wr.writeheader()
        for n,r in refs.items():wr.writerow(dict(part_ID=n,STEP=r['path'],STEP_SHA256=r['SHA256'],qualification='CANDIDATE ONLY; material, assembly and protected loads not qualified'))
    dump(out/'summary.json',dict(status='CANDIDATE_NOMINAL_GEOMETRY_PASS' if not hits else 'CANDIDATE_INTERFERENCE_FAIL',revision=a.tag,adopted=False,parent=ref(source),parts=len(parts),changed=rows,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),inventory=ref(out/'CANDIDATE_INVENTORY.csv'),interferences=hits,wire=route,
        footprint=dict(old_palm_OD_mm=230,new_palm_OD_mm=290,root_radius_mm=50,drive_radial_translation_mm=30),
        tradeoff='Larger Palm and longer cable in exchange for actual Root/motor clearance and removal of separate rigid two-shaft coupling',
        removed_design_parts=d['removed_design_parts'],producer=ref(out/'producer.py'),
        invalidated=['all mounting/tool/assembly and tolerances','all prescribed motion and maximum-stock wire checks','cap nipple retention strength','spring/friction/drag and torque limit','shaft overhang and motor bearing loads','Palm strength and manufacturing drawings'],whole_system_release=False))
    print(json.dumps(dict(parts=len(parts),changed=len(rows),interferences=hits,wire=route),indent=2))
if __name__=='__main__':main()
