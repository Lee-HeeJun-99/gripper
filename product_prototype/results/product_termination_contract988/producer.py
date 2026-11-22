"""Supplier terminal dimension gate,not wire/anchor strength qualification."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def fit(diameter,channel,bore):
 lo,hi=diameter
 if not (0<lo<=hi and channel>0 and bore>0):raise ValueError('positive ordered geometry required')
 return dict(channel_clearance_range_mm=[channel-hi,channel-lo],all_sizes_fit_channel=bool(channel>hi),minimum_retaining_radial_shoulder_mm=(lo-bore)/2,positive_shoulder_all_sizes=bool(lo>bore))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'config/termination_candidates_v48.json';cfg=json.loads(src.read_text());records=[dict(item=r['item'],**fit(r['diameter_mm'],1.5,1.2)) for r in cfg['candidates']]
 result=dict(status='TERMINAL_CATALOG_DIMENSION_SCREEN_NOT_QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,BASE/'results/product_drum_contract962/summary.json')},records=records,actual_pullout_N=None,fabrication_ready=False,scope='Existing CADdrumfreechannel1.5mm,Eyeletbore1.2mm;nominaldesign dimensions not process tolerances. Catalog NI000001maxD2.8 andKU000016maxD1.8 each exceed channel. KUminimumD1.2 giveszero shoulderatbore1.2;NOTpositive retention across catalogrange. NIminimumD2.2 givespositive geometricshoulderonly,NOTstrength. No swagingprocess/preload/material/friction/fatigue or Native approval.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
