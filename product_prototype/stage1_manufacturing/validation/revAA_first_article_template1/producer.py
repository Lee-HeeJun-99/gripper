"""Blank physical inspection schema and fail-closed record checker.

No actual hardware readings are generated. Software completeness is not
material/strength qualification or authorization to power a gripper.
"""
import argparse,csv,json,shutil,hashlib
from pathlib import Path
from manufacturing_packet import ROOT
def evaluate(rows):
 missing=[];failed=[]
 for r in rows:
  if not all(r.get(k,'').strip() for k in ('measured_mm','operator','specimen_ID','gauge_ID','calibration_ID','timestamp')):missing.append(r['inspection_ID']);continue
  try:v=float(r['measured_mm']);ok=float(r['minimum_mm'])<=v<=float(r['maximum_mm'])
  except (ValueError,TypeError):ok=False
  if not ok:failed.append(r['inspection_ID'])
 return dict(status='FIRST_ARTICLE_NOT_MEASURED' if missing else 'FIRST_ARTICLE_DIMENSIONAL_FAIL' if failed else 'FIRST_ARTICLE_DIMENSIONAL_RECORDS_WITHIN_LIMITS',missing=missing,failed=failed,scope='Entered physical dimensional records only; no strength/preload/free-spin/fatigue/powered approval.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);p.add_argument('--records');a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';j=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 if a.records:rows=list(csv.DictReader(Path(a.records).open()))
 else:
  specs=[('journal_D',4.982,4.990),('journal_coax_DIAMETER',0,.005),('housing_min_bore',16.025,16.035),('housing_coax_DIAMETER',0,.010),('plain_grip_D',4.390,4.400),('groove_root_D',21.850,21.860),('idler_running_gap',.025,.035),('receiver_running_gap',.025,.035),('fork_gap_minus_finished_sleeve',.005,.010),('left_bearing_endplay',.01,.15),('right_bearing_endplay',.58,.74),('cable_D',.48,.52),('finished_cable_outlet_length',190.5593251034887,191.0593251034887)]+[(f'matched_receiver_screw_{k}_tip',.50,.65) for k in range(4)]
  rows=[dict(inspection_ID=f'F{i}_{n}',case=a.case,case_SHA256=hashlib.sha256(src.read_bytes()).hexdigest(),minimum_mm=lo,maximum_mm=hi,measured_mm='',operator='',specimen_ID='',gauge_ID='',calibration_ID='',timestamp='',state='NOT MEASURED') for i in range(3) for n,lo,hi in specs]
 with (out/'INSPECTION_RECORDS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 result=evaluate(rows);result.update(case=a.case,records=len(rows),all_blank=all(not r['measured_mm'] for r in rows),input_case_SHA256=hashlib.sha256(src.read_bytes()).hexdigest(),actual_hardware_execution=False,design_release_affected=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],records=len(rows),missing=len(result['missing']),hardware_run=False)))
if __name__=='__main__':main()
