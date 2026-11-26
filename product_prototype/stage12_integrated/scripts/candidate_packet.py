"""Actual candidate BOM / identity map. No copying old revision PASS flags."""
import argparse,csv,json
from pathlib import Path
from baseline_registry import ROOT,S1,REPO,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(source.read_text())
    out=ROOT/'bom'/a.tag;out.mkdir(parents=True,exist_ok=False)
    rows=list(csv.DictReader((S1/'bom/revAA_mbd1/STAGE1_BOM.csv').open()))
    for row in rows:
        r=d['part_references'][row['part_ID']];step=REPO/r['path'];row['STEP']=r['path'];row['STEP_SHA256']=r['SHA256'];row['STL']=str(step.with_suffix('.stl').relative_to(REPO))
        row['physical_qualification']='NOT QUALIFIED; CANDIDATE ONLY; no inherited Stage1 or Stage2 approval'
        if row['part_ID'].endswith('_SKIN'):
            row['actual_producer_detail']='Candidate PET end z=-93.200mm, end gap1.800mm; other root/taper/holes retained. See actual STEP; cut/datum +/-0.15mm provisional budget, not measured process.'
            row['interface_notes']='Independent PET end, not captured by old index boss. Finite channel geometry has unresolved deformed interference; do not fabricate/adopt on this packet.'
        elif row['part_ID'].endswith('_TERMINAL_FRONT'):
            row['actual_producer_detail']='RevAB integral rail pads and finite lip retained unchanged; deformed overlap FAIL under reconstructed fixture shapes.'
    bom=out/'CANDIDATE_BOM.csv'
    with bom.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    dump(out/'summary.json',dict(status='CANDIDATE_IDENTITY_PACKET_CREATED',candidate=ref(source),BOM=ref(bom),parts=len(rows),revision=a.candidate,producer=ref(Path(__file__)),adopted=False,stage1_release=False,stage2_release=False))
    print(json.dumps(dict(parts=len(rows),BOM=str(bom),adopted=False)))
if __name__=='__main__':main()
