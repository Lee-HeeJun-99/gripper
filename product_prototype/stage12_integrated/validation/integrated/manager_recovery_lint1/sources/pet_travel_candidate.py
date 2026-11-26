"""Rev AC candidate: provide axial travel revealed by independent finite coupon.
Only three PET ends shortened from RevAB. Not adopted; no old release transfer.
"""
import argparse,csv,json,sys,shutil
from pathlib import Path
from baseline_registry import ROOT,S1,S2,REPO,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cut,box,rotate,bounds,overlap,common,volume,export,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    parent=S2/'revised_cad/revAB_sliding_pet1';old=json.loads((parent/'summary.json').read_text())
    rows=list(csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open()));parts={};files={}
    changes={r['part']:r for r in old['modified']}
    for row in rows:
        name=row['part_ID'];f=parent/changes[name]['STEP'] if name in changes else S1/row['STEP']
        expected=changes[name]['STEP_SHA256'] if name in changes else row['STEP_SHA256']
        assert sha(f)==expected;parts[name]=read(f);files[name]=ref(f)
    # Without stop, prior fixed-rail coupon requires1.40643mm travel.
    # New nominal1.8mm = that result +0.15mm declared cut/datum +0.24357margin.
    # This is a candidate budget, NOT proof for actual flexible/frictional rail.
    source=ROOT/'validation/finger/finite_pet2/summary.json';e=json.loads(source.read_text())
    migration=max(r['axial_migration_m'] for r in e['controls_without_endstop'])*1000
    assert all(r['status']=='PASS' for r in e['controls_without_endstop'])
    end_gap=1.8;assert end_gap>migration+.15
    skin=cut(parts['F0_SKIN'],box(49,-20,-101,3,40,7.8)) # upper cut z=-93.2
    modified=[]
    for i in range(3):
        name=f'F{i}_SKIN';shape=rotate(skin,i*120);oldv=volume(parts[name])
        assert BRepCheck_Analyzer(shape).IsValid() and solid_count(shape)==1 and volume(shape)>0
        export(shape,out/name);parts[name]=shape;files[name]=ref(out/(name+'.step'))
        modified.append(dict(part_ID=name,old_volume_mm3=oldv,new_volume_mm3=volume(shape),STEP=files[name],STL=ref(out/(name+'.stl'))))
    boxes={n:bounds(s) for n,s in parts.items()};hits=[]
    for changed in modified:
        name=changed['part_ID']
        for other in parts:
            if name!=other and overlap(boxes[name],boxes[other]):
                v=common(parts[name],parts[other])
                if abs(v)>1e-8:hits.append(dict(a=name,b=other,common_mm3=v))
    assembly=out/'ASSEMBLY.step';w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs)
    assert w.Write(str(assembly))==IFSelect_RetDone
    reread=read(assembly);err=abs(volume(reread)-sum(volume(s) for s in parts.values()))/volume(reread)
    result=dict(status='CANDIDATE_GEOMETRY_PASS' if not hits and err<1e-8 else 'FAIL',revision=a.tag,parent='revAB_sliding_pet1',adopted=False,
        part_count=len(parts),changed=modified,part_references=files,assembly=ref(assembly),assembly_volume_relative=err,
        changed_vs_all_collisions=hits,nominal_end_gap_mm=end_gap,previous_coupon_free_travel_mm=migration,
        declared_cut_datum_budget_mm=.15,remaining_candidate_budget_mm=end_gap-migration-.15,
        geometry_evidence=ref(source),producer=ref(Path(__file__)),
        invalidated=['PET mass/inertia','finite PET/rail contact and end-stop results','whole prescribed motion/maxstock/cutting/drawings/BOM','assembled strength and material/fatigue'],
        preserved=['301rail geometry','root/palm/drivetrain geometry','RevABfront lip and independent rail capture'],
        next='Rerun actual shorter PET finite-rotation coupon, then actual whole-assembly motion/service/tolerances; no automatic Stage1 or Stage2 PASS')
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('part_references','modified')},indent=2))
if __name__=='__main__':main()
