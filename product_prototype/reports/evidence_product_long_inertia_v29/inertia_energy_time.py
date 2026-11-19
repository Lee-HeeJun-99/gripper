"""All-pair accumulated signed inventory comparison,including tiny residual FAILs."""
import argparse,itertools,json
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_inertia_energy_allcontacts608/summary.json';data=json.loads(src.read_text());records=[];series={}
 if data['missing_intervals']:raise ValueError('cannot silently sum missing intervals as zero')
 quantities=['sampled_coordinate_input_metric_work_J','contact_impulse_metric_work_J','rotating_mass_metric_transport_J','normal_constraint_metric_work_J','tangential_constraint_metric_work_J','signed_inventory_residual_J','row_work_reconstruction_residual_J']
 for row in data['records']:
  case=row['case'];previous=series.setdefault(case,[]);accum={name:row[name]+(previous[-1]['values'][name] if previous else 0.) for name in quantities};accum['actual_kinetic_energy_J']=row['actual_kinetic_energy_J'];previous.append(dict(time_s=row['time_s'],values=accum))
 for c,d in itertools.combinations(series,2):
  x=series[c];y=series[d];ratio=round(len(y)/len(x))
  if ratio*len(x)!=len(y):raise ValueError('unsupported time nesting')
  for k,u in enumerate(x):
   v=y[(k+1)*ratio-1]
   if abs(u['time_s']-v['time_s'])>1e-12:raise ValueError('noncommon actual times')
   for name,value in u['values'].items():
    absolute=abs(value-v['values'][name]);den=max(abs(value),abs(v['values'][name]));relative=absolute/den if den else 0.;records.append(dict(cases=[c,d],time_s=u['time_s'],quantity=name,absolute_error_J=absolute,relative_error=relative,status='PASS_SELECTED_SIGNED_VALUE' if relative<=.001 else 'FAIL'))
 result=dict(status='PASS_SELECTED_SIGNED_TIME' if all(r['status']!='FAIL' for r in records) else 'FAIL_SIGNED_TIME',scope='All-common-time/all-pair cumulative numerical inventory;zero/tiny residuals NOT ignored,NO relative-error floor. Signed identity closure is NOT physical heat/energy/time qualification.',producer_sha256=sha(Path(__file__)),input_sha256=sha(src),gate=.001,records=records,worst=max(records,key=lambda r:r['relative_error']),maximum_relative_errors={n:max(r['relative_error'] for r in records if r['quantity']==n) for n in quantities+['actual_kinetic_energy_J']})
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
