"""Actual V5 used/next-dt plan restore;optional explicit COMPLETED-plan extension."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--compare',action='store_true');p.add_argument('--restart-plan',action='store_true');p.add_argument('--extended-build',action='store_true');p.add_argument('--value-clearance',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text())
 if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete qualified actual V5 parent required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('parent raw changed')
 checkpoint=src/f'three.checkpoint_{a.step}.txt';tokens=checkpoint.read_text().split()
 if tokens[0]!='REGRIP_PERSISTENT_OBSERVATION_V5':raise ValueError('versioned complete V5 state required')
 value=lambda label:tokens[tokens.index(label)+1];remaining=int(value('STEPS_REMAINING'));nominal=float(value('NOMINAL_DT'));time=float(tokens[1]);next_dt=float(value('EXPECTED_NEXT_DT'));total=int(value('TOTAL_STEPS'));target=float(value('OBSERVATION_END'))
 if a.restart_plan:
  if remaining!=0 or a.compare or a.steps!=total:raise ValueError('explicit new full plan only from a completed V5;not a continuous-run comparison')
  target=time+.0008;next_dt=nominal
 elif remaining==0 or not 1<=a.steps<=remaining:raise ValueError('resume cannot exceed restored remaining budget')
 extended_parent=bool(meta.get('extended_owner') or meta.get('extended_build'))
 if target>(.038 if a.extended_build or extended_parent else .032):raise ValueError('separate qualified recovery physical cap exceeded')
 forecast=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 if forecast>480:raise ValueError('profiled resume forecast exceeds480s')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();owner=scene.find('ThreeFilmPersistentRecoveryODE')
 if owner is None:owner=scene.find('ThreeFilmExtendedRecoveryODE')
 if owner is None:raise ValueError('actual persistent plan owner required')
 binary=next(n.get('pluginName') for n in scene.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripThreeFilmRecovery.so'))
 if sha(binary)!=meta['binary_sha256']:raise ValueError('qualified V5 DLL changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');original=tokens.copy()
 extension=None
 if a.extended_build:
  if not a.restart_plan or time<.0315 or nominal!=.0001 or a.steps!=8:raise ValueError('new extended binary only for completed100us eight-step plan')
  proof=ROOT/'results/autonomous_film_20261118_three_film_v5_long_fine_time1123/summary.json';qualification=json.loads(proof.read_text())
  if qualification['status']!='PASS' or qualification['duration_s']!=.0064:raise ValueError('separate long FREE all-pair qualification required')
  for case,digest in qualification['source_summary_hashes'].items():
   if sha(ROOT/'results'/('autonomous_film_'+case)/'summary.json')!=digest:raise ValueError('qualification evidence changed')
  archive=out/'sources/models';shutil.copytree(ROOT/'models',archive,ignore=shutil.ignore_patterns('*.so','__pycache__'));build=ROOT/'build'/('three_film_extended_'+a.tag);build.mkdir(exist_ok=False)
  configure=guarded(['cmake','-S',archive/'film_three_finger_recovery','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK),'-DREGRIP_VALUE_CLEARANCE='+('ON' if a.value_clearance else 'OFF')],out/'configure',120)
  compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
  extension=dict(value_clearance=a.value_clearance,qualification_sha256=sha(proof),configure=configure,compile=compile,sources={str(f.relative_to(out/'sources')):sha(f) for f in archive.rglob('*') if f.is_file()})
  write_json(out/'extension_build.json',extension)
  if not compile or compile['exit_code']:raise RuntimeError('extended build failed;preserved extension_build.json')
  binary=build/'libReGripThreeFilmRecovery.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('extended ABI mismatch')
  for plugin in scene.findall('RequiredPlugin'):
   if plugin.get('pluginName','').endswith('/libReGripThreeFilmRecovery.so'):plugin.set('pluginName',str(binary))
  owner.tag='ThreeFilmExtendedRecoveryODE'
 if a.restart_plan:tokens[4]=hashlib.sha256(json.dumps(dict(binary=sha(binary),parent=sha(src/'summary.json'),checkpoint=sha(checkpoint),new_target=target,nominal_dt=nominal,explicit_restart=True),sort_keys=True).encode()).hexdigest()
 if any(x!=y for i,(x,y) in enumerate(zip(original,tokens)) if i!=4):raise ValueError('physical payload or step counter changed')
 if a.restart_plan:(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
 else:shutil.copy2(checkpoint,out/'input.checkpoint')
 scene.set('time',tokens[1]);scene.set('dt',format(next_dt,'.17g'));owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',tokens[4]);owner.set('restartObservationPlan','true' if a.restart_plan else 'false');owner.set('endTime',format(target,'.17g'))
 for node in scene.iter():
  for key,text in list(node.attrib.items()):
   if key in ('filename','displacementFilename','publicMassFilename') and text.startswith(str(src)):node.set(key,str(out)+text[len(str(src)):])
 tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result=dict(status='FAIL',scope='actual persistent V5 plan continuation or explicit completed-plan extension;NOT physical recovery/grasp certification',parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),original_checkpoint_sha256=sha(checkpoint),input_checkpoint_sha256=sha(out/'input.checkpoint'),binary_sha256=sha(binary),sdk=str(SDK),scene_sha256=sha(out/'scene.scn'),start_time=time,steps=a.steps,nominal_dt_s=nominal,restored_next_dt_s=next_dt,source_used_dt_s=float(tokens[2]),source_remaining_steps=remaining,restart_plan=a.restart_plan,target_time_s=target,predicted_runtime_s=forecast,process=run,sofa_errors=errors,root_reaction_work=None,legacy_sampled_work='new private origin;prior work evidence stays in parent;NOT restored',physical_payload_and_counter_unchanged=True)
 result['source_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 result['extended_build']=extension
 result['extended_owner']=owner.tag=='ThreeFilmExtendedRecoveryODE'
 if run['exit_code']==0 and not errors:
  rows=list(csv.DictReader((out/'three.states.csv').open()));clocks=list(csv.DictReader((out/'three.recovery.clock.csv').open()));gap=min(float(r['minimum_gap']) for r in rows);momentum=max(float(r['momentum_residual']) for r in rows);result.update(status='EXPERIMENTAL' if len(rows)==a.steps and len(clocks)==a.steps and all(r['all_child_times_exact']=='true' and int(r['contexts'])==11 for r in clocks) and gap>=-1e-10 and momentum<=1e-17 else 'FAIL',actual_end_time_s=float(rows[-1]['time']),minimum_gap_mm=gap,momentum_Ns=momentum)
  if a.compare:
   parent_rows=list(csv.DictReader((src/'three.states.csv').open()));indices=[i for i,r in enumerate(parent_rows) if float(r['time'])==time]
   if len(indices)!=1 or len(parent_rows)<indices[0]+1+a.steps:raise ValueError('complete continuous reference window required')
   start=indices[0]+1;reference=parent_rows[start:start+a.steps];state_errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,reference)) for k in ('q','v')};stages=list(csv.DictReader((out/'three.free.stages.csv').open()));reference_stages=[r for r in csv.DictReader((src/'three.free.stages.csv').open()) if int(r['macro'])>a.step][:3*a.steps];reference_clocks=list(csv.DictReader((src/'three.recovery.clock.csv').open()))[start:start+a.steps];snapshots={str(a.step+i+1):sha(out/f'three.checkpoint_{a.step+i+1}.txt')==sha(src/f'three.checkpoint_{a.step+i+1}.txt') for i in range(a.steps)};field_error=0
   for f in range(3):
    actual=list(csv.DictReader((out/f'film_{f}.csv').open()));expected=list(csv.DictReader((src/f'film_{f}.csv').open()))[start:start+a.steps]
    for x,y in zip(actual,expected):
     for k in x:
      if k!='tendon_work':field_error=max(field_error,float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))))
   exact_time=all(x['time']==y['time'] for x,y in zip(rows,reference));result.update(status='PASS' if result['status']=='EXPERIMENTAL' and max(state_errors.values())<1e-12 and field_error<1e-12 and exact_time and stages==reference_stages and clocks==reference_clocks and all(snapshots.values()) else 'FAIL',reference_max_abs=state_errors,actual_field_max_abs=field_error,absolute_api_gate=1e-12,stage_rows_exact=stages==reference_stages,controller_rows_exact=clocks==reference_clocks,accumulated_time_exact=exact_time,serialized_snapshots_byte_exact=snapshots)
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes','extended_build')}))
if __name__=='__main__':main()
