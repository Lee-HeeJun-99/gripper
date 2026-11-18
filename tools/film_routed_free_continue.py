"""Bounded actual FREE_V3 continuation, with optional exact suffix resume audit.

Same compiled release owner and physical checkpoint; no state projection,
legacy sampled-work reconstruction, or extrapolated clock.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',default='20261118_routed_release_actual1360');p.add_argument('--provider',default='20261118_routed_release_actual1360');p.add_argument('--checkpoint-step',type=int,default=137);p.add_argument('--steps',type=int,choices=(1,2,4,8),default=4);p.add_argument('--compare');a=p.parse_args()
 provider=ROOT/'results'/('autonomous_film_'+a.provider);proof=json.loads((provider/'summary.json').read_text());src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt'
 rebind=m['binary_sha256']!=proof['binary_sha256']
 if rebind and (proof.get('parent_summary_sha256')!=sha(src/'summary.json') or proof.get('change_scope') not in ('strict separating-plane exclusion ONLY','explicit FREE endpoint50ms ONLY')):raise ValueError('unqualified compiled handoff')
 if proof['status']!='PASS' or m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors'] or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('completed exact actual released checkpoint required')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled source archive changed')
 tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);end=time
 if tokens[0]!='REGRIP_ROUTED_FREE_V3' or tokens[4]!=m['identity'] or dt!=.0002:raise ValueError('explicit route/released clock schema required')
 for i in range(a.steps):end+=dt
 if end>proof.get('maximum_resume_end_s',.03):raise ValueError('explicit compiled FREE physical interval only')
 binary=ROOT/proof['build_relative']/'libReGripThreeFilmRelease.so'
 if sha(binary)!=proof['binary_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=proof['sdk_runner_sha256'] or sha(src/'scene.scn')!=m['scene_sha256']:raise ValueError('binary/SDK/scene changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');before=tokens.copy();tokens[4]=proof['identity'];(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
 if before[:4]+before[5:]!=tokens[:4]+tokens[5:]:raise ValueError('physical checkpoint payload changed')
 # Conservative measured former coupled eight-step cost; no timing speedup assumed.
 costsrc=ROOT/'results/autonomous_film_20261118_routed_unload_begin1307/summary.json';cost=json.loads(costsrc.read_text());forecast=2*cost['process']['runtime_s']*a.steps/cost['actual_steps']+30
 r=dict(status='BLOCKED',scope='bounded actual separated routed continuation;NOT full recovery/time/energy/wrapping/holding/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent_summary_sha256=sha(src/'summary.json'),provider_summary_sha256=sha(provider/'summary.json'),input_checkpoint_sha256=sha(checkpoint),binary_sha256=sha(binary),identity=proof['identity'],build_relative=proof['build_relative'],sdk=str(SDK),sdk_runner_sha256=proof['sdk_runner_sha256'],start_time_s=time,dt_s=dt,actual_steps=a.steps,expected_end_time_s=end,predicted_child_runtime_s=forecast,cost_profile_summary_sha256=sha(costsrc),normal_velocity_residual=None,root_reaction_work=None,legacy_sampled_work='NOT restored;excluded ALL',time_convergence='NOT RUN')
 if forecast>480:write_json(out/'summary.json',r);return
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmAccelerationReleaseODE')
 if owner is None:owner=scene.find('RoutedThreeFilmFreeODE')
 if owner is None:raise ValueError('released actual owner missing')
 # Preserve inherited maxSteps=64 frozen pilot CAP. Actual -n and endTime
 # independently bound this run; do not spoof the accepted step counter.
 if owner.get('maxSteps')!='64':raise ValueError('frozen compiled pilot cap differs')
 owner.tag='RoutedThreeFilmFreeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(end,'.17g'));owner.set('identity',proof['identity'])
 for node in scene.iter():
  if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmRelease.so'):node.set('pluginName',str(binary))
  for k,v in list(node.attrib.items()):
   if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
 tree.write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');write_json(out/'summary.json',dict(r,status='NOT RUN'))
 run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(status='FAIL',process=run,sofa_errors=errors)
 if run['exit_code']==0 and not errors:
  rows=list(csv.DictReader((out/'three.states.csv').open()));clock=time;exact=True
  for row in rows:clock+=dt;exact=exact and float(row['time'])==clock
  gap=min(float(x['minimum_gap']) for x in rows);momentum=max(float(x['momentum_residual']) for x in rows);valid=len(rows)==a.steps and exact and gap>=-1e-10 and momentum<=1e-17 and all(x['normal_velocity_residual']=='null' for x in rows)
  r.update(status='PASS' if valid else 'FAIL',accumulated_clock_exact=exact,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,end_time_s=clock)
  if a.compare:
   other=ROOT/'results'/('autonomous_film_'+a.compare);om=json.loads((other/'summary.json').read_text());expected={float(x['time']):x for x in csv.DictReader((other/'three.states.csv').open())}
   if om['status']!='PASS' or om['binary_sha256']!=sha(binary) or any(sha(other/f)!=d for f,d in om['raw_hashes'].items()):raise ValueError('completed unchanged suffix reference required')
   delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(expected[float(x['time'])][k],sep=' ')))) for x in rows) for k in ('q','v')}
   stages=list(csv.DictReader((out/'three.free.stages.csv').open()));oldstages={(x['macro'],x['kind'],x['time']):x for x in csv.DictReader((other/'three.free.stages.csv').open())};stage_exact=all(oldstages.get((x['macro'],x['kind'],x['time']))==x for x in stages)
   snapshots=list(out.glob('three.checkpoint_*.txt'));snapshot_exact=all((other/x.name).exists() and x.read_text().split()==(other/x.name).read_text().split() for x in snapshots)
   r.update(suffix_reference_sha256=sha(other/'summary.json'),suffix_max_abs=delta,all_free_stages_exact=stage_exact,full_physical_checkpoint_tokens_exact=snapshot_exact)
   if max(delta.values())>1e-12 or not stage_exact or not snapshot_exact:r['status']='FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
