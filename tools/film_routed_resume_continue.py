"""Same binary,ACTUAL route-bound checkpoint;not an old-route transplant."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--steps',type=int,choices=(2,4,8,16,32),default=4);p.add_argument('--end-time',type=float,default=.01);p.add_argument('--compare-peak',action='store_true');p.add_argument('--reuse-journal-rows',action='store_true');p.add_argument('--owner-profile',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text())
 if m['status'] not in ('PASS','EXPERIMENTAL') or m['process']['exit_code'] or m['sofa_errors']:raise ValueError('qualified actual routed resume parent required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual resume evidence changed')
 if sha(src/'scene.scn')!=m['scene_sha256']:raise ValueError('actual parent Scene changed')
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);identity=tokens[4]
 if tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1' or int(tokens[3])!=a.checkpoint_step or identity!=m['identity'] or not time<a.end_time<=.03:raise ValueError('route-bound actual checkpoint/physical time required')
 end=time
 for i in range(a.steps):end+=dt
 if end>a.end_time+1e-14:raise ValueError('bounded accumulated endpoint exceeds allowed physical window')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();owner=scene.find('RoutedThreeFilmResumeODE')
 if owner is None:raise ValueError('only qualified NEW route owner admitted')
 binary=next(n.get('pluginName') for n in scene.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripThreeFilmResume.so'))
 if sha(binary)!=m['binary_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=m['sdk_runner_sha256']:raise ValueError('same source-bound binary/SDK required')
 old=json.loads((ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002/summary.json').read_text())
 for node in scene.findall('RequiredPlugin'):
  path=node.get('pluginName','')
  if path.startswith('/') and path!=binary and sha(path)!=old['plugins'].get(path):raise ValueError('legacy mapping dependency changed')
 forecast=2*m['process']['runtime_s']*a.steps/m['actual_steps']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');scene.set('time',format(time,'.17g'));owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(a.end_time,'.17g'))
 for node in scene.iter():
  for key,value in list(node.attrib.items()):
   if key in ('filename','displacementFilename','publicMassFilename') and value.startswith(str(src)):node.set(key,str(out)+value[len(str(src)):])
 owner.set('reuseJournalRows','1' if a.reuse_journal_rows else '0');owner.attrib.pop('ownerCostFilename',None)
 if a.owner_profile:owner.set('ownerCostFilename',str(out/'owner_cost.csv'))
 tree.write(out/'scene.scn');r=dict(status='BLOCKED',scope='same-binary actual routed persistent continuation;NOT wrapping/holding/lift/time/energy certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),identity=identity,checkpoint_magic=tokens[0],route_amplitude_mm=4.5,binary_sha256=sha(binary),sdk=str(SDK),sdk_runner_sha256=m['sdk_runner_sha256'],scene_sha256=sha(out/'scene.scn'),input_checkpoint_sha256=sha(out/'input.checkpoint'),start_time_s=time,dt_s=dt,actual_steps=a.steps,predicted_child_runtime_s=forecast,reuse_journal_rows=a.reuse_journal_rows,owner_profile=a.owner_profile,legacy_sampled_work='NOT RESTORED;excluded from physical work/splicing',root_reaction_work=None)
 if forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(status='FAIL',process=run,sofa_errors=errors)
 if run['exit_code']==0 and not errors:
  states=list(csv.DictReader((out/'three.states.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()))
  if len(states)!=a.steps or len(rows)!=9*a.steps:raise ValueError('incomplete actual routed continuation')
  clock=time;exact=True
  for s in states:clock+=dt;exact=exact and float(s['time'])==clock
  gap=min(float(s['minimum_gap']) for s in states);momentum=max(float(s['momentum_residual']) for s in states);vn=max(float(s['normal_velocity_residual']) for s in states);r.update(status='EXPERIMENTAL' if exact and gap>=-1e-10 and momentum<=1e-17 and vn<=1e-10 else 'FAIL',accumulated_clock_exact=exact,end_time_s=clock,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=vn)
  if a.compare_peak:
   control=ROOT/'results/autonomous_film_20261118_routed_coupled_peak1272';proof=json.loads((control/'summary.json').read_text())
   for f,d in proof['raw_hashes'].items():
    if sha(control/f)!=d:raise ValueError('continuous NEW route control changed')
   expected=list(csv.DictReader((control/'three.states.csv').open()))[a.checkpoint_step:a.checkpoint_step+a.steps];expected_rows=list(csv.DictReader((control/'three.rows.csv').open()))[(a.checkpoint_step-1)*9:(a.checkpoint_step+a.steps-1)*9]
   if len(expected)!=a.steps:raise ValueError('known continuous route horizon absent')
   api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected)) for k in ('q','v')};same_time=all(x['time']==y['time'] for x,y in zip(states,expected));r.update(status='PASS' if r['status']=='EXPERIMENTAL' and max(api.values())<1e-12 and same_time and rows==expected_rows else 'FAIL',reference_max_abs=api,whole_stage_rows_exact=rows==expected_rows,continuous_control_sha256=sha(control/'summary.json'),api_gate=1e-12)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('raw_hashes','process')}))
if __name__=='__main__':main()
