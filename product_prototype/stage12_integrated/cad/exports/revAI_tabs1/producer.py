"""RevAI: preserve all drive locations, replace full annulus by three tabs.

Prove actual new Palm is a subset of AH Palm and needed mounting footprints
are unchanged. This permits ONLY monotone collision-screen reuse, not strength.
"""
import argparse,json,shutil,sys,itertools,math
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,rotate,export,volume,bounds,common,solid_count,overlap
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAH_pilot2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references']);parts={n:read(REPO/r['path']) for n,r in refs.items()}
    adsrc=ROOT/'cad/exports/revAD_funnel1/summary.json';ad=json.loads(adsrc.read_text());original=read(REPO/ad['part_references']['PALM']['path']);old=parts['PALM']
    tab=fuse(box(108,-18,-12,25,22,5),box(105,-15,-12,31,16,5))
    for x in (108,133):
        for y in (-15,1):tab=fuse(tab,cyl(3,(x,y,-12),5))
    palm=original
    for i in range(3):
        palm=fuse(palm,rotate(tab,120*i))
        for x in (93,127):palm=cut(palm,rotate(cyl(1.7,(x,-6.5,-13),7),120*i))
    assert BRepCheck_Analyzer(palm).IsValid() and solid_count(palm)==1 and volume(palm)>0
    added=volume(cut(palm,old));removed=volume(old)-volume(palm)
    support=[]
    for i in range(3):
        for x in (93,127):
            annulus=rotate(cut(cyl(5,(x,-6.5,-12),5),cyl(1.7,(x,-6.5,-12.1),5.2)),120*i)
            before=common(old,annulus);after=common(palm,annulus)
            support.append(dict(sector=i,radial_mount_mm=x,old_supported_volume_mm3=before,new_supported_volume_mm3=after,relative_change=abs(after-before)/max(abs(before),1e-30)))
    checks=dict(no_material_added=abs(added)<1e-8,all_mounting_footprints_preserved=all(r['relative_change']<1e-8 for r in support),positive_material_saving=removed>0)
    export(palm,out/'PALM');parts['PALM']=palm;refs['PALM']=ref(out/'PALM.step')
    b=bounds(palm);hits=[]
    for n,s in parts.items():
        if n!='PALM' and overlap(b,bounds(s)):
            v=common(palm,s)
            if abs(v)>1e-8:hits.append(dict(a='PALM',b=n,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='CANDIDATE_MONOTONE_GEOMETRY_PASS' if all(checks.values()) and not hits else 'FAIL',revision=a.tag,adopted=False,parent=ref(src),original_palm_source=ad['part_references']['PALM'],parts=len(parts),changed=[dict(part_ID='PALM',STEP=refs['PALM'],STL=ref(out/'PALM.stl'))],part_references=refs,assembly=ref(out/'ASSEMBLY.step'),interferences=hits,checks=checks,support=support,
        old_palm_volume_mm3=volume(old),new_palm_volume_mm3=volume(palm),removed_volume_mm3=removed,new_minus_old_volume_mm3=added,palm_volume_reduction_fraction=removed/volume(old),
        illustrative_removed_mass_kg_at_2700kg_m3=removed*1e-9*2700,
        design='Original230mm Palm plus three rounded local drive tabs, all old and new needed holes retained. No motor/shaft/Finger/tendon relocation.',
        collision_reuse_rule='All non-Palm STEP hashes unchanged, Palm subset and mounting-footprint invariance proven. Only prior bounded collision screens can be reused; no inherited material/strength/whole Stage1 PASS.',
        invalidated=['Palm loaded strength and compliance','Tab/root local stress and fastener reactions','Manufacturing contour/drawing/process','Mass/inertia if material grade is actually selected'],
        producer=ref(out/'producer.py'),whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('part_references','changed')},indent=2))
if __name__=='__main__':main()
