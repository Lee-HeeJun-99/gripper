"""RevAK: one-piece motor plate/spindle and longer actual shaft engagement.

The new plate is machined from blank: Boolean hole restoration is NOT a weld
repair. Motor moves+5.5mm axially; Drum/Idler/Finger/wire positions unchanged.
Removes five separate support parts per sector, retains real bearing clips.
"""
import argparse,json,shutil,sys,itertools
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,translate,rotate,export,volume,bounds,overlap,common,solid_count
from mechanisms_stage1 import hex_axis
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAJ_idler1/summary.json';d=json.loads(source.read_text());refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()};removed=[]
    for n in list(parts):
        if n[3:].startswith('CLUTCH_GROUND_'):
            removed.append(n);parts.pop(n);refs.pop(n)
    module={}
    for n,s in parts.items():
        if n.startswith(('F0_MOTOR','F0_MF0_','F0_MF1_')):module[n[3:]]=translate(s,0,5.5,0)
    plate=module['MOTOR_PLATE']
    # Former bracket taps are absent on the NEW blank.
    for x in (89,131):plate=fuse(plate,cyl(1.51,(x,-8.5,20),5,(0,1,0)))
    # Rear22.02 pilot well depth2.7, finite2.3mm floor and integral8mm spindle.
    plate=fuse(plate,cyl(11.02,(110,-5.8,20),2.3,(0,1,0)))
    plate=fuse(plate,cyl(4,(110,-3.5,20),7.2,(0,1,0)))
    plate=fuse(plate,cyl(4.8,(110,-1.5,20),.5,(0,1,0)))
    plate=cut(plate,cyl(2.65,(110,-8.6,20),12.4,(0,1,0)),cut(cyl(4.2,(110,3.1,20),.6,(0,1,0)),cyl(3.6,(110,3,20),.8,(0,1,0))))
    module['MOTOR_PLATE']=plate
    # Independent finite inner-ring clip reaches9.6mm shoulder diameter.
    clip=cut(cyl(4.8,(110,3.1,20),.5,(0,1,0)),cyl(3.6,(110,3,20),.7,(0,1,0)),box(110,3,19.4,8,.8,1.2))
    module['CLUTCH_INNER_CLIP']=clip
    cy=12.7
    hub=fuse(cyl(4,(110,4.8,20),11.2,(0,1,0)),cyl(7,(110,9.8,20),6.2,(0,1,0)))
    hub=fuse(hub,box(106,4.8,16,8,1.4,8));hub=fuse(hub,box(113,9.8,14.5,5,6.2,16))
    hub=cut(hub,cyl(2.52,(110,4.7,20),11.4,(0,1,0)),box(110,4.7,19.7,9,11.4,.6),cyl(1.5,(115,cy,12),7.7),cyl(1.6,(115,cy,20.3),10.3))
    bolt=fuse(cyl(1.49,(115,cy,13.5),17),cyl(2.75,(115,cy,30.5),3));bolt=cut(bolt,hex_axis((115,cy,31.5),(0,0,1),2.5,2.1))
    module.update(CLUTCH_INPUT_HUB=hub,CLUTCH_CLAMP_BOLT=bolt)
    # New Palm blank: remove obsolete MF holes under the relocated feet,
    # not physical plugs. Existing historical Palm remains unchanged.
    palm=parts['PALM']
    for i in range(3):
        for x,y in ((93,-6.5),(127,-6.5),(90.5,-5.5)):
            palm=fuse(palm,rotate(cyl(1.71,(x,y,-12),5),120*i))
        for x in (93,127):palm=cut(palm,rotate(cyl(1.7,(x,-1,-13),7),120*i))
    todo={'PALM':palm}
    for i in range(3):
        for suffix,s in module.items():todo[f'F{i}_{suffix}']=rotate(s,120*i)
    changed=[];rows=[]
    for n,s in todo.items():
        assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
        export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n);rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl'))))
    bb={n:bounds(s) for n,s in parts.items()};hits=[]
    for n,m in itertools.combinations(parts,2):
        if n not in changed and m not in changed:continue
        if overlap(bb[n],bb[m]):
            v=common(parts[n],parts[m])
            if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='CANDIDATE_NOMINAL_GEOMETRY_PASS' if not hits else 'CANDIDATE_INTERFERENCE_FAIL',revision=a.tag,adopted=False,parent=ref(source),parts=len(parts),changed=rows,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),interferences=hits,removed_design_parts=removed,
        mechanism='One-piece grounded motor plate/spindle, no loose bridge/ground bolts/spacers. Same fixed-ground bearing, one friction face and unchanged winding route.',integrated_motor_support=True,ground_support_part_ID_suffix='MOTOR_PLATE',motor_axial_translation_from_AJ_mm=5.5,motor_flange_Y_mm=-8.5,clamp_bolt_Y_mm=cy,
        minimum_shaft_tip_Y_mm=14.5,maximum_shaft_tip_Y_mm=16.5,actual_shaft_grip_range_mm=[9.7,11.2],clamp_clearance_zone_Y_mm=[cy-1.6,cy+1.6],minimum_shaft_coverage_margin_mm=14.5-(cy+1.6),
        torque_model=d['torque_model'],geometry=d['geometry'],spindle=dict(journal_OD_mm=8,shaft_clearance_ID_mm=5.3,rear_inner_ring_shoulder_OD_mm=9.6,clip_OD_mm=9.6,inner_ring_endplay_mm=.1),
        register_requirement=dict(pilot_bore_mm=[22.010,22.030],motor_pilot_mm=[21.950,22.000],well_depth_mm=[2.68,2.72],motor_pilot_height_mm=[1.5,2.5],shaft_clearance_ID_mm=[5.29,5.31],minimum_axial_clearance_mm=.18,note='Proposed machining requirements, not measured process; motor pilot-to-shaft runout and one-piece journal coaxiality still needed'),
        new_risks=['Integral journal material/wear and groove strength','Actual clamp closure/contact and spring/motor axial load','New foot holes, tool access and complete manufacturing definitions','Unqualified calibration, materials and maximum transient load'],producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),removed=len(removed),hits=hits),indent=2))
if __name__=='__main__':main()
