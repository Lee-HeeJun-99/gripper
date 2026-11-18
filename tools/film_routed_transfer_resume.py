"""Explicit physical-state handoff after qualified routed birth/impact.
Reuse old persistent DLL ONLY after actual compiled dependency parity proof.
"""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,default=122);p.add_argument('--steps',type=int,choices=(2,4,8),default=8);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_routed_resume1278';proof=json.loads((provider/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt'
 if m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors'] or proof['status']!='PASS' or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('qualified actual transfer checkpoint required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual event evidence changed')
 for path,meta in ((src,m),(provider,proof)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('source archive changed')
 build=ROOT/proof['build_relative'];binary=build/'libReGripThreeFilmResume.so';dependency_files=list(build.rglob('*.o.d'));closure={};dependency_proof={}
 if sha(binary)!=proof['binary_sha256'] or len(dependency_files)!=2:raise ValueError('exact qualified generic executable/dependency records required')
 for dep in dependency_files:
  dependency_proof[str(dep.relative_to(ROOT))]=sha(dep)
  for token in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   path=Path(token).resolve()
   if path.is_relative_to(provider/'sources'):
    key=str(path.relative_to(provider/'sources'))
    if proof['source_hashes'].get(key)!=m['source_hashes'].get(key) or sha(path)!=proof['source_hashes'][key]:raise ValueError('compiled generic physical dependency differs:'+key)
    closure[key]=sha(path)
 if 'models/film_three_finger/SharedFilmSystem.h' not in closure or 'models/film_three_finger_resume/ThreeFilmResume.cpp' not in closure or 'models/film_routed_tendon/Field.generated.cpp' not in closure:raise ValueError('incomplete compiled dependency proof')
 if sha(src/'scene.scn')!=m['scene_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=proof['sdk_runner_sha256'] or m['sdk_runner_sha256']!=proof['sdk_runner_sha256']:raise ValueError('actual Scene/SDK changed')
 tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);end=time
 if tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1' or tokens[4]!=m['identity'] or dt!=.0002 or int(tokens[3])!=a.checkpoint_step:raise ValueError('source physical schema/identity differs')
 for i in range(a.steps):end+=dt
 if not time<end<=.03:raise ValueError('bounded unchanged C2 interval')
 profile=ROOT/'results/autonomous_film_20261118_routed_unload_begin1307';cost=json.loads((profile/'summary.json').read_text());forecast=2*cost['process']['runtime_s']*a.steps/cost['actual_steps']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');old=tokens.copy();token=hashlib.sha256(json.dumps(dict(source_checkpoint=sha(checkpoint),binary=sha(binary),compiled_dependency_closure=closure),sort_keys=True).encode()).hexdigest();tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
 if tokens[:4]+tokens[5:]!=old[:4]+old[5:]:raise ValueError('physical checkpoint payload changed')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmContactTransferODE');owner.tag='RoutedThreeFilmResumeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime',format(end,'.17g'));owner.set('reuseJournalRows','1');owner.attrib.pop('ownerCostFilename',None)
 for node in scene.iter():
  if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmTransfer.so'):node.set('pluginName',str(binary))
  for k,v in list(node.attrib.items()):
   if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
 tree.write(out/'scene.scn');r=dict(status='BLOCKED',scope='actual explicit same-physics one-step post-event state handoff;NOT full Unload/energy/time/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),source_checkpoint_sha256=sha(checkpoint),provider_summary_sha256=sha(provider/'summary.json'),physical_checkpoint_payload_exact=True,compiled_dependency_closure=closure,dependency_files=dependency_proof,binary_sha256=sha(binary),sdk=str(SDK),sdk_runner_sha256=proof['sdk_runner_sha256'],identity=token,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),start_time_s=time,dt_s=dt,actual_steps=a.steps,predicted_child_runtime_s=forecast,cost_profile_summary_sha256=sha(profile/'summary.json'),legacy_sampled_work='NOT restored;not a physical work origin',root_reaction_work=None)
 if forecast>480:r['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',r);return
 run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(status='FAIL',process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')))
 if run['exit_code']==0 and not r['sofa_errors']:
  rows=list(csv.DictReader((out/'three.states.csv').open()));clock=time;exact=True
  for row in rows:clock+=dt;exact=exact and float(row['time'])==clock
  r.update(status='EXPERIMENTAL' if len(rows)==a.steps and exact else 'FAIL',accumulated_clock_exact=exact,end_time_s=clock,minimum_whole_stage_gap_mm=min(float(z['minimum_gap']) for z in rows),momentum_residual_Ns=max(float(z['momentum_residual']) for z in rows),normal_velocity_residual_mm_s=max(float(z['normal_velocity_residual']) for z in rows))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('compiled_dependency_closure','dependency_files','process','raw_hashes')}))
if __name__=='__main__':main()
