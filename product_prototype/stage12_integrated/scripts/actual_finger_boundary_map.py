"""Actual RevAD STEP boundary inventory and finite distal sliding probes.

No clamp preload, friction, strength or deformed trajectory is invented.
The translated distal fragment is a local clearance probe, NOT a Finger solve.
"""
import argparse,json,shutil,sys
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,box,cut,translate,common,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAD_funnel1/summary.json';d=json.loads(src.read_text())
    names=['F0_SKIN','F0_RAIL_L','F0_RAIL_R','F0_ROOT_FRONT','F0_ROOT_BACK','F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_TENDON_WIRE']
    names=[n for n in names if n in d['part_references']]
    shapes={};inventory=[]
    for n in names:
        r=d['part_references'][n];path=REPO/r['path'];assert sha(path)==r['SHA256']
        s=read(path);shapes[n]=s;inventory.append(dict(part=n,STEP=r,bounds_mm=bounds(s),volume_mm3=volume(s)))
    skin=shapes['F0_SKIN'];b=bounds(skin)
    # The finite distal material fragment can translate axially without
    # imposing motion on root nodes or assuming a common Rail/PET curvature.
    fragment=BRepAlgoAPI_Common(skin,box(40,-30,-95,20,60,5)).Shape()
    assert volume(fragment)>0
    probes=[]
    for dz in (0,-.5,-1.5,-1.8,-2.0,1.0):
        moved=translate(fragment,0,0,dz);pairs=[]
        for n in ('F0_TERMINAL_FRONT','F0_TERMINAL_BACK','F0_RAIL_L','F0_RAIL_R'):
            other=shapes[n];dist=BRepExtrema_DistShapeShape(moved,other);dist.Perform();assert dist.IsDone()
            pairs.append(dict(other=n,common_mm3=common(moved,other),distance_mm=dist.Value()))
        probes.append(dict(distal_translation_Z_mm=dz,fragment_bounds_mm=bounds(moved),pairs=pairs))
    # Infer only the declared geometry datum, not a stiffness/clamp certificate.
    end_gap=b[2]-(-95.0)
    controls=dict(actual_nominal_end_matches_1p8=abs(end_gap-1.8)<1e-6,
                  nominal_fragment_no_positive_overlap=all(abs(v['common_mm3'])<1e-8 for v in probes[0]['pairs']),
                  all_sources_hash_checked=len(inventory)==len(names))
    ports=[dict(part='PET',root='F0_ROOT_FRONT/F0_ROOT_BACK clamp contact; axial hold depends on actual preload/friction or positive retention, not certified',terminal='finite lip/back unilateral transverse contact; axial end free until actual stop contact',axial_terminal_DOF='FREE_WITH_FINITE_STOPS; do not tie to Rail'),
           dict(part='RAIL_L/RAIL_R',root='same finite root clamp, separate elastic constituents',terminal='RevAB integral front pads capture Rail; preload/strength not certified',axial_terminal_DOF='FINITE_CAPTURE_CONTACT, not a PET tie'),
           dict(part='TENDON',terminal='factory nipple / blind receiver loads terminal body, then Rail pads and PET through unilateral contact',root='drum/idler route; no direct external force on PET assumed')]
    result=dict(status='BOUNDARY_GEOMETRY_INVENTORY_PASS' if all(controls.values()) else 'BOUNDARY_GEOMETRY_INVENTORY_FAIL',
        scope='Actual nominal RevAD STEP inventory and local distal fragment probes only',revision='revAD_funnel1',adopted=False,
        source=ref(src),producer=ref(out/'producer.py'),inventory=inventory,load_ports=ports,probes=probes,controls=controls,
        nominal_end_gap_mm=end_gap,coordinate_system='F0: X radial outward, Y circumferential, Z upward; SI m = CAD mm / 1000',
        rod_reference_mapping=dict(root_station_Z_mm=-7,rail_station_Z_mm=-95,rail_length_m=.088,PET_station_Z_mm=b[2],PET_length_m=(-7-b[2])/1000,
            note='Mapping datums only. Actual root compliance and channel friction are NOT validated by the independent rod reference.'),
        required_physics=['separate PET/Rail axial fields','finite terminal lips/stops and Rail pads','finite root clamp preload and retention','independent transverse contact and friction','actual tendon nipple and terminal contact'],
        excluded=['No deformed motion or force solution','No root clamp strength or friction certification','No implicit fixed PET distal displacement','No adoption of rod/BVP PASS as assembled Finger PASS'],whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
    raise SystemExit(0 if all(controls.values()) else 2)
if __name__=='__main__':main()
