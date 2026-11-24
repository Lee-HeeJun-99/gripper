"""Distinguish accepted solid geometry from Native buffer-mediated support.
Never erase real constraint impulses because physical facets are separated.
"""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha

def part(path):return re.sub(r'/(?:Point|Line|Triangle)CollisionModel\d+$','',path)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);geom=BASE/'results/capillary_clearance1705';src=BASE/'results/capillary_hold1700';records=json.loads((geom/'uncleared.json').read_text());run=json.loads((geom/'summary.json').read_text());root=ET.parse(src/'scene.scn').getroot();prox=next(n for n in root if 'Proximity'in n.tag);buffer=float(prox.get('contactDistance'));bad=[r for r in records if r['status']!='SEPARATED' or r['axis_gap_mm']<=0];keys=set()
 for r in records:
  names=[f'/guides{v[0]}/cable{v[1]}/{v[2]}' for v in (r['left'],r['right'])];keys.add((r['time_s'],*sorted(names)))
 active={}
 for r in csv.DictReader((src/'response_rows.csv').open()):
  names=[r[k] for k in ('model0','model1')]
  if not all('/guides'in x for x in names) or names[0].split('/')[1]==names[1].split('/')[1] or float(r['lambda_Ns'])==0:continue
  key=(float(r['time_s']),*sorted(part(x) for x in names));active[key]=active.get(key,0)+1
 intersect=set(active)&keys;sector=json.loads((BASE/'results/sector_route1707/summary.json').read_text());current=next(r for r in sector['results'] if r['case']==src.name)
 d=dict(status='SAVED_SOLIDS_SEPARATE_BUT_NATIVE_INTERNAL_SUPPORT_REMAINS' if not bad and active else 'UNRESOLVED_GEOMETRY_OR_RESPONSE',actual_pair_frames=run['pair_frames'],uncleared_buffer_pair_frames=len(records),nonseparated_convex_envelope_pair_frames=len(bad),minimum_positive_recorded_axis_gap_mm=min(r['axis_gap_mm'] for r in records),maximum_recorded_axis_gap_mm=max(r['axis_gap_mm'] for r in records),Native_contactDistance_mm=buffer*1000,active_response_pair_times=len(active),active_response_pair_times_with_accepted_gap_within_buffer=len(intersect),active_response_pair_times_not_in_accepted_buffer_list=len(set(active)-keys),worst_fixed_pose_sector_excess_mm=current['maximum_actual_sector_excess_mm'],sector_excess_after_removing_only_global_buffer_mm=current['maximum_actual_sector_excess_mm']-buffer*1000,scope='Full saved convex-envelope screen certified strict positive physical separation at sampled poses,including all76inside-buffer cases. Native nonzero internal impulses STILL exist and are not ignored. Detection/free/accepted stages differ; unmatched pair-times do NOT alone prove detector error. No swept-solid or all-time no-contact proof. Zero-margin alone cannot restore the WORST fixed-pose own-sector certificate (1.832mm excess vs0.2mm buffer);this is NOT a new dynamic zero-buffer trial or universal design impossibility. Do not weaken old margin/speed gates or declare unbraced success.',input_sha256={str(f.relative_to(BASE)):sha(f) for f in [geom/'summary.json',geom/'uncleared.json',src/'scene.scn',src/'response_rows.csv',BASE/'results/sector_route1707/summary.json']},source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
