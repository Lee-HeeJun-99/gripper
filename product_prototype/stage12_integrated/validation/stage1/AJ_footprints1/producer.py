"""Actual entire motor-foot contact preservation, not just six bolt annuli."""
import argparse,json,shutil,sys
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,translate,common,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/stage1'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAJ_idler1/summary.json';parent=ROOT/'cad/exports/revAH_pilot2/summary.json';d=json.loads(src.read_text());old=json.loads(parent.read_text());palm=read(REPO/d['part_references']['PALM']['path']);previous=read(REPO/old['part_references']['PALM']['path']);rows=[]
    for i in range(3):
        n=f'F{i}_MOTOR_PLATE';assert d['part_references'][n]==old['part_references'][n]
        plate=read(REPO/d['part_references'][n]['path']);slab=BRepAlgoAPI_Common(plate,box(-160,-160,-7,320,320,.001)).Shape();probe=translate(slab,0,0,-.001)
        before=common(previous,probe);after=common(palm,probe);fraction=abs(after-before)/max(abs(before),1e-30)
        rows.append(dict(part=n,footprint_area_mm2=volume(slab)/.001,old_supported_area_mm2=before/.001,new_supported_area_mm2=after/.001,relative_change=fraction))
    ok=all(r['old_supported_area_mm2']>0 and r['relative_change']<1e-8 for r in rows)
    dump(out/'summary.json',dict(status='FULL_MOTOR_FOOTPRINT_PRESERVATION_PASS' if ok else 'FAIL',scope='Actual nominal foot contact geometry only, no preload, pressure/strength or support compliance',candidate=ref(src),parent=ref(parent),producer=ref(out/'producer.py'),rows=rows,whole_system_release=False))
    print(json.dumps(dict(status='PASS' if ok else 'FAIL',rows=rows),indent=2))
if __name__=='__main__':main()
