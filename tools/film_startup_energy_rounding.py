"""Reduction-only arbitrary precision audit;does not improve force/state precision."""
import argparse,csv,json,shutil,decimal,math
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_precise_startup_energy1694';m=json.loads((parent/'summary.json').read_text())
 if m.get('observer_validation')!='PASS':raise ValueError('qualified stage observer required')
 for f,d in m['raw_hashes'].items():
  if sha(parent/f)!=d:raise ValueError('archived audit changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');decimal.getcontext().prec=100;D=decimal.Decimal.from_float;rows=[]
 for steps,name in ((8,'base1688'),(16,'half1689'),(32,'quarter1690')):
  stage=ROOT/'results'/('autonomous_film_20261119_precise_startup_'+name)/'actual.csv.gauss4.csv';weights=list(csv.DictReader(stage.open()));values=list(csv.DictReader((parent/str(steps)/'process/stdout.log').open()));terms=[];exact=decimal.Decimal(0)
  for w,v in zip(weights,values[:-1]):
   h=float(w['weight_s']);t=float(v['tendon_power_Nmm_s']);d=float(v['damping_power_Nmm_s']);terms.extend((h*t,-h*d));exact+=D(h)*(D(t)-D(d))
  for key in ('U_skin','U_rails','U_attachment','K'):
   x=float(values[-1][key]);terms.append(-x);exact-=D(x)
  double=math.fsum(terms);rows.append(dict(steps=steps,legacy_partial_signed_defect_Nmm=m['trials'][str(steps)]['partial_signed_defect_Nmm'],fsum_double_product_defect_Nmm=double,decimal100_exact_binary_inputs_defect_Nmm=str(exact),power_and_energy_input_precision='unchanged binary64',root_reaction_work=None,physical_heat=None))
 write_json(out/'summary.json',dict(status='EXPERIMENTAL',scope='reduction-only roundoff separation;NOT new simulation/physical energy certification',source_summary_sha256=sha(parent/'summary.json'),precision_decimal_digits=100,trials=rows,original_time_FAIL='PRESERVED;no relative error floor or gate change',warning='exact decimal reduction cannot recover force/energy value quantization;residual is not heat'))
 print(json.dumps(rows))
if __name__=='__main__':main()
