"""Fail-closed coupon data inventory. Never certifies jamming or hardware.

Calibrated instrument readings still require fixture/compliance/pressure-field,
repeatability and material validation outside this parser.
"""
import argparse,csv,hashlib,json,math,statistics
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
FIELDS=('time_s','specimen_id','condition','cycle','branch','steady','force_N','displacement_m','pressure_Pa')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def analyze(rows,meta):
 if meta.get('data_origin') not in ('measured','synthetic_fixture'):raise ValueError('explicit data origin required')
 if meta.get('units')!={'force':'N','displacement':'m','pressure':'Pa','time':'s'}:raise ValueError('SI units required')
 for key in ('specimen_id','fixture_id','operator','test_date','calibration_files'):
  if not meta.get(key):raise ValueError('missing '+key)
 if set(meta['calibration_files'])!={'force','displacement','pressure'}:raise ValueError('three sensor calibration identities required')
 if len(rows)<6:raise ValueError('insufficient samples')
 groups={};last=-math.inf;seen=set()
 for r in rows:
  if set(r)!=set(FIELDS):raise ValueError('exact SI schema required')
  t,F,u,P=(float(r[k]) for k in ('time_s','force_N','displacement_m','pressure_Pa'))
  if not all(math.isfinite(x) for x in (t,F,u,P)) or t<=last or P<0:raise ValueError('nonfinite,nonmonotonic time or negative vacuum pressure difference')
  last=t
  if r['specimen_id']!=meta['specimen_id'] or r['branch'] not in ('loading','unloading') or r['steady'] not in ('0','1'):raise ValueError('specimen/branch/steady mismatch')
  if not r['condition'] or not r['cycle'].isdigit() or int(r['cycle'])<1:raise ValueError('condition and positive cycle required')
  seen.add(r['condition'])
  if r['steady']=='1' and r['branch']=='loading':groups.setdefault((r['condition'],r['cycle']),[]).append((F,u,P))
 if len(seen)<2:raise ValueError('paired pressure conditions required')
 result=[]
 for (condition,cycle),samples in sorted(groups.items()):
  if len(samples)<3 or len({F for F,u,P in samples})<3:raise ValueError('three distinct steady loading forces required pergroup')
  F=[x[0] for x in samples];u=[x[1] for x in samples];P=[x[2] for x in samples];fm=statistics.mean(F);um=statistics.mean(u);var=sum((x-fm)**2 for x in F);slope=sum((x-fm)*(y-um) for x,y in zip(F,u))/var
  if slope<=0:raise ValueError('nonpositive measured compliance;check polarity or fixture')
  intercept=um-slope*fm;err=max(abs(y-(intercept+slope*x)) for x,y in zip(F,u));result.append(dict(condition=condition,cycle=int(cycle),samples=len(samples),pressure_mean_Pa=statistics.mean(P),pressure_range_Pa=[min(P),max(P)],fitted_compliance_m_N=slope,fitted_offset_m=intercept,maximum_fit_residual_m=err))
 if {r['condition'] for r in result}!=seen or len({r['pressure_mean_Pa'] for r in result})<2:raise ValueError('missing usable condition or identical pressure means')
 cycles={r['cycle'] for r in result}
 if any({r['condition'] for r in result if r['cycle']==c}!=seen for c in cycles):raise ValueError('unpaired cycles')
 return dict(status='SYNTHETIC_PARSER_FIXTURE_ONLY' if meta['data_origin']=='synthetic_fixture' else 'CALIBRATED_DATA_INVENTORY_NOT_HARDWARE_PASS',records=result,hardware_test='NOT MEASURED' if meta['data_origin']=='synthetic_fixture' else 'NOT QUALIFIED_BY_IMPORTER',jamming_validation='NOT QUALIFIED',scope='Linear loading compliance fits,not EI unless fixture/beam assumptions validated. No stiffness ratio,pressure efficiency,grasp or product qualification. steady is recorded operator label,not verified equilibrium.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--metadata',type=Path,required=True);p.add_argument('--tag',required=True);a=p.parse_args();meta=json.loads(a.metadata.read_text());cal={}
 for sensor,record in meta.get('calibration_files',{}).items():
  file=a.metadata.parent/record['path']
  if not file.is_file() or sha(file)!=record['sha256']:raise ValueError('missing/hash-mismatched calibration '+sensor)
  cal[sensor]=dict(path=str(file.resolve()),sha256=sha(file))
 result=analyze(list(csv.DictReader(a.input.open())),meta);result['input_sha256']=sha(a.input);result['metadata_sha256']=sha(a.metadata);result['calibrations']=cal;out=BASE/'results'/a.tag
 if Path(a.tag).name!=a.tag:raise ValueError('unique basename tag required')
 out.mkdir(exist_ok=False);(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'input.csv').write_bytes(a.input.read_bytes());(out/'metadata.json').write_bytes(a.metadata.read_bytes());print(json.dumps(result))
if __name__=='__main__':main()
