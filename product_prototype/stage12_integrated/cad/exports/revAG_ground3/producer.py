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
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--raised-clamp-head',action='store_true');p.add_argument('--flat-clamp-seat',action='store_true');a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAF_layout6/summary.json';d=json.loads(source.read_text());refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()}
    removed=[]
    for i in range(3):
        n=f'F{i}_CLUTCH_LINER_L';removed.append(n);parts.pop(n);refs.pop(n)
    # Rear bridge bolts at +/-22mm are OUTSIDE the actual 17mm Drum radius.
    bridge=fuse(box(86,-6,18,48,2,4),cyl(4,(110,-6,20),9.7,(0,1,0)))
    bridge=fuse(bridge,cyl(4.8,(110,-1.5,20),.5,(0,1,0)))
    bridge=cut(bridge,cyl(2.6,(110,-6.1,20),9.9,(0,1,0)),ring(3.6,4.2,3.1,.6))
    for x in (88,132):bridge=cut(bridge,cyl(1.7,(x,-6.1,20),2.2,(0,1,0)))
    inner_clip=cut(ring(3.6,4.35,3.1,.5),box(110,3,19.4,8,.8,1.2))
    # Input sleeve is driven ONLY from actual motor shaft at the front.
    hub=fuse(cyl(4,(110,4.8,20),9.2,(0,1,0)),cyl(7,(110,9.8,20),4.2,(0,1,0)))
    head_z=30.5 if a.raised_clamp_head else 25.5
    hub=fuse(hub,box(106,4.8,16,8,1.4,8));hub=fuse(hub,box(113,9.8,14.5,5,4.2,head_z-14.5))
    hub=cut(hub,cyl(2.52,(110,4.7,20),9.4,(0,1,0)),box(110,4.7,19.7,9,9.4,.6),cyl(1.5,(115,11.3,12),7.7),cyl(1.6,(115,11.3,20.3),head_z-20.2))
    if not a.flat_clamp_seat:hub=cut(hub,cyl(3,(115,11.3,head_z),3.2))
    if a.flat_clamp_seat:assert a.raised_clamp_head
    # Reuse actual socket bolt shape after a rigid translation only.
    clamp=translate(parts['F0_CLUTCH_CLAMP_BOLT'],0,19.3,0)
    if a.raised_clamp_head:
        clamp=fuse(cyl(1.49,(115,11.3,13.5),17),cyl(2.75,(115,11.3,30.5),3))
        clamp=cut(clamp,hex_axis((115,11.3,31.5),(0,0,1),2.5,2.1))
    plate=parts['F0_MOTOR_PLATE']
    for x in (88,132):plate=cut(plate,cyl(1.5,(x,-14.1,20),10.2,(0,1,0)))
    module=dict(CLUTCH_GROUND_SPINDLE=bridge,CLUTCH_INNER_CLIP=inner_clip,CLUTCH_INPUT_HUB=hub,CLUTCH_CLAMP_BOLT=clamp,MOTOR_PLATE=plate)
    for x in (88,132):module[f'CLUTCH_GROUND_BOLT_{x}']=fuse(cyl(1.49,(x,-14,20),10,(0,1,0)),cyl(2.75,(x,-4,20),3,(0,1,0)))
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
        ground_bridge_bolt_offsets_mm=[-22,22],motor_shaft_available_nominal_engagement_mm=6.2,raised_clamp_head=a.raised_clamp_head,flat_clamp_seat=a.flat_clamp_seat,clamp_nominal_underhead_length_mm=17 if a.raised_clamp_head else 12,
        spindle=dict(OD_mm=8,ID_mm=5.2,groove_root_OD_mm=7.2,inner_ring_clip_endplay_mm=.1),
        new_risks=['Spring axial load now reacts through output bearing and motor shaft collet; axial bearing/clamp capacity unqualified','5.2mm hollow-spindle bore/5mm motor shaft alignment and rotating clearance require tolerance/deformation analysis','M3 blind thread/tool/socket/bridge contact proof incomplete','Custom spindle retaining clip and1mm groove-root wall strength unqualified','One-face torque model replaces RevAF two-face model; cannot reuse its force window','Front collet grip and shaft tip engagement require strength/assembly verification'],
        producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),hits=hits),indent=2))
if __name__=='__main__':main()
