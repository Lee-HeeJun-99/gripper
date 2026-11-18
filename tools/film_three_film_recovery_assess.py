"""All-pair same-time independent recovery comparison;never whole-gripper PASS."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3);p.add_argument('--duration',type=float,choices=(.0008,.0064),default=.0008);a=p.parse_args();names=a.cases or ['20261118_three_film_recovery_base1097','20261118_three_film_recovery_half1098','20261118_three_film_recovery_quarter1099'];cases=[]
 for name in names:
  path=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((path/'summary.json').read_text())
  if meta['status']!='PASS' or meta['run']['exit_code']:raise ValueError('all complete independent references required')
  if meta.get('duration_s',.0008)!=a.duration:raise ValueError('reference physical horizon differs')
  for file,digest in meta['raw_hashes'].items():
   if sha(path/file)!=digest:raise ValueError('independent raw changed')
  state=list(csv.DictReader((path/'recovery.states.csv').open()))[-1];cases.append((path,meta,state))
 if len({x[1]['binary_sha256'] for x in cases})!=1 or len({x[1]['actual_checkpoint_sha256'] for x in cases})!=1 or len({x[1]['metrics']['time'] for x in cases})!=1:raise ValueError('same binary/physical IVP/exact observation time required')
 comparisons=[];physical_pass=True;momentum_pass=all(float(x[1]['metrics']['momentum_Ns'])<=1e-17 for x in cases)
 def compare(x,y):
  x=np.asarray(x);y=np.asarray(y);absolute=float(np.linalg.norm(x-y));scale=max(float(np.linalg.norm(x)),float(np.linalg.norm(y)));relative=absolute/scale if scale else 0;return dict(absolute_error=absolute,relative_error_percent=100*relative,pass_0p1_percent=relative<=.001)
 for i,j in ((0,1),(1,2),(0,2)):
  left,right=cases[i],cases[j];errors={key:compare(float(left[1]['metrics'][key]),float(right[1]['metrics'][key])) for key in ('U_skin','U_rails','U_attachment','K_film','K_body','minimum_gap_mm')}
  for key in ('q','v'):
   x=np.fromstring(left[2][key],sep=' ');y=np.fromstring(right[2][key],sep=' ');nf=(len(x)-6)//3
   for f in range(3):errors[f'film{f}_{key}']=compare(x[f*nf:(f+1)*nf],y[f*nf:(f+1)*nf])
   errors['body_'+key]=compare(x[-6:],y[-6:])
  pair_pass=all(e['pass_0p1_percent'] for e in errors.values());physical_pass&=pair_pass;comparisons.append(dict(cases=[names[i],names[j]],same_actual_observation_time=True,observables=errors,subset_time_gate='PASS' if pair_pass else 'FAIL',momentum_residual_difference_diagnostic=compare(float(left[1]['metrics']['momentum_Ns']),float(right[1]['metrics']['momentum_Ns']))))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if physical_pass and momentum_pass else 'FAIL',scope='independent same-IVP FREE recovery observable subset,NOT actual SOFA/full-cycle time/recovery certificate',duration_s=a.duration,source_summary_hashes={n:sha(cases[i][0]/'summary.json') for i,n in enumerate(names)},physical_time_gate_percent=.1,momentum_absolute_gate_Ns=1e-17,momentum_gate='PASS' if momentum_pass else 'FAIL',comparisons=comparisons,full_gripper_time_gate='FAIL remains:contact/stage-work/full-cycle gates not requalified',recovery_completion='NOT ESTABLISHED');write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],scope=result['scope'],pairs=[dict(cases=r['cases'],gate=r['subset_time_gate'],maximum_observable_error_percent=max(e['relative_error_percent'] for e in r['observables'].values())) for r in comparisons])))
if __name__=='__main__':main()
