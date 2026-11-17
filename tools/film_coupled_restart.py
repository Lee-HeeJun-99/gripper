"""Explicit saved-event continuation;first qualify exact original remainder."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True);p.add_argument('--reuse');p.add_argument('--duration',type=float);p.add_argument('--steps',type=int,default=1);p.add_argument('--profile');p.add_argument('--pre-step',action='store_true');p.add_argument('--adaptive-profile');p.add_argument('--snapshot',help='explicit archived model sources for exact old-version replay');p.add_argument('--reintegrated-reference',help='PASS independent entering-bracket kernel before experimental actual owner');p.add_argument('--dense-event-control',action='store_true');a=p.parse_args()
 if a.dense_event_control and not a.reintegrated_reference:raise ValueError('dense control is a same-binary reintegrated-owner comparison only')
 if a.reintegrated_reference and (a.adaptive_profile or a.snapshot):raise ValueError('isolated reintegrated prototype is separate from old snapshot/adaptive owner')
 if not 1<=a.steps<=1600:raise ValueError('step budget1600')
 source=ROOT/'results'/('autonomous_film_'+a.source);meta=json.loads((source/'identity.json').read_text());prior=json.loads((source/'summary.json').read_text())
 if prior['status']!='PASS' or meta.get('adaptive') or meta.get('frozen_grid'):raise ValueError('complete uniform actual source required')
 snapshots=list(csv.DictReader((source/'coupled.event_states.csv').open()));event=min((s for s in snapshots if s['stage']=='post'),key=lambda s:float(s['time']));start=float(event['time']);states=list(csv.DictReader((source/'coupled.states.csv').open()));original=next(s for s in states if float(s['time'])>start)
 if a.pre_step:
  original_index=states.index(original)
  if original_index==0:raise ValueError('original pre-step accepted state not stored')
  event=states[original_index-1];start=float(event['time'])
 duration=a.duration if a.duration is not None else meta['duration']/meta['steps'] if a.pre_step else float(original['time'])-start
 if not 0<duration<=.025:raise ValueError('short isolated post-impact window<=25ms')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 directories=['film_coupled_restart','film_coupled_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact']
 if a.adaptive_profile:directories+=['film_coupled_adaptive','film_value_energy']
 if a.reintegrated_reference:directories+=['film_coupled_reintegrated']
 model_source=ROOT/'results'/('autonomous_film_'+a.snapshot)/'sources/models' if a.snapshot else ROOT/'models'
 for directory in directories:
  target=archive/'models'/directory;target.mkdir(parents=True)
  for f in (model_source/directory).iterdir():
   if f.is_file() and (f.suffix in ('.h','.cpp','.in') or f.name=='CMakeLists.txt'):shutil.copy2(f,target/f.name)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for name,digest in meta['sources'].items():
  physical=name.startswith(('models/film_shell/','models/film_rail_tendon/','models/film_sphere_contact/')) or name=='models/film_native_contact/CoupledPlaneStep.h'
  if name.endswith('.h') and name in sources and sources[name]!=digest and (not a.reintegrated_reference or physical):raise ValueError('restart physical source differs:'+name)
 if a.reintegrated_reference:
  referenceDir=ROOT/'results'/('autonomous_film_'+a.reintegrated_reference);rm=json.loads((referenceDir/'identity.json').read_text());rs=json.loads((referenceDir/'summary.json').read_text())
  if not a.pre_step or rs['status']!='PASS' or duration/a.steps>.001:raise ValueError('qualified independent isolated bracket and<=1ms steps required')
  for name,digest in rm['sources'].items():
   if name.endswith('.h') and name!='models/film_coupled_contact/CoupledOwnerClass.h' and sources.get(name)!=digest:raise ValueError('independent reintegrated kernel header drift:'+name)
 build=ROOT/'build'/('coupled_restart_'+a.tag);stages={};library='libReGripCoupledReintegrated.so' if a.reintegrated_reference else 'libReGripCoupledAdaptive.so' if a.adaptive_profile else 'libReGripCoupledRestart.so';module='film_coupled_reintegrated' if a.reintegrated_reference else 'film_coupled_adaptive' if a.adaptive_profile else 'film_coupled_restart'
 if a.reuse:
  reused=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((reused/'identity.json').read_text())
  if old['sources']!=sources:raise ValueError('restart compiled source drift')
  build=ROOT/'build'/('coupled_restart_'+a.reuse);binary=build/library
  if sha(binary)!=old['binary_sha256']:raise ValueError('restart binary drift')
  stages['build']=dict(exit_code=0,reused=a.reuse)
 else:
  build.mkdir(exist_ok=False);stages['configure']=guarded(['cmake','-S',archive/'models'/module,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
 identity={**{k:v for k,v in meta.items() if k not in ('generated_source_hashes','predicted_runtime_s','profile')},'sources':sources,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'actual_solver':'CoupledRestartODE explicit post-impact initial-value experiment','steps':a.steps,'duration':duration,'start_time':start,'source_case':a.source,'initial_body_center':event['body_center'],'initial_body_velocity':event['body_velocity']+' '+event['body_omega'],'initial_body_quaternion':event['body_quaternion'],'state_file':'coupled.states.csv','initial_displacement':event['local_displacement'],'initial_velocity':event['local_velocity'],'source_event_sha256':sha(source/'coupled.event_states.csv')}
 result=dict(status='FAIL',stages=stages,scope='isolated actual saved-event continuation;NOT original full trajectory/time/energy certification')
 identity.update(initial_state_kind='pre-impact accepted macro state' if a.pre_step else 'post-impact event state',source_state_sha256=sha(source/'coupled.states.csv'))
 if a.reintegrated_reference:identity.update(reintegrated_reference=a.reintegrated_reference,actual_solver='IsolatedReintegratedSphereODE explicit C2 midpoint solve-to-event bracket prototype',strict_newton=True,force_residual=1e-17,gap_solve=1e-14,earliest_endpoint_family_certified=False,scope='actual ISOLATED entering-bracket prototype;NOT global earliest CCD/full cycle/grasp')
 if a.reintegrated_reference:identity.update(reintegrated_birth=not a.dense_event_control,event_state_policy='full-step dense interpolation' if a.dense_event_control else 'coupled midpoint reintegration to event')
 if stages['build']['exit_code']==0:
  binary=build/library;identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('SDK identity mismatch')
  limit=120
  if a.adaptive_profile:
   profileDir=ROOT/'results'/('autonomous_film_'+a.adaptive_profile);pm=json.loads((profileDir/'identity.json').read_text());pr=json.loads((profileDir/'summary.json').read_text());referenceInitial=json.loads((ROOT/'results'/('autonomous_film_'+pm['source_case'])/'identity.json').read_text())
   if not a.pre_step or a.steps!=pm['macros'] or duration!=pm['duration'] or duration/a.steps>.001 or pr['status']!='PASS':raise ValueError('complete matching adaptive initial-value profile required')
   for key in ('start_time','initial_displacement','initial_velocity','initial_body_center','initial_body_velocity','initial_body_quaternion','source_event_sha256','midpoint_contact'):
    if identity.get(key)!=referenceInitial.get(key):raise ValueError('adaptive profile initial state differs:'+key)
   for key,digest in pm['sources'].items():
    if key.endswith('.h') and sources.get(key)!=digest:raise ValueError('adaptive profiled header differs:'+key)
   estimate=1.6*pr['run']['runtime_s'];identity.update(adaptive=True,adaptive_profile=a.adaptive_profile,actual_solver='AdaptiveCoupledSphereODE explicit saved-state C2 continuation',state_file='coupled.macro_states.csv',predicted_runtime_s=estimate,controller_tolerance=1e-4)
   if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='profile policy;not OS exhaustion',predicted_runtime_s=estimate));return
   limit=480
  if a.steps>64 or a.profile:
   if not a.profile:raise ValueError('measured same-binary continuation profile required')
   priorDir=ROOT/'results'/('autonomous_film_'+a.profile);pm=json.loads((priorDir/'identity.json').read_text());pr=json.loads((priorDir/'summary.json').read_text())
   if pr['status']!='PASS' or pm['binary_sha256']!=identity['binary_sha256'] or pm['source_event_sha256']!=identity['source_event_sha256']:raise ValueError('invalid continuation profile')
   estimate=2*pr['process']['runtime_s']*a.steps/pm['steps'];identity['predicted_runtime_s']=estimate
   if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='profile policy;not OS exhaustion',predicted_runtime_s=estimate));return
   limit=480
  tree=ET.parse(source/'scene.scn');scene=tree.getroot();scene.set('dt',format(duration/a.steps,'.17g'))
  for plugin in scene.findall('RequiredPlugin'):
   if any(name in plugin.get('pluginName','') for name in ('libReGripCoupledSphere.so','libReGripCoupledRestart.so')):plugin.set('pluginName',str(binary))
  ode=scene.find('CoupledSphereODE')
  if ode is None:ode=scene.find('CoupledRestartODE')
  if ode is None:raise ValueError('explicit supported sole source owner required')
  ode.tag='IsolatedReintegratedSphereODE' if a.reintegrated_reference else 'AdaptiveCoupledSphereODE' if a.adaptive_profile else 'CoupledRestartODE';ode.set('startTime',format(start,'.17g'));ode.set('maxSteps',str(1600 if a.adaptive_profile else a.steps));ode.set('filename',str(out/'coupled'))
  if a.reintegrated_reference:ode.set('strictNewton','1');ode.set('midpointContact','1');ode.set('reintegratedEvent',str(int(not a.dense_event_control)))
  if a.adaptive_profile:ode.set('maxMacroSteps',str(a.steps));ode.set('adaptiveTolerance','0.0001');ode.set('reuseCoarseTrial','1');ode.set('valueEnergyEstimator','0')
  dofs=scene.find("MechanicalObject[@name='dofs']");dofs.set('position',event['local_displacement']);dofs.set('velocity',event['local_velocity'])
  q=np.fromstring(event['body_quaternion'],sep=' ');body=scene.find("Node[@name='free_object']/MechanicalObject");body.set('position',event['body_center']+' '+' '.join(map(str,q)));body.set('velocity',event['body_velocity']+' '+event['body_omega'])
  field=scene.find('.//FilmRailTendon');field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'));tree.write(out/'scene.scn')
  write_json(out/'identity.json',identity);process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',limit);result['process']=process
  path=out/identity['state_file'];rows=list(csv.DictReader(path.open())) if path.exists() else []
  finite=len(rows)==a.steps and all(math.isfinite(float(s[k])) for s in rows for k in ('time','minimum_gap','U_shell','U_attachment','K_film','K_linear'))
  if process['exit_code']==0 and finite and abs(float(rows[-1]['time'])-(start+duration))<1e-12:
   result.update(status='PASS' if min(float(s['minimum_gap']) for s in rows)>=-1e-10 else 'FAIL',minimum_gap=min(float(s['minimum_gap']) for s in rows))
   if a.duration is None and a.steps==1:
    fields=('local_displacement','local_velocity','body_center','body_velocity','body_quaternion','body_omega','U_shell','U_attachment','K_film','K_linear');errors={}
    for key in fields:
     x=np.fromstring(rows[-1][key],sep=' ');y=np.fromstring(original[key],sep=' ');errors[key]=float(np.max(abs(x-y)))
    result.update(remainder_reproduction=dict(status='PASS' if all(v==0 for v in errors.values()) else 'FAIL',absolute_errors=errors,original_state_time=float(original['time'])))
  else:result['observed_rows']=len(rows)
  identity['generated_source_hashes']={str(f.relative_to(build)):sha(f) for f in build.rglob('*') if f.is_file() and ('value_models' in f.parts or f.name=='generated_value_manifest.tsv')}
  identity['control']=field.attrib
 write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
