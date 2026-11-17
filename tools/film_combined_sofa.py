"""Actual coupled PRE-impact C2 state:reintegrated birth + Lobatto remainder."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);p.add_argument('--steps',type=int,choices=(4,8,16,32,64,128,256,512),default=4);p.add_argument('--reuse');p.add_argument('--profile');p.add_argument('--pilot-profile',help='explicit changed-owner-budget pilot from measured identical kernel headers');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rs=json.loads((ref/'summary.json').read_text())
 if rs['status']!='PASS' or not (ref/'states.csv').is_file():raise ValueError('qualified independent COMBINED pre-state reference required')
 uniform='completed_rows' in rs
 if uniform:
  parent=ROOT/'results'/('autonomous_film_'+rs['profile']);qualified=json.loads((parent/'summary.json').read_text());rows=list(csv.DictReader((ref/'states.csv').open()))
  if qualified['status']!='PASS' or not qualified.get('sparse_stage') or rs['completed_rows']!=rs['steps'] or len(rows)!=rs['steps'] or rs['input_sha256']!=qualified['input_sha256'] or a.steps!=rs['steps']:raise ValueError('complete same-input same-grid independent uniform reference required')
  rs={**rs,'actual_pre_source':qualified['actual_pre_source'],'sparse_stage':True}
 source=ROOT/'results'/('autonomous_film_'+rs['actual_pre_source']);meta=json.loads((source/'identity.json').read_text());ss=json.loads((source/'summary.json').read_text());duration=rs['duration']
 if ss['status']!='PASS' or duration>(.001 if uniform else .000125) or duration/a.steps>1e-5 or meta.get('initial_state_kind')!='pre-impact accepted macro state':raise ValueError('qualified actual pre-impact source and profiled reference window required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 for directory in ('film_coupled_contact','film_coupled_collocation','film_combined_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
  target=archive/'models'/directory;target.mkdir(parents=True)
  for f in (ROOT/'models'/directory).iterdir():
   if f.is_file() and (f.suffix in ('.h','.cpp','.in') or f.name=='CMakeLists.txt'):shutil.copy2(f,target/f.name)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 for name,digest in rs['sources'].items():
  if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('qualified combined kernel changed:'+name)
 build=ROOT/'build'/('combined_'+a.tag);stages={}
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);pm=json.loads((prior/'identity.json').read_text());ps=json.loads((prior/'summary.json').read_text());build=ROOT/'build'/('combined_'+a.reuse)
  if ps['status']!='PASS' or pm['sources']!=sources or sha(build/'libReGripCombinedContact.so')!=pm['binary_sha256']:raise ValueError('reused combined binary/source mismatch')
  stages['build']=dict(exit_code=0,reused=a.reuse)
 else:
  build.mkdir(exist_ok=False);stages['configure']=guarded(['cmake','-S',archive/'models/film_combined_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
 identity={**meta,'sources':sources,'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_case':rs['actual_pre_source'],'reference':a.reference,'duration':duration,'steps':a.steps,'start_time':meta['start_time'],'actual_solver':'CoupledEventLobattoODE isolated coupled midpoint birth + shared impact + Lobatto remainder','combined_contact':True,'persistent_radau':True,'persistent_lobatto':True,'reintegrated_birth':True,'source_event_sha256':sha(source/'coupled.event_states.csv'),'reference_input_sha256':rs['input_sha256'],'earliest_endpoint_family_certified':False,'unused_baseline_remainder':'evaluated and counted,never applied;new collocation overwrites state/forces/projection','scope':'actual isolated PRE-impact combined event/persistent coupon;NOT full C2/release/global CCD/grasp'}
 result=dict(status='FAIL',stages=stages,scope=identity['scope'])
 identity['sparse_stage']=rs.get('sparse_stage',False)
 if stages['build']['exit_code']==0:
  binary=build/'libReGripCombinedContact.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('Installed SDK ABI mismatch')
  if a.steps>4:
   profile=a.profile or a.pilot_profile
   if not profile or (a.profile and a.pilot_profile):raise ValueError('exactly one measured same-binary OR explicit changed-budget pilot profile required')
   pm=json.loads((ROOT/'results'/('autonomous_film_'+profile)/'identity.json').read_text());ps=json.loads((ROOT/'results'/('autonomous_film_'+profile)/'summary.json').read_text());estimate=2*ps['process']['runtime_s']*a.steps/pm['steps'];identity.update(predicted_runtime_s=estimate,profile_case=profile,profile_kind='new binary pilot,same kernel headers,changed owner duration guard' if a.pilot_profile else 'same binary')
   if ps['status']!='PASS' or pm['source_case']!=identity['source_case'] or pm.get('sparse_stage',False)!=identity['sparse_stage']:raise ValueError('combined physical/backend profile differs')
   if a.profile and pm['binary_sha256']!=identity['binary_sha256']:raise ValueError('same-binary runtime profile differs')
   if a.pilot_profile:
    if a.steps>(128 if uniform else 16) or a.reuse:raise ValueError('changed-budget first pilot bounded by measured kernel profile;subsequent runs require same binary')
    for name,digest in pm['sources'].items():
     if name.endswith('.h') and sources.get(name)!=digest:raise ValueError('pilot profiled kernel differs:'+name)
   if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='measured runtime policy,NOT OS exhaustion',predicted_runtime_s=estimate));return
  tree=ET.parse(source/'scene.scn');scene=tree.getroot();scene.set('dt',format(duration/a.steps,'.17g'))
  for plugin in scene.findall('RequiredPlugin'):
   if 'libReGripCoupledReintegrated.so' in plugin.get('pluginName',''):plugin.set('pluginName',str(binary))
  owner=scene.find('IsolatedReintegratedSphereODE')
  if owner is None:raise ValueError('explicit actual pre-state reintegrated source scene required')
  owner.tag='CoupledEventLobattoODE';owner.attrib.pop('reintegratedEvent',None);owner.set('filename',str(out/'coupled'));owner.set('startTime',str(meta['start_time']));owner.set('maxSteps',str(a.steps));owner.set('maximumDuration',format(duration,'.17g'));owner.set('sparseStage',str(int(identity['sparse_stage'])));field=scene.find('.//FilmRailTendon');field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'));tree.write(out/'scene.scn');write_json(out/'identity.json',identity)
  process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',120 if a.steps==4 else 480);result['process']=process
  states=list(csv.DictReader((out/'coupled.states.csv').open())) if (out/'coupled.states.csv').exists() else [];events=list(csv.DictReader((out/'coupled.events.csv').open())) if (out/'coupled.events.csv').exists() else [];times={s['time'] for s in events}
  finite=len(states)==a.steps and all(math.isfinite(float(s[k])) for s in states for k in ('time','minimum_gap','U_shell','U_attachment','K_film','K_linear'))
  policies=list(csv.DictReader((out/'coupled.policy.csv').open())) if (out/'coupled.policy.csv').exists() else [];policy_ok=len(policies)==1 and policies[0]['component']=='CoupledEventLobattoODE' and int(policies[0]['sparse_stage'])==int(identity['sparse_stage']) and float(policies[0]['start_time'])==identity['start_time'] and float(policies[0]['maximum_duration'])==duration
  error_count=sum((out/'process'/name).read_text(errors='replace').count('[ERROR]') for name in ('stdout.log','stderr.log'));result.update(runtime_policy_verified=policy_ok,runtime_policy=policies,sofa_error_count=error_count)
  if process['exit_code']==0 and finite:result.update(status='PASS' if policy_ok and not error_count and len(times)==1 and min(float(s['minimum_gap']) for s in states)>=-1e-10 and abs(float(states[-1]['time'])-meta['start_time']-duration)<1e-12 else 'FAIL',minimum_gap=min(float(s['minimum_gap']) for s in states),impact_times=sorted(times))
 write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','impact_times','minimum_gap','process')}))
if __name__=='__main__':main()
