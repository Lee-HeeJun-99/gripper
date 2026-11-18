"""Reuse original aligned recovery scheme on actual routed31.6ms IVP.
Only copied dt/provenance change for a DECLARED numerical experiment;
q/v/quaternion/mass/root/contact inventory/counter/physical time preserved.
"""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(8,16,32),required=True);p.add_argument('--reuse');a=p.parse_args();provider=ROOT/'results/autonomous_film_20261118_routed_free_window1392';pm=json.loads((provider/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_routed_recovery_window1393';m=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_158.txt'
 if pm['status']!='PASS' or m['status']!='PASS' or m['binary_sha256']!=pm['binary_sha256'] or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('completed actual routed31.6ms IVP required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified compiled source changed')
 nominal=.0008/a.steps;original=checkpoint.read_text().split();time=float(original[1]);target=time+.0008;forecast=2*m['process']['runtime_s']*a.steps/m['actual_steps']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_routed_recovery',archive/'models/film_routed_recovery')
 cpp=archive/'models/film_three_finger_recovery/ThreeFilmRecovery.cpp';text=cpp.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda x:'Routed'+x.group(),text);text='#include "../film_routed_contact/SeparatedPath.h"\n'+text
 old='if(regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius))'
 if text.count(old)!=1:raise ValueError('recovery numerical-path guard differs')
 text=text.replace(old,'if(!regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius).clear&&regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius))');cpp.write_text(text)
 reference=archive/'diagnostics/film_three_finger/RoutedAlignedReference.cpp';reference.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/FreeRecovery.cpp').read_text();text='#include "../../models/film_routed_contact/SeparatedPath.h"\n'+text.replace('"REGRIP_FREE_V3"','"REGRIP_ROUTED_FREE_V3"')
 anchor=' if(magic=="REGRIP_PERSISTENT_OBSERVATION_V5"){'
 if text.count(anchor)!=1 or text.count(old)!=1:raise ValueError('existing independent reference loader/CCD changed')
 loader=''' if(magic=="REGRIP_ROUTED_FREE_V3"){
 unsigned count;in>>label>>count;if(label!="RELEASED_EDGES"||count!=3)throw std::runtime_error("routed released owner audit required");
 for(unsigned f=0;f<3;++f){unsigned owner,triangle,a,b;double born;in>>owner>>triangle>>a>>b>>born;if(owner!=f||triangle>=s.shared.films[f].triangles.size()||a==b||born>time)throw std::runtime_error("released owner invalid");for(unsigned node:{a,b}){const auto&tri=s.shared.films[f].triangles[triangle];if(std::find(tri.begin(),tri.end(),node)==tri.end())throw std::runtime_error("released edge topology invalid");}}
 double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time)throw std::runtime_error("routed actual clock invalid");std::string extra;if(in>>extra)throw std::runtime_error("routed actual trailing state");}
'''
 text=text.replace(anchor,loader+anchor).replace(old,'if(!regrip_routed_contact::separatedNumericalPath(path.path,path.triangles,{0,0,0},s.layout.bufferRadius).clear&&regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius))');reference.write_text(text);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('routed_aligned_'+a.tag);binary=build/'libReGripRoutedAlignedRecovery.so';refbin=out/'reference'
 if a.reuse:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((previous/'summary.json').read_text())
  if proof['status']!='PASS' or proof['source_hashes']!=sources or sha(previous/'reference')!=proof['reference_binary_sha256']:raise ValueError('exact compiled aligned model/reference required')
  build=ROOT/proof['build_relative'];binary=build/'libReGripRoutedAlignedRecovery.so'
  if sha(binary)!=proof['binary_sha256']:raise ValueError('compiled binary changed')
  shutil.copy2(previous/'reference',refbin);configure=compile=refcompile=dict(exit_code=0,reused_from=a.reuse)
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_routed_recovery','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;refcompile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',reference,'-o',refbin],out/'reference_compile',120) if compile and compile['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual routed same-IVP aligned800us FREE numerical study;NOT whole trajectory/recovery/energy/time/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,source_checkpoint_sha256=sha(checkpoint),parent_summary_sha256=sha(parent/'summary.json'),steps=a.steps,nominal_dt_s=nominal,start_time_s=time,expected_end_time_s=target,predicted_child_runtime_s=forecast,configure=configure,compile=compile,reference_compile=refcompile,build_relative=str(build.relative_to(ROOT)),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),numerical_replan='copied dt/provenance ONLY;all physical state/control/counter/time tokens unchanged;actual step increment natural',V6_resume='NOT QUALIFIED',root_reaction_work=None,legacy_sampled_work='EXCLUDED')
 if refcompile and refcompile['exit_code']==0:
  deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('aligned SDK mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),input=sha(checkpoint),steps=a.steps),sort_keys=True).encode()).hexdigest();tokens=original.copy();tokens[2]=format(nominal,'.17g');tokens[4]=token
  if any(x!=y for i,(x,y) in enumerate(zip(tokens,original)) if i not in (2,4)):raise ValueError('physical IVP changed')
  (out/'input.checkpoint').write_text(' '.join(tokens)+'\n');r.update(binary_sha256=sha(binary),reference_binary_sha256=sha(refbin),identity=token,input_checkpoint_sha256=sha(out/'input.checkpoint'))
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured per-step policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  ref=guarded([refbin,out/'input.checkpoint',str(a.steps),out/'recovery'],out/'reference_process',480);r['reference_process']=ref
  if ref['exit_code']==0:
   tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));scene.set('dt',format(nominal,'.17g'));owner=scene.find('RoutedThreeFilmFreeODE');owner.tag='RoutedThreeFilmAlignedStudyODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime',format(target,'.17g'));owner.set('nominalStep',format(nominal,'.17g'));owner.set('observationSteps',str(a.steps))
   for node in scene.iter():
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmRelease.so'):node.set('pluginName',str(binary))
    for k,v in list(node.attrib.items()):
     if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
   tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors,scene_sha256=sha(out/'scene.scn'))
   if run['exit_code']==0 and not errors:
    actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((out/'recovery.states.csv').open()));clock=len(actual)==len(expected)==a.steps and all(x['time']==y['time'] for x,y in zip(actual,expected)) and float(actual[-1]['time'])==target;delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};schedules=list(csv.DictReader((out/'three.recovery.clock.csv').open()));contexts=len(schedules)==a.steps and all(x['contexts']=='11' and x['all_child_times_exact']=='true' for x in schedules);r.update(status='PASS' if clock and contexts and max(delta.values())<1e-12 else 'FAIL',reference_max_abs=delta,accumulated_common_clock_exact=clock,all_contexts_exact=contexts,reference_metrics=next(csv.DictReader((out/'recovery.metrics.csv').open())))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','configure','compile','reference_compile','process','reference_process')}))
if __name__=='__main__':main()
