"""Read-only SAME macro-IVP local release-grid comparison;not global time gate."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();cases=['20261119_stationary_window10_64_1582','20261119_stationary_window10_128_1588'];data=[]
 for name in cases:
  path=ROOT/'results'/('autonomous_film_'+name);m=json.loads((path/'summary.json').read_text())
  if m['status']!='PASS' or m.get('local_release_window_us')!=10:raise ValueError('completed same-window release references required')
  for f,d in m['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('source archive changed')
  for f,d in m['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('reference raw changed')
  if sha(path/'reference')!=m['binary_sha256']:raise ValueError('reference binary changed')
  row=next(csv.DictReader((path/'states.csv').open()));stages=list(csv.DictReader((path/'states.csv.rk.csv').open()));impulse=np.array([math.fsum(float(x['weight_s'])*np.fromstring(x['force'],sep=' ')[f] for x in stages) for f in range(3)])
  data.append((path,m,row,impulse))
 x,y=data
 if any(x[1][k]!=y[1][k] for k in ('source_hashes','input_checkpoint_sha256','binary_sha256','end_time_s','pre_h_s','admissible_root_lo_s','admissible_root_hi_s')):raise ValueError('SAME source/binary/public-mass IVP/root/macro endpoint required')
 result={}
 def compare(name,left,right):
  left=np.atleast_1d(left).astype(np.longdouble);right=np.atleast_1d(right).astype(np.longdouble);delta=float(np.linalg.norm(left-right));scale=float(max(np.linalg.norm(left),np.linalg.norm(right)));relative=delta/scale if scale else 0.;result[name]=dict(absolute_l2=delta,max_absolute=float(np.max(abs(left-right))),relative=relative,status='PASS' if relative<=.001 else 'FAIL')
 for field in ('q','v'):compare(field,np.fromstring(x[2][field],sep=' '),np.fromstring(y[2][field],sep=' '))
 compare('local_RK_contact_impulse_Ns',x[3],y[3]);compare('outgoing_normal_velocity_mm_s',x[1]['outgoing_normal_velocity_mm_s'],y[1]['outgoing_normal_velocity_mm_s'])
 start=float((x[0]/'input.checkpoint').read_text().split()[1]);compare('first_FREE_STAGE_offset_from_macro_start_s',x[1]['first_all_free_STAGE_time_s']-start,y[1]['first_all_free_STAGE_time_s']-start)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if all(z['status']=='PASS' for z in result.values()) else 'FAIL',scope='limited64/128 local release-grid observables ONLY;NOT macro-dt/ALL-pair/full time/energy/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summaries={cases[i]:sha(z[0]/'summary.json') for i,z in enumerate(data)},metrics=result,gate_relative=.001,stored_energy=None,tendon_work=None,whole_energy='BLOCKED',macro_time_convergence='NOT RUN',row_lifetime='no invented material history;FREE stage time is sampled,not exact continuous exit root');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
