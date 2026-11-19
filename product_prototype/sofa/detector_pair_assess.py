"""Public narrowphase pair provenance. Counts are NOT contact area or force."""
import argparse,json,collections
from pathlib import Path
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('complete probe required')
 rows=read(src/'detection_pairs.csv');counts=collections.Counter();hold=collections.Counter();first={}
 for r in rows:
  paths=(r['model0'],r['model1'])
  if not any('/object/' in x for x in paths):continue
  other=paths[1] if '/object/' in paths[0] else paths[0];label='skin' if '/skinCollision/' in other else 'rail' if '/railCollision/' in other else 'guide' if '/guides' in other else 'support' if '/floor/' in other else 'other';counts[label]+=1;t=float(r['accepted_time_s']);first.setdefault(label,t)
  if 1.6-1e-12<=t<=2.+1e-12:hold[label]+=1
 result=dict(status='FAIL_SKIN_PROVENANCE' if not counts['skin'] else 'DETECTOR_SKIN_CANDIDATES_ONLY',scope='actual detector model pairs,not per-row multiplier ownership,actual force,contact area or accepted-state complementarity',case=a.case,object_pair_samples=dict(counts),hold_object_pair_samples=dict(hold),first_detected_pair_output_accepted_clock_s=first,clock='detector runs earlier in the native step;accepted clock labels observation,not continuous event time',input_sha256=sha(src/'detection_pairs.csv'),source_sha256=sha(Path(__file__)),binary_sha256=meta['binary_sha256']);(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
