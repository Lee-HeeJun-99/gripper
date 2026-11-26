"""Finite clamp-stack compression path audit; no bolt preload is invented."""
import argparse,json,math,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,bounds,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());refs=d['part_references'];rows=[]
    plate=read(REPO/refs['F0_MOTOR_PLATE']['path']);bridge=read(REPO/refs['F0_CLUTCH_GROUND_SPINDLE']['path'])
    for off in d['ground_bridge_bolt_offsets_mm']:
        x=110+off;column=cyl(2.5,(x,-15,20),12,(0,1,0));pb=bounds(BRepAlgoAPI_Common(plate,column).Shape());bb=bounds(BRepAlgoAPI_Common(bridge,column).Shape())
        gap=bb[1]-pb[4];name=f'F0_CLUTCH_GROUND_SPACER_{x}';present=name in refs
        closed=False;contact_areas=[];expected=math.pi*(3**2-1.7**2)
        if present:
            spacer=read(REPO/refs[name]['path']);sb=bounds(spacer);closed=abs(sb[1]-pb[4])<1e-6 and abs(sb[4]-bb[1])<1e-6
            for support,y in [(plate,pb[4]-.001),(bridge,bb[1])]:
                test=cut(cyl(3,(x,y,20),.001,(0,1,0)),cyl(1.7,(x,y-.0001,20),.0012,(0,1,0)))
                contact_areas.append(volume(BRepAlgoAPI_Common(support,test).Shape())/.001)
        rows.append(dict(offset_mm=off,plate_column_bounds_mm=pb,bridge_column_bounds_mm=bb,unsupported_axial_gap_mm=gap,spacer_present=present,spacer_closes_gap=closed,actual_annular_contact_areas_mm2=contact_areas,full_annular_area_mm2=expected,
            full_contact=present and all(abs(v/expected-1)<1e-6 for v in contact_areas)))
    ok=all(r['spacer_closes_gap'] and r['full_contact'] for r in rows)
    dump(out/'summary.json',dict(status='COMPRESSION_PATH_GEOMETRY_PASS' if ok else 'COMPRESSION_PATH_GEOMETRY_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),rows=rows,
        scope='Actual F0 nominal clamp-stack/contact footprint only; bolt preload, ground-plate attachment strength and manufacturing tolerance NOT qualified',whole_system_release=False))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',rows=rows),indent=2))
if __name__=='__main__':main()
