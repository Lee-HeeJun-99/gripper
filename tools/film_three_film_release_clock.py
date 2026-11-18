"""Read-only distinguish exact absolute joins from quadrature-duration inventory."""
import argparse,csv,json,math,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='20261118_three_film_actual_clock_release1079');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS' or meta['process']['exit_code']:raise ValueError('complete actual release required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 rows=list(csv.DictReader((src/'three.release.stages.csv').open()));free=list(csv.DictReader((src/'three.release.free.csv').open()));groups=[rows[i:i+4] for i in range(0,len(rows),4)];nominal=float((src/'input.checkpoint').read_text().split()[2]);start=float(rows[0]['time']);end=float(free[-1]['time']);weights=math.fsum([float(r['weight_s']) for r in rows]+[float(r['weight_s']) for r in free]);joins=all(float(groups[i][-1]['time'])==float(groups[i+1][0]['time']) for i in range(len(groups)-1)) and float(rows[-1]['time'])==float(free[0]['time']);difference=weights-(end-start)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if joins and abs(weights-nominal)<1e-18 else 'FAIL',scope='read-only actual accumulated clock and quadrature duration inventory;NOT full time/energy gate',source_case=a.case,source_summary_sha256=sha(src/'summary.json'),binary_sha256=meta['binary_sha256'],absolute_stage_joins_exact=joins,nominal_macro_dt_s=nominal,absolute_clock_advance_s=end-start,sum_actual_quadrature_weights_s=weights,weight_minus_clock_advance_s=difference,weight_minus_nominal_dt_s=weights-nominal,existing_duration_inventory_gate_s=1e-18,interpretation='floating substep-duration versus accumulated-clock discrepancy;NOT physical dissipation or fabricated work');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
