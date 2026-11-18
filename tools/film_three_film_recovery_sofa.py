"""Separately bounded actual30..30.8ms FREE recovery and exact-clock reference."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(8,16,32),required=True);p.add_argument('--reuse');p.add_argument('--align-end',action='store_true');p.add_argument('--persistent',action='store_true');a=p.parse_args();parent=ROOT/'results/autonomous_film_20261118_three_film_unload_end1083';meta=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_200.txt'
 if a.persistent and not a.align_end:raise ValueError('persistent observation requires aligned clock scheme')
 if meta['status']!='EXPERIMENTAL' or meta['process']['exit_code'] or sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('complete actual30ms state required')
 qualification=ROOT/'results/autonomous_film_20261118_three_film_recovery_time1100/summary.json'
 if json.loads(qualification.read_text())['status']!='PASS':raise ValueError('independent base-to-quarter FREE subset required')
 forecast=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 if forecast>480:raise ValueError('measured recovery forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FreeRecovery.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FreeRecovery.cpp',cpp);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('three_film_recovery_'+a.tag);reference=out/'reference';configure=compile=None
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((previous/'summary.json').read_text())
  if proof['status']!='PASS' or proof['sources']!=sources or proof.get('aligned_observation',False)!=a.align_end or proof.get('persistent_observation',False)!=a.persistent or sha(previous/'reference')!=proof['reference_binary_sha256']:raise ValueError('unchanged qualified recovery DLL/reference source/clock scheme required')
  binary=ROOT/proof['build_relative']/'libReGripThreeFilmRecovery.so'
  if sha(binary)!=proof['binary_sha256']:raise ValueError('qualified recovery DLL changed')
  shutil.copy2(previous/'reference',reference);configure={'exit_code':0,'reused_from':a.reuse};compile=configure;refcompile=configure;build=binary.parent
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_recovery','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;binary=build/'libReGripThreeFilmRecovery.so';refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',reference],out/'reference_compile',120) if compile and compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual separated30..30.8ms recovery and exact clock-scheme reference;NOT complete recovery/full contact-time/grasp certification',aligned_observation=a.align_end,observation_checkpoint_resume='NOT QUALIFIED:new observation V4' if a.align_end else 'FREE V3,no new fractional-dt policy',steps=a.steps,nominal_dt_s=.0008/a.steps,predicted_runtime_s=forecast,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,sdk=str(SDK),parent_summary_sha256=sha(parent/'summary.json'),original_checkpoint_sha256=sha(checkpoint),independent_subset_sha256=sha(qualification),configure=configure,compile=compile,reference_compile=refcompile,build_relative=str(build.relative_to(ROOT)),numerical_dt_contrast='only saved/public dt and provenance token change;physical q/v/quaternion/mass/root/control/counter unchanged',root_reaction_work=None,legacy_sampled_work='new origin;NOT restored/not used')
 result['persistent_observation']=a.persistent
 if a.persistent:result['observation_checkpoint_resume']='V5 implementation;actual resume qualification separate'
 write_json(out/'summary.json',result)
 if refcompile and refcompile['exit_code']==0:
  deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in s and '=> /' in s and str(SDK) not in s for s in deps.splitlines()):raise ValueError('recovery SDK ABI mismatch')
  original=checkpoint.read_text().split();tokens=original.copy();tokens[2]=format(.0008/a.steps,'.17g');token=hashlib.sha256(json.dumps(dict(binary=sha(binary),source=sources,checkpoint=sha(checkpoint),dt=tokens[2],aligned=a.align_end,persistent=a.persistent,steps=a.steps,target=float(tokens[1])+.0008),sort_keys=True).encode()).hexdigest();tokens[4]=token
  if any(x!=y for i,(x,y) in enumerate(zip(tokens,original)) if i not in (2,4)):raise ValueError('physical initial state changed')
  (out/'input.checkpoint').write_text(' '.join(tokens)+'\n');ref=guarded([reference,out/'input.checkpoint',str(a.steps),out/'recovery']+([] if a.align_end else ['accumulated']),out/'reference_run',480);result.update(reference_run=ref,reference_binary_sha256=sha(reference),binary_sha256=sha(binary),generated_checkpoint_sha256=sha(out/'input.checkpoint'),identity=token)
  if ref['exit_code']==0:
   tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',tokens[1]);scene.set('dt',tokens[2]);owner=scene.find('ThreeFilmFreeODE');owner.tag='ThreeFilmAlignedRecoveryODE' if a.align_end else 'ThreeFilmRecoveryODE';owner.set('identity',token);owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(float(tokens[1])+.0008,'.17g'))
   if a.align_end:owner.set('nominalStep',tokens[2]);owner.set('observationSteps',str(a.steps))
   if a.persistent:owner.tag='ThreeFilmPersistentRecoveryODE'
   for node in scene.iter():
    for key,value in list(node.attrib.items()):
     if key in ('filename','displacementFilename','publicMassFilename') and value.startswith(str(parent)):node.set(key,str(out)+value[len(str(parent)):])
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmRelease.so'):node.set('pluginName',str(binary))
   tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/name).read_text(errors='replace').count('[ERROR]') for name in ('stdout.log','stderr.log'));result.update(process=run,sofa_errors=errors,scene_sha256=sha(out/'scene.scn'))
   if run['exit_code']==0 and not errors:
    actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((out/'recovery.states.csv').open()));metrics=next(csv.DictReader((out/'recovery.metrics.csv').open()))
    if len(actual)!=a.steps or len(expected)!=a.steps:raise ValueError('complete actual/reference recovery states required')
    state_errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};clock_exact=all(x['time']==y['time'] for x,y in zip(actual,expected));fields=[list(csv.DictReader((out/f'film_{f}.csv').open()))[-1] for f in range(3)];field_error=max(abs(sum(float(f['U_shell']) for f in fields)-float(metrics['U_skin'])-float(metrics['U_rails'])),abs(sum(float(f['U_attachment']) for f in fields)-float(metrics['U_attachment'])),abs(sum(float(f['K']) for f in fields)-float(metrics['K_film'])));gap=min(float(r['minimum_gap']) for r in actual);momentum=max(float(r['momentum_residual']) for r in actual)
    target=float(tokens[1])+.0008;plan_ok=True
    if a.align_end:
     clock_rows=list(csv.DictReader((out/'three.recovery.clock.csv').open()));plan_ok=len(clock_rows)==a.steps and all(int(r['contexts'])==11 and r['all_child_times_exact']=='true' for r in clock_rows) and float(actual[-1]['time'])==target and clock_rows[-1]['target_reached']=='1';result.update(public_next_dt_schedule_verified=plan_ok,exact_common_target_time=float(actual[-1]['time'])==target)
    result.update(status='PASS' if max(state_errors.values())<1e-12 and clock_exact and plan_ok and field_error<1e-12 and gap>=-1e-10 and momentum<=1e-17 else 'FAIL',reference_max_abs=state_errors,reference_accumulated_clock_exact=clock_exact,actual_field_energy_error_Nmm=field_error,minimum_gap_mm=gap,momentum_Ns=momentum,actual_end_time_s=float(actual[-1]['time']),common_nominal_target_time_s=target,end_time_minus_common_target_s=float(actual[-1]['time'])-target,metrics=metrics,absolute_api_gate=1e-12)
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','configure','compile','reference_compile','process','reference_run','raw_hashes')}))
if __name__=='__main__':main()
