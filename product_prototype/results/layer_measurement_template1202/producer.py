"""Hardware-neutral SI measurement template/validator;never invents samples."""
import argparse,csv,json,math
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
FIELDS=['time_s','pressure_gauge_Pa','normal_load_N','bending_load_N','tip_displacement_m','stage']
def validate(rows,meta):
 if not rows:return dict(status='NOT MEASURED',samples=0,stiffness=None,hardware_test='NOT MEASURED')
 previous=-math.inf
 for r in rows:
  values=[float(r[k]) for k in FIELDS[:-1]]
  if not all(math.isfinite(v) for v in values) or values[0]<=previous:raise ValueError('finite strictly increasing SI timestamps required')
  if r['stage'] not in ('unloaded','preload','load','unload','recovery'):raise ValueError('explicit protocol stage required')
  previous=values[0]
 if meta.get('source_kind')!='LAB_MEASUREMENT' or not all(meta.get('calibration',{}).get(k) for k in ('clock','pressure','force','displacement')):return dict(status='BLOCKED_UNCALIBRATED_OR_NONLAB',samples=len(rows),stiffness=None,hardware_test='NOT QUALIFIED')
 return dict(status='PASS_DATA_FORMAT_ONLY',samples=len(rows),stiffness=None,hardware_test='NOT QUALIFIED:format alone is not a mechanical test')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--csv');p.add_argument('--metadata');a=p.parse_args()
 if a.csv:
  with Path(a.csv).open() as f:rows=list(csv.DictReader(f))
  print(json.dumps(validate(rows,json.loads(Path(a.metadata).read_text()))));return
 if not a.tag or Path(a.tag).name!=a.tag:raise ValueError('unique tag required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 with (out/'measurement.csv').open('w') as f:csv.writer(f).writerow(FIELDS)
 meta=dict(source_kind='NOT_MEASURED',units='SI;negative gauge pressure means vacuum relative to atmosphere',calibration=dict(clock=None,pressure=None,force=None,displacement=None),material_batch=None,geometry=None,pressure_regulator=None,leak_test=None,cycles=None,safety='No purchase or hardware actuation performed. Set pressure/load limits only after material/fixture qualification.');(out/'metadata.json').write_text(json.dumps(meta,indent=2));d=validate([],meta);(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
