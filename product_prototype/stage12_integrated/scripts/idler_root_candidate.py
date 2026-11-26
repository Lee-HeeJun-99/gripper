"""RevAJ: larger M3 runout with finite fillets and integral metal shoulder.

Responds to the catalog-limiter load window, NOT adoption of that limiter.
Keeps 3mm pulley journal, wire plane, shims and all Finger/drive positions.
Removes one loose shoulder washer/sector; actual thread/core proof still needed.
"""
import argparse,json,math,shutil,sys,itertools
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,rotate,export,volume,bounds,overlap,common,solid_count
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.gp import gp_Pnt,gp_Ax1,gp_Dir
from OCP.GC import GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def axle():
    def p(r,y):return gp_Pnt(44+r,y,25)
    wire=BRepBuilderAPI_MakeWire();last=(0,-8.4)
    def line(point):
        nonlocal last
        wire.Add(BRepBuilderAPI_MakeEdge(p(*last),p(*point)).Edge());last=point
    def arc(mid,end):
        nonlocal last
        wire.Add(BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(p(*last),p(*mid),p(*end)).Value()).Edge());last=end
    for pt in [(1.3,-8.4),(1.5,-8.2),(1.5,-3.5),(1.29,-3.5)]:line(pt)
    arc((1.2192893219,-3.4707106781),(1.19,-3.4));line((1.19,-3.1))
    arc((1.2192893219,-3.0292893219),(1.29,-3))
    for pt in [(2.5,-3),(2.5,-2.5),(1.5,-2.5),(1.5,3),(2.75,3),(2.75,6),(0,6),(0,-8.4)]:line(pt)
    s=BRepPrimAPI_MakeRevol(BRepBuilderAPI_MakeFace(wire.Wire()).Face(),gp_Ax1(gp_Pnt(44,0,25),gp_Dir(0,1,0))).Shape()
    return cut(s,hex_axis((44,6,25),(0,-1,0),2.5,1.5))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAI_tabs1/summary.json';d=json.loads(source.read_text());refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()};removed=[]
    for i in range(3):
        n=f'F{i}_IDLER_SHOULDER_WASHER';removed.append(n);parts.pop(n);refs.pop(n)
    module=dict(IDLER_AXLE=axle(),IDLER_CLAMP_WASHER=cut(cyl(2.75,(44,-5.5,25),.5,(0,1,0)),cyl(1.55,(44,-5.6,25),.7,(0,1,0))),IDLER_NUT=cut(hex_axis((44,-7.9,25),(0,1,0),5.5,2.4),cyl(1.5,(44,-8,25),2.6,(0,1,0))))
    changed=[];rows=[]
    for i in range(3):
        for suffix,s in module.items():
            n=f'F{i}_{suffix}';s=rotate(s,120*i);assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
            export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n);rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl'))))
    bb={n:bounds(s) for n,s in parts.items()};hits=[]
    for n,m in itertools.combinations(parts,2):
        if n not in changed and m not in changed:continue
        if overlap(bb[n],bb[m]):
            v=common(parts[n],parts[m])
            if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    drive_src=ROOT/'cad/exports/revAH_pilot2/summary.json';drive=json.loads(drive_src.read_text())
    same_drive=[n for n in refs if n.startswith(('F0_MOTOR','F1_MOTOR','F2_MOTOR','F0_CLUTCH','F1_CLUTCH','F2_CLUTCH','F0_DRUM','F1_DRUM','F2_DRUM'))]
    assert all(refs[n]==drive['part_references'][n] for n in same_drive)
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='CANDIDATE_NOMINAL_GEOMETRY_PASS' if not hits else 'CANDIDATE_INTERFERENCE_FAIL',revision=a.tag,adopted=False,parent=ref(source),parts=len(parts),changed=rows,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),interferences=hits,removed_design_parts=removed,
        geometry=dict(journal_mm=3,thread='M3x0.5-6g nominal major envelope, actual core/gauge NOT qualified',runout_neck_mm=2.38,neck_fillets_mm=.1,integral_shoulder_OD_mm=5,shoulder_Y_mm=[-3,-2.5],washer_OD_ID_t_mm=[5.5,3.1,.5],nut_AF_height_mm=[5.5,2.4]),
        preload_path='Nut -> actual rear metal washer -> existing bracket -> integral metal shoulder -> shaft thread. Rotating POM and matched shims retain prior clearance geometry.',
        same_lever_nominal_bending_stress_ratio=(1.55/2.38)**3,
        warning='Section-modulus ratio is not a strength PASS: actual thread root, stress concentration, preload/contact, material and fatigue unresolved. JH1M is not installed or certified.',
        drive_definition=ref(drive_src),torque_model=drive['torque_model'],shared_register=drive['shared_register'],register_requirement=drive['register_requirement'],ground_bridge_bolt_offsets_mm=drive['ground_bridge_bolt_offsets_mm'],
        invalidated=['Idler axle/washer/nut material and strength','Thread/preload/assembly and tool access','Changed hardware collision/motion checks','Part mass/inertia and BOM'],producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),hits=hits,section_ratio=result['same_lever_nominal_bending_stress_ratio']),indent=2))
if __name__=='__main__':main()
