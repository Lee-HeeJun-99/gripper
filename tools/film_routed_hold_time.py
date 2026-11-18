"""All-pair, every common macro-time Hold test; retain tiny work residuals."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');data=[];proof=[];identity=None
 for case in a.cases:
  src=ROOT/'results'/('autonomous_film_'+case);m=json.loads((src/'summary.json').read_text());key=(m['input_checkpoint_sha256'],m['binary_sha256'],m['control'],m['source_hashes'])
  if m['status']!='PASS' or m['process']['exit_code'] or sha(src/'input.checkpoint')!=m['input_checkpoint_sha256'] or sha(src/'states.csv')!=m['raw_hashes']['states.csv']:raise ValueError('complete unchanged same-IVP reference required')
  if identity is None:identity=key
  elif key!=identity:raise ValueError('different initial state/control/compiled model')
  tokens=(src/'input.checkpoint').read_text().split();q0=np.array(list(map(float,tokens[5:1958])));rows=list(csv.DictReader((src/'states.csv').open()));values=[];previous={k:0. for k in ('tendon_work','external_work','damping_work','normal_work')}
  for row in rows:
   q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ')
   d=dict(film_q_change=q[:-6]-q0[:-6],film_velocity=v[:-6],body_displacement=q[-6:-3]-q0[-6:-3],body_linear_velocity=v[-6:-3],body_angular_velocity=v[-3:],normal_force=np.fromstring(row['force'],sep=' '))
   d.update({k:np.asarray(float(row[k])) for k in ('U_skin','U_rails','U_attachment','K')})
   for k in previous:
    z=float(row[k]);d[k]=np.asarray(z);d['interval_'+k]=np.asarray(z-previous[k]);previous[k]=z
   values.append((float(row['time']),d))
  if len(values)!=8:raise ValueError('incomplete Hold horizon')
  data.append(values);proof.append(dict(case=case,summary_sha256=sha(src/'summary.json'),refinement=m['refinement'],runtime_s=m['process']['runtime_s']))
 if sorted(x['refinement'] for x in proof)!=[1,2,4]:raise ValueError('base/half/quarter required')
 metrics=[]
 for i,j in itertools.combinations(range(3),2):
  if proof[i]['refinement']>proof[j]['refinement']:i,j=j,i
  for (t,x),(u,y) in zip(data[i],data[j]):
   if t!=u:raise ValueError('public accumulated clocks differ;no interpolation')
   for k in x:
    absolute=float(np.linalg.norm(x[k]-y[k]));reference=float(np.linalg.norm(y[k]));relative=absolute/reference if reference else (0. if absolute==0. else None)
    metrics.append(dict(pair=[proof[i]['case'],proof[j]['case']],time_s=t,metric=k,absolute_error=absolute,reference_norm=reference,relative_error=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL'))
 failed=[x for x in metrics if x['status']=='FAIL'];by={k:max((x['relative_error'] if x['relative_error'] is not None else float('inf')) for x in metrics if x['metric']==k) for k in data[0][0][1]}
 result=dict(status='FAIL' if failed else 'PASS',scope='same saved actual10ms IVP,shared-kernel reference10..11.6ms,every common endpoint and interval,all three pairs;NOT fine actual SOFA/full-cycle time certification',relative_gate=.001,provenance=proof,metrics=metrics,maximum_relative_error_by_metric={k:(v if np.isfinite(v) else None) for k,v in by.items()},failed_metrics=len(failed),normal_work_note='numerical constraint-work residual retained with no absolute exemption;NOT heat',full_energy_gate='BLOCKED',full_time_gate='FAIL remains',root_reaction_work=None)
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='metrics'}))
if __name__=='__main__':main()
