"""RevAE direct-motor friction-drum candidate, NOT a certified force limiter.

Actual make-part solids and explicit replacement cut-set; purchased bearing is
an interface envelope. Nominal thread envelopes are NOT manufactured helices.
Spring/friction/load ratings require independent qualification, never guessed.
"""
import argparse,csv,json,math,shutil,sys,itertools
from pathlib import Path
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,translate,export,volume,bounds,overlap,common,solid_count,hex_y
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakeRevol
from OCP.gp import gp_Pnt,gp_Ax1,gp_Dir
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def ring(ri,ro,y,h):return cut(cyl(ro,(80,y,20),h,(0,1,0)),cyl(ri,(80,y-.1,20),h+.2,(0,1,0)))
def disc_spring():
    p=BRepBuilderAPI_MakePolygon()
    for r,y in [(4.1,6.35),(10,6),(10,6.25),(4.1,6.6)]:p.Add(gp_Pnt(80+r,y,20))
    p.Close();return BRepPrimAPI_MakeRevol(BRepBuilderAPI_MakeFace(p.Wire()).Face(),gp_Ax1(gp_Pnt(80,0,20),gp_Dir(0,1,0))).Shape()
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    parent=ROOT/'cad/exports/revAD_funnel1/summary.json';data=json.loads(parent.read_text());refs=dict(data['part_references']);old={n:read(REPO/r['path']) for n,r in refs.items()};parts=dict(old)
    removed=[];changed=[];rows=[]
    # These are DESIGN replacements, not operating collision-model deletion.
    def replaced(name):
        suffix=name[3:] if name.startswith(('F0_','F1_','F2_')) else ''
        return suffix.startswith(('SHAFT','BEARING_','PEDESTAL_','CAP_L','CAP_R','COUPLING_','DRUM_PIN'))
    for name in list(parts):
        if replaced(name):removed.append(name);del parts[name];del refs[name]
    rotor=cut(old['F0_DRUM'],cyl(8.015,(80,-3,20),8.5,(0,1,0)))
    rotor=fuse(rotor,ring(7.2,8.1,-1.5,.5));rotor=cut(rotor,ring(8.015,8.4,3.1,.6))
    hub=fuse(cyl(7,(80,-12,20),8,(0,1,0)),cyl(4,(80,-4,20),16,(0,1,0)))
    hub=fuse(hub,cyl(10.8,(80,-3.5,20),.5,(0,1,0)));hub=fuse(hub,cyl(4.8,(80,-1.5,20),.5,(0,1,0)))
    hub=fuse(hub,box(76,4.8,16,8,1.4,8));hub=fuse(hub,box(83,-11,14.5,5,6,11))
    hub=cut(hub,cyl(2.52,(80,-12.1,20),24.2,(0,1,0)),box(80,-12,19.7,9,8,.6),cyl(1.6,(85,-8,20.3),5.3),cyl(1.5,(85,-8,14.4),5.3))
    pressure=cut(ring(0,10.8,5,1),box(75.95,4.9,15.95,8.1,1.2,8.1))
    clip=cut(ring(7.2,8.35,3.1,.5),box(80,3,18.5,12,.8,3))
    adjust=cut(hex_y(13,6.6,3),cyl(4.025,(80,6.5,20),3.2,(0,1,0)),cyl(1,(83.9,8.1,20),4,(1,0,0)))
    screw=fuse(cyl(1.49,(85,-8,13.5),12),cyl(2.75,(85,-8,25.5),3))
    # Nominal socket is a real finite hex cut, not a virtual tool point.
    poly=BRepBuilderAPI_MakePolygon()
    for i in range(6):poly.Add(gp_Pnt(85+2.5/math.sqrt(3)*math.cos(i*math.pi/3),-8+2.5/math.sqrt(3)*math.sin(i*math.pi/3),26.5))
    poly.Close()
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec
    screw=cut(screw,BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(),gp_Vec(0,0,2.1)).Shape())
    module=dict(DRUM=rotor,CLUTCH_INPUT_HUB=hub,CLUTCH_BEARING=ring(4,8,-1,4),CLUTCH_LINER_L=ring(8.3,10.8,-3,.5),CLUTCH_LINER_R=ring(8.3,10.8,4.5,.5),CLUTCH_PRESSURE=pressure,CLUTCH_SPRING=disc_spring(),CLUTCH_ADJUSTER=adjust,CLUTCH_RETAINING_CLIP=clip,CLUTCH_CLAMP_BOLT=screw,CLUTCH_LOCK_PLUG=cyl(.99,(84,8.1,20),2.4,(1,0,0)))
    moved=[n for n in old if n.startswith('F0_MOTOR')]
    for n in moved:module[n[3:]]=translate(old[n],0,30,0)
    for i in range(3):
        for suffix,s in module.items():
            name=f'F{i}_{suffix}';shape=rotate(s,120*i)
            if not BRepCheck_Analyzer(shape).IsValid() or solid_count(shape)!=1 or volume(shape)<=0:raise ValueError('Invalid new solid '+name)
            export(shape,out/name);parts[name]=shape;refs[name]=ref(out/(name+'.step'));changed.append(name)
            rows.append(dict(part_ID=name,STEP=refs[name]['path'],STEP_SHA256=refs[name]['SHA256'],STL=ref(out/(name+'.stl'))['path'],volume_mm3=volume(shape),bounds_mm=bounds(shape),role='MOTOR/bearing boundary envelope' if suffix in ('MOTOR','CLUTCH_BEARING') else 'FINITE MAKE/PURCHASE INTERFACE CANDIDATE',material_basis='UNQUALIFIED make-material/spring/friction; motor/bearing source separately identified'))
    boxes={n:bounds(s) for n,s in parts.items()};hits=[]
    for n,m in itertools.combinations(parts,2):
        if n not in changed and m not in changed:continue
        if overlap(boxes[n],boxes[m]):
            v=common(parts[n],parts[m])
            if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    with (out/'CANDIDATE_CHANGED_BOM.csv').open('w') as f:
        fields=['part_ID','STEP','STEP_SHA256','STL','volume_mm3','bounds_mm','role','material_basis'];writer=csv.DictWriter(f,fields);writer.writeheader();writer.writerows(rows)
    result=dict(status='CANDIDATE_GEOMETRY_PASS' if not hits else 'CANDIDATE_INTERFERENCE_FAIL',scope='ACTUAL DIRECT-CLUTCH CAD CANDIDATE ONLY; NO RATED FORCE CAP OR FULL STAGE1/2',revision=a.tag,adopted=False,parent=ref(parent),parts=len(parts),removed_design_parts=removed,changed_parts=changed,part_references=refs,assembly=ref(out/'ASSEMBLY.step'),changed_BOM=ref(out/'CANDIDATE_CHANGED_BOM.csv'),interferences=hits,
        dimensions=dict(motor_axial_translation_mm=30,shaft_bore_mm=5.04,hub_bearing_journal_mm=8,bearing_boundary_mm=[8,16,4],friction_radii_mm=[8.3,10.8],faces=2,spring_nominal_thickness_mm=.25,adjuster_thread='CUSTOM M8x0.5 nominal envelopes; manufacturing gauge REQUIRED'),
        manufacturer_evidence=dict(motor='https://www.omc-stepperonline.com/nema-17-bipolar-45ncm-63-74oz-in-1-5a-42x42x39mm-4-wires-w-1m-cable-connector-17hs15-1504s1',bearing='https://www.nsk.com/engineering/688a-esm-md.html'),
        unresolved=['Relocated motor plate to Palm fastener path and existing Palm holes NOT requalified','Spring load/temperature/fatigue and liner friction NOT qualified; no actual limiter torque bound','Bearing parasitic drag is an additional torque bypass requiring a bound','Motor radial shaft loads/overhang and dynamic jam energy NOT yet qualified','Retaining clip, clamp, thread and spring strength NOT qualified','Unused inherited pin/plug holes in rotor need manufacturing redesign before adoption','Purchased bearing is a boundary model, no invented races or actual inertia','Full wire path, motion, assembly and all inherited release gates incomplete'],producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(parts),removed=len(removed),changed=len(changed),interferences=hits),indent=2))
if __name__=='__main__':main()
