"""RevAG: ground-supported output bearing removes input/output bearing bypass.

Actual hollow spindle/bridge, independent inner-ring clip, front motor-shaft
collet and ONE friction face. Material/preload, torque cap and strength remain
unqualified. This is not a renamed RevAF two-face force model.
"""
import argparse,json,shutil,sys,itertools
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,translate,export,volume,bounds,overlap,common,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from mechanisms_stage1 import hex_axis

def ring(ri,ro,y,h):return cut(cyl(ro,(110,y,20),h,(0,1,0)),cyl(ri,(110,y-.1,20),h+.2,(0,1,0)))

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--raised-clamp-head',action='store_true');p.add_argument('--flat-clamp-seat',action='store_true');p.add_argument('--clamp-wall',action='store_true');p.add_argument('--ground-standoffs',action='store_true');p.add_argument('--full-spacer-seat',action='store_true');p.add_argument('--shared-register',action='store_true');a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAF_layout6/summary.json';d=json.loads(source.read_text());refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()}
    removed=[]
    for i in range(3):
        n=f'F{i}_CLUTCH_LINER_L';removed.append(n);parts.pop(n);refs.pop(n)
    # Rear bridge bolts at +/-22mm are OUTSIDE the actual 17mm Drum radius.
    bridge=fuse(box(86,-6,16 if a.ground_standoffs else 18,48,2,8 if a.ground_standoffs else 4),cyl(4,(110,-6,20),9.7,(0,1,0)))
    bridge=fuse(bridge,cyl(4.8,(110,-1.5,20),.5,(0,1,0)))
    if a.shared_register:
        assert a.ground_standoffs and a.full_spacer_seat
        bridge=fuse(bridge,cyl(10.99,(110,-11.3,20),5.3,(0,1,0)))
    bridge=cut(bridge,cyl(2.65 if a.shared_register else 2.6,(110,-11.4 if a.shared_register else -6.1,20),15.2 if a.shared_register else 9.9,(0,1,0)),ring(3.6,4.2,3.1,.6))
    xs=(89,131) if a.full_spacer_seat else (88,132)
    for x in xs:bridge=cut(bridge,cyl(1.7,(x,-6.1,20),2.2,(0,1,0)))
    inner_clip=cut(ring(3.6,4.35,3.1,.5),box(110,3,19.4,8,.8,1.2))
    # Input sleeve is driven ONLY from actual motor shaft at the front.
    cy=12.9 if a.clamp_wall else 11.3
    front=16 if a.clamp_wall else 14
    hub=fuse(cyl(4,(110,4.8,20),front-4.8,(0,1,0)),cyl(7,(110,9.8,20),front-9.8,(0,1,0)))
    head_z=30.5 if a.raised_clamp_head else 25.5
    hub=fuse(hub,box(106,4.8,16,8,1.4,8));hub=fuse(hub,box(113,9.8,14.5,5,front-9.8,head_z-14.5))
    hub=cut(hub,cyl(2.52,(110,4.7,20),front-4.6,(0,1,0)),box(110,4.7,19.7,9,front-4.6,.6),cyl(1.5,(115,cy,12),7.7),cyl(1.6,(115,cy,20.3),head_z-20.2))
    if not a.flat_clamp_seat:hub=cut(hub,cyl(3,(115,cy,head_z),3.2))
    if a.flat_clamp_seat:assert a.raised_clamp_head
    # Reuse actual socket bolt shape after a rigid translation only.
    clamp=translate(parts['F0_CLUTCH_CLAMP_BOLT'],0,cy+8,0)
    if a.raised_clamp_head:
        clamp=fuse(cyl(1.49,(115,cy,13.5),17),cyl(2.75,(115,cy,30.5),3))
        clamp=cut(clamp,hex_axis((115,cy,31.5),(0,0,1),2.5,2.1))
    plate=parts['F0_MOTOR_PLATE']
    if a.shared_register:
        # NEW machined plate from blank, NOT a welded repair of an old hole.
        plate=fuse(plate,cut(cyl(11.26,(110,-14,20),3,(0,1,0)),cyl(11.01,(110,-14.1,20),3.2,(0,1,0))))
        extension=cut(box(86,-11,-7,48,2,52),cyl(11.01,(110,-11.1,20),2.2,(0,1,0)))
        for x in (94.5,125.5):
            for z in (4.5,35.5):extension=cut(extension,cyl(1.8,(x,-11.1,z),2.2,(0,1,0)))
        plate=fuse(plate,extension)
    for x in xs:plate=cut(plate,cyl(1.5,(x,-14.1,20),10.2,(0,1,0)))
    module=dict(CLUTCH_GROUND_SPINDLE=bridge,CLUTCH_INNER_CLIP=inner_clip,CLUTCH_INPUT_HUB=hub,CLUTCH_CLAMP_BOLT=clamp,MOTOR_PLATE=plate)
    if a.shared_register:
        for name,s in parts.items():
            if name.startswith('F0_MOTOR_BOLT_'):
                # Under-head length6->8mm, head advances2mm; retain actual
                # socket geometry and original3mm motor-thread engagement.
                q=translate(s,0,2,0);b=bounds(s);x=(b[0]+b[3])/2;z=(b[2]+b[5])/2
                q=fuse(q,cyl(1.49,(x,b[1],z),2.1,(0,1,0)))
                module[name[3:]]=q
    for x in xs:
        module[f'CLUTCH_GROUND_BOLT_{x}']=fuse(cyl(1.49,(x,-14,20),10,(0,1,0)),cyl(2.75,(x,-4,20),3,(0,1,0)))
        if a.ground_standoffs:
            start=-9 if a.shared_register else -11;length=-6-start
            module[f'CLUTCH_GROUND_SPACER_{x}']=cut(cyl(3,(x,start,20),length,(0,1,0)),cyl(1.7,(x,start-.1,20),length+.2,(0,1,0)))
    changed=[];rows=[]
    for i in range(3):
        for suffix,s in module.items():
            n=f'F{i}_{suffix}';s=rotate(s,120*i)
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
    result=dict(status='CANDIDATE_NOMINAL_GEOMETRY_PASS' if not hits else 'CANDIDATE_INTERFERENCE_FAIL',revision=a.tag,adopted=False,parent=ref(source),parts=len(parts),changed=rows,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),interferences=hits,removed_design_parts=removed,
        mechanism='Ground bridge -> hollow 8mm spindle -> bearing inner ring. Motor shaft passes through5.2mm clearance bore and drives front split collet. One input pressure/liner face drives Drum; no input-supported output bearing.',
        torque_model=dict(faces=1,annulus_inner_mm=8.3,annulus_outer_mm=9.6,nominal_drum_wire_radius_mm=11.25),
        ground_bridge_bolt_offsets_mm=[x-110 for x in xs],motor_shaft_available_nominal_engagement_mm=6.2,raised_clamp_head=a.raised_clamp_head,flat_clamp_seat=a.flat_clamp_seat,clamp_nominal_underhead_length_mm=17 if a.raised_clamp_head else 12,ground_standoffs=a.ground_standoffs,full_spacer_seat=a.full_spacer_seat,
        spindle=dict(OD_mm=8,ID_mm=5.3 if a.shared_register else 5.2,groove_root_OD_mm=7.2,inner_ring_clip_endplay_mm=.1),clamp_wall=a.clamp_wall,clamp_bolt_Y_mm=cy,clamp_hole_min_side_ligament_mm=min(cy-9.8,front-cy)-1.6,
        shared_register=a.shared_register,register_requirement=(dict(common_bore_mm=[22.010,22.030],spindle_pilot_mm=[21.970,21.990],motor_pilot_mm=[21.950,22.000],plate_thickness_mm=[4.98,5.02],spacer_length_mm=[2.99,3.01],spindle_boss_length_mm=[5.28,5.32],nominal_pilot_engagement_mm=2.3,motor_shaft_engagement_mm=[4.2,6.2],note='New design tolerances, not measured manufacturing capability; motor pilot-to-shaft runout is not specified by this interface drawing.') if a.shared_register else None),
        new_risks=['Spring axial load now reacts through output bearing and motor shaft collet; axial bearing/clamp capacity unqualified','5.2mm hollow-spindle bore/5mm motor shaft alignment and rotating clearance require tolerance/deformation analysis','M3 blind thread/tool/socket/bridge contact proof incomplete','Custom spindle retaining clip and1mm groove-root wall strength unqualified','One-face torque model replaces RevAF two-face model; cannot reuse its force window','Front collet grip and shaft tip engagement require strength/assembly verification'],
        producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),hits=hits),indent=2))
if __name__=='__main__':main()
