"""Same-binary restart from an ACTUAL checkpoint;exclusive outputs,bounded steps.
No inference that completed frictionless contact is grasp/energy certification.
"""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--end-time',type=float,default=.01);p.add_argument('--compare1002',action='store_true');p.add_argument('--profile',action='store_true');a=p.parse_args()
 src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text())
 if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete qualified transfer or bounded actual continuation required')
 for n,h in meta['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('immutable parent raw changed:'+n)
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);token=tokens[4]
 if int(tokens[3])!=a.checkpoint_step or token!=meta['identity'] or not 1<=a.steps<=64 or not time<a.end_time<=.03 or time+dt*a.steps>a.end_time+1e-14:raise ValueError('explicit checkpoint identity/physical window required')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();owner=scene.find('ThreeFilmResumeODE');binary=next(n.get('pluginName') for n in scene.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripThreeFilmResume.so'))
 if sha(binary)!=meta['binary_sha256']:raise ValueError('same resume binary changed')
 estimate=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 if estimate>480:raise ValueError('profile-based child forecast exceeds480s;split only after transfer proof')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');scene.set('time',format(time,'.17g'));owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(a.end_time,'.17g'))
 for node in scene.iter():
  for k,v in list(node.attrib.items()):
   if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
 if a.profile:owner.set('ownerCostFilename',str(out/'owner_cost.csv'))
 tree.write(out/'scene.scn')
 result=dict(status='FAIL',scope='actual bounded persistent continuation;NOT release/wrapping/holding/lift/full energy',parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),checkpoint_sha256=sha(checkpoint),identity=token,binary_sha256=sha(binary),sdk=str(SDK),scene_sha256=sha(out/'scene.scn'),start_time=time,dt=dt,steps=a.steps,predicted_runtime_s=estimate,legacy_sampled_work='reset private ledger;NOT a continuous-work observation',stage_work_origin=time,root_reaction_work=None)
 run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;result['sofa_errors']=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'))
 if run['exit_code']==0 and not result['sofa_errors']:
  states=list(csv.DictReader((out/'three.states.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()));complete=len(states)==a.steps and len(rows)==9*a.steps
  if not complete:raise ValueError('incomplete accepted journals')
  gap=min(float(r['minimum_gap']) for r in states);mom=max(float(r['momentum_residual']) for r in states);vn=max(float(r['normal_velocity_residual']) for r in states);clock=time;clock_error=0
  for r in states:clock+=dt;clock_error=max(clock_error,abs(float(r['time'])-clock))
  result.update(status='EXPERIMENTAL' if gap>=-1e-10 and mom<=1e-17 and vn<=1e-10 and clock_error==0 else 'FAIL',end_time=clock,minimum_gap_mm=gap,momentum_max_Ns=mom,normal_velocity_max_mm_s=vn,accumulated_clock_error_s=clock_error)
  if a.compare1002:
   control=ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002';expected=list(csv.DictReader((control/'three.states.csv').open()))[a.checkpoint_step:a.checkpoint_step+a.steps]
   if len(expected)!=len(states):raise ValueError('saved continuous comparison unavailable')
   errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected)) for k in ('q','v')};exact_time=all(x['time']==y['time'] for x,y in zip(states,expected));erows=list(csv.DictReader((control/'three.rows.csv').open()))[(a.checkpoint_step-1)*9:(a.checkpoint_step+a.steps-1)*9];exact_rows=rows==erows
   result.update(status='PASS' if result['status']=='EXPERIMENTAL' and max(errors.values())<1e-12 and exact_time and exact_rows else 'FAIL',reference_max_abs=errors,stage_rows_exact=exact_rows,absolute_api_gate=1e-12)
  result['checkpoint_count']=len(list(out.glob('three.checkpoint_*.txt')))
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('raw_hashes','process')}))
if __name__=='__main__':main()
