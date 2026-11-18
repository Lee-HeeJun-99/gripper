"""Actual recovery nominal-time observables plus explicit exact-time reference bridge."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def difference(x,y):
 x=np.asarray(x);y=np.asarray(y);absolute=float(np.linalg.norm(x-y));scale=max(float(np.linalg.norm(x)),float(np.linalg.norm(y)));return dict(absolute_error=absolute,relative_error_percent=100*absolute/scale if scale else 0)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--aligned',action='store_true');a=p.parse_args();names=['20261118_three_film_aligned_recovery1107','20261118_three_film_aligned_recovery_half1108','20261118_three_film_aligned_recovery_quarter1109'] if a.aligned else ['20261118_three_film_actual_recovery1101','20261118_three_film_actual_recovery_half1102','20261118_three_film_actual_recovery_quarter1103'];aligned=['20261118_three_film_recovery_base1097','20261118_three_film_recovery_half1098','20261118_three_film_recovery_quarter1099'];cases=[];bridges=[]
 for name,reference in zip(names,aligned):
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text());ref=ROOT/'results'/('autonomous_film_'+reference);proof=json.loads((ref/'summary.json').read_text())
  if meta['status']!='PASS' or meta['process']['exit_code'] or meta['sofa_errors'] or not meta['reference_accumulated_clock_exact'] or proof['status']!='PASS':raise ValueError('complete exact-own-clock actual/reference results required')
  if a.aligned and (not meta.get('aligned_observation') or not meta.get('public_next_dt_schedule_verified') or not meta.get('exact_common_target_time')):raise ValueError('actual all-context aligned schedule required')
  for path,m in ((src,meta),(ref,proof)):
   for file,digest in m['raw_hashes'].items():
    if sha(path/file)!=digest:raise ValueError('preserved raw changed')
  row=list(csv.DictReader((src/'three.states.csv').open()))[-1];exact=list(csv.DictReader((ref/'recovery.states.csv').open()))[-1];bridge={key:float(np.max(abs(np.fromstring(row[key],sep=' ')-np.fromstring(exact[key],sep=' ')))) for key in ('q','v')};bridges.append(dict(actual=name,exact_common_time_reference=reference,reference_summary_sha256=sha(ref/'summary.json'),state_max_abs=bridge,actual_time_offset_s=float(row['time'])-float(exact['time']),within_original_1e12_API_gate=max(bridge.values())<1e-12));cases.append((src,meta,row))
 if len({m['binary_sha256'] for _,m,_ in cases})!=1 or len({m['original_checkpoint_sha256'] for _,m,_ in cases})!=1 or len({m['common_nominal_target_time_s'] for _,m,_ in cases})!=1:raise ValueError('same actual binary/physical IVP/nominal observation required')
 comparisons=[]
 for i,j in ((0,1),(1,2),(0,2)):
  x,y=cases[i],cases[j];errors={key:difference(float(x[1]['metrics'][key]),float(y[1]['metrics'][key])) for key in ('U_skin','U_rails','U_attachment','K_film','K_body','minimum_gap_mm')}
  for key in ('q','v'):
   left=np.fromstring(x[2][key],sep=' ');right=np.fromstring(y[2][key],sep=' ');nf=(len(left)-6)//3
   for f in range(3):errors[f'film{f}_{key}']=difference(left[f*nf:(f+1)*nf],right[f*nf:(f+1)*nf])
   errors['body_'+key]=difference(left[-6:],right[-6:])
  comparisons.append(dict(cases=[names[i],names[j]],observables=errors,nominal_time_subset_gate='PASS' if all(e['relative_error_percent']<=.1 for e in errors.values()) else 'FAIL',actual_clock_difference_s=float(x[2]['time'])-float(y[2]['time'])))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');clock_identical=len({r['time'] for _,_,r in cases})==1;passed=all(r['nominal_time_subset_gate']=='PASS' for r in comparisons) and all(r['within_original_1e12_API_gate'] for r in bridges) and (not a.aligned or clock_identical);result=dict(status='PASS' if passed else 'FAIL',scope='actual exact-common-time FREE800us observable subset;NOT full contact-time/recovery certification' if a.aligned else 'actual nominal-time FREE800us observable subset with independent exact-time bridge;NOT exact cross-grid clock equality/full contact-time/recovery certification',nominal_time_gate_percent=.1,original_state_API_gate=1e-12,source_summary_hashes={n:sha(cases[i][0]/'summary.json') for i,n in enumerate(names)},comparisons=comparisons,exact_common_time_bridges=bridges,exact_cross_grid_clocks_identical=clock_identical,global_gripper_time_gate='FAIL remains;old contact/work/full-cycle gates are not replaced',recovery_completion='NOT ESTABLISHED');write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],scope=result['scope'],maximum_nominal_observable_error_percent=max(e['relative_error_percent'] for r in comparisons for e in r['observables'].values()),maximum_exact_time_bridge_state_error=max(max(b['state_max_abs'].values()) for b in bridges),exact_cross_grid_clocks_identical=result['exact_cross_grid_clocks_identical'])))
if __name__=='__main__':main()
