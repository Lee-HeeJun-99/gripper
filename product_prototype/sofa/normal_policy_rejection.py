"""Append-only policy verdicts;do not rewrite invalid Native partial Raw."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records={};files=[]
 for case in ('layer_local_slip1216','layer_local_friction1217'):
  src=BASE/'results'/case;file=src/'rigid.csv';rows=list(csv.DictReader(file.open()));first=None
  for r in rows:
   if not np.isfinite(np.fromstring(r['rigid_q'],sep=' ')).all() and first is None:first=float(r['time_s'])
  raw=json.loads((src/'summary.json').read_text());records[case]=dict(status='FAIL_NONFINITE_AND_TIMEOUT',first_nonfinite_accepted_time_s=first,raw_status=raw['status'],runtime_s=raw['process']['runtime_s'],outputs=len(rows),cause='UNKNOWN;do not interpret later trajectory/friction');files.extend([file,src/'summary.json'])
 records['surface_normals_mu0']=dict(status='FAIL_FRICTIONLESS_COMPONENT_EXPECTATION',evidence='contact_gap_assess1215',description='Support restored but lateral contact force−0.01N cancels0.01N applied force atmu0;not validated flat frictionless sliding or jamming')
 d=dict(status='REJECT_NORMAL_POLICIES_FOR_PRODUCT',records=records,physical_validation='NOT QUALIFIED',scope='Specific fixture/load/geometry only;not universal SOFA component verdict. Existing Raw/NaN evidence untouched,old FAIL unchanged.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in files});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
