"""Finite selected stock-component interface at the actual AO drive axes.
Nominal envelopes from primary drawing facts, NOT manufacturer STEP or release.
"""
import itertools,json,math,shutil,sys
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,export,common,bounds,overlap,solid_count,volume
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'cad/exports/revAV_micro_interface1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    parent=ROOT/'cad/exports/revAO_root2/summary.json';pd=json.loads(parent.read_text())
    reviewed=ROOT/'models/standard_drive/batch6_sources1/reviewed.json'
    deps=[parent,reviewed,ROOT/'validation/transmission/batch6_operating1/summary.json',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
    refs=pd['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
    dump(out/'inputs.json',dict(parent=ref(parent),producer=ref(out/'producer.py'),dependencies=[ref(p) for p in deps],context_parts=refs,
        tolerances=dict(exact_intersection_mm3_max=1e-8),
        design='Stock1101 body/terminal clearance envelope10x12x25.6;9mm D shaft and4mm pilot. Stock1996 nominal hub17.5x5, M3 holes radius6.35. Spool custom11mm core/12mm flanges with0.5mm wire center radius11.25;2mm hub face disk, four M3x5 cap screws. Radial M3x8 set screw design requirement, supplied length unknown.',
        assumptions='Nominal dimensions only. Motor shaft flat modeled over exposed shaft, full flat extent unverified. Hub radial hole centered axially; face hole clock45deg relative set screw. No fictional motor ground support, shaft bearing rating, cable anchor or physical overload bound.'))
    body=box(105,-33.6,14,10,25.6,12)
    shaft=cut(cyl(1.5,(110,-8,20),9,(0,1,0)),box(111,-8,17,2,9,6))
    motor=fuse(fuse(body,cyl(2,(110,-8,20),.7,(0,1,0))),shaft)
    hub=cut(cyl(8.75,(110,-6,20),5,(0,1,0)),cyl(1.5,(110,-6.1,20),5.2,(0,1,0)))
    hub=cut(hub,cyl(1.5,(110,-3.5,20),9,(1,0,0)))
    spool=fuse(fuse(cyl(11,(110,-1,20),2,(0,1,0)),cyl(12,(110,-1,20),.5,(0,1,0))),cyl(12,(110,.5,20),.5,(0,1,0)))
    spool=cut(spool,cyl(1.6,(110,-1.1,20),2.2,(0,1,0)))
    local={'MICRO_MOTOR':motor,'STOCK_HUB':hub,'SPOOL':spool}
    holes=[]
    for j in range(4):
        a=math.pi/4+j*math.pi/2;x=110+6.35*math.cos(a);z=20+6.35*math.sin(a);holes.append([x,z])
        hub=cut(hub,cyl(1.5,(x,-6.1,z),5.2,(0,1,0)))
        spool=cut(spool,cyl(1.65,(x,-1.1,z),2.2,(0,1,0)))
        screw=fuse(cyl(1.5,(x,-4,z),5,(0,1,0)),cyl(2.75,(x,1,z),3,(0,1,0)))
        local[f'SPOOL_BOLT_{j}']=screw
    local.update(STOCK_HUB=hub,SPOOL=spool,SET_SCREW=cyl(1.5,(111,-3.5,20),8,(1,0,0)))
    parts={};rows=[]
    for i in range(3):
        for suffix,s in local.items():
            assert not (ROOT/'runtime/STOP').exists()
            n=f'F{i}_{suffix}';s=rotate(s,120*i)
            assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
            export(s,out/n);parts[n]=s;rows.append(dict(part_ID=n,STEP=ref(out/(n+'.step')),STL=ref(out/(n+'.stl')),volume_mm3=volume(s),bounds_mm=bounds(s)))
    # Only a finite interface assembly is exported. Context exclusions enumerate
    # the functions being replaced; they are NOT removed from an adopted BOM.
    replaced=[];retained={}
    for n,r in refs.items():
        suffix=n[3:] if n.startswith(('F0_','F1_','F2_')) else n
        if suffix.startswith(('DRUM','MOTOR','CLUTCH','AXIAL','MF0_','MF1_')):replaced.append(n)
        else:retained[n]=read(REPO/r['path'])
    hits=[];pairs=0
    allparts={**retained,**parts};bb={n:bounds(s) for n,s in allparts.items()}
    for n,m in itertools.combinations(allparts,2):
        if n not in parts and m not in parts:continue
        assert not (ROOT/'runtime/STOP').exists()
        if overlap(bb[n],bb[m]):
            pairs+=1;v=common(allparts[n],allparts[m])
            if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    # Straight driver access for four face bolts and the radial set screw.
    tool=cyl(1,(119,-3.5,20),20,(1,0,0));toolhits=[]
    for i in range(3):
        n=f'F{i}_SET_DRIVER';s=rotate(tool,120*i);export(s,out/n)
        for m,t in allparts.items():
            if overlap(bounds(s),bb[m]):
                v=common(s,t)
                if v>1e-8:toolhits.append(dict(tool=n,part=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'INTERFACE_ASSEMBLY.step'))==IFSelect_RetDone
    bom=[]
    for n in parts:
        suffix=n[3:]
        kind='CUSTOM' if suffix=='SPOOL' else 'STANDARD_COMPONENT_INTERFACE'
        item='Pololu1101' if suffix=='MICRO_MOTOR' else 'Pololu1996' if suffix=='STOCK_HUB' else 'M3x5 cap screw required; grade/vendor unselected' if suffix.startswith('SPOOL_BOLT') else 'M3x8 radial set screw required; tip/grade/vendor unselected' if suffix=='SET_SCREW' else 'Custom turned spool; material/anchor unqualified'
        bom.append(dict(part_ID=n,STEP=ref(out/(n+'.step')),classification=kind,item=item,physical_rating_qualified=False))
    dump(out/'BOM.json',dict(revision=out.name,scope='24 finite interface instances only, NOT whole product BOM',parts=bom))
    result=dict(status='MICRO_INTERFACE_NOMINAL_CLEARANCE_PASS' if not hits and not toolhits else 'MICRO_INTERFACE_CLEARANCE_FAIL',revision=out.name,scope='ACTUAL SELECTED DRIVE INTERFACE AND AO RETAINED-CONTEXT CHECK ONLY',
        parent=ref(parent),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),BOM=ref(out/'BOM.json'),assembly=ref(out/'INTERFACE_ASSEMBLY.step'),parts=rows,
        part_references={n:ref(out/(n+'.step')) for n in parts},finite_interface_instances=len(parts),custom_spools=3,standard_interface_instances=21,
        context_replacement_IDs=replaced,retained_context_count=len(retained),context_intersections=hits,set_driver_intersections=toolhits,exact_intersection_pairs=pairs,
        face_hole_centers_F0_mm=holes,spool_core_radius_mm=11,wire_center_radius_mm=11.25,wire_diameter_mm=.5,
        complexity='Replaces proposed drive subassembly functions with stock motor/hub, one turned spool and standard screws per Finger; no special rivet forming or friction stack. Old drive context count is not a realized total product reduction because mounting/protection/anchor are missing.',
        removed_custom_processes_proposed=['Clutch liner/preload spring/adjuster manufacture and calibration','Custom D-bore input hub and split-clamp setup'],
        functions_not_yet_replaced=['Grounded motor mount','Rated radial/axial shaft support','Physical overload limitation','Factory cable nipple/anchor retention'],
        invalidated_gates=['tendon_force_stroke','motor_running_torque_speed','overload_protection','motor_alignment_reactions','drum_strength','complete_path'],
        whole_product_candidate=False,adopted=False,actual_capacity_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],instances=len(parts),replaced_context=len(replaced),pairs=pairs,hits=hits,toolhits=toolhits)))
    raise SystemExit(2 if hits or toolhits else 0)
if __name__=='__main__':main()
