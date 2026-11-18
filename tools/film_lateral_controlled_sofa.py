"""Isolated actual controlled macro-step from SAME accepted23ms checkpoint."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',required=True);p.add_argument('--parent');p.add_argument('--reuse-build');p.add_argument('--stage-labels',action='store_true');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);rm=json.loads((ref/'summary.json').read_text());parent=ROOT/'results'/('autonomous_film_'+(a.parent or '20261118_lateral_unload_boundary1458'));pm=json.loads((parent/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_lateral_resume1420';proof=json.loads((provider/'summary.json').read_text())
 if rm['status']!='PASS' or rm['macros'] not in (1,2,4,8) or pm['status']!=('PASS' if a.parent else 'FAIL') or proof['status']!='PASS':raise ValueError('qualified isolated reference and preserved old failure required')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('actual provider archive changed')
 for f,d in rm['source_hashes'].items():
  if sha(ref/'sources'/f)!=d:raise ValueError('qualified reference archive changed')
 for f,d in proof['source_hashes'].items():
  if not a.parent and f.startswith('models/') and rm['source_hashes'].get(f)!=d:raise ValueError('reference/actual base physical source differs:'+f)
 checkpoint=ref/'input.checkpoint'
 if sha(checkpoint)!=rm['checkpoint_sha256']:raise ValueError('same actual IVP changed')
 if a.parent:
  if rm.get('parent_actual_summary_sha256') not in (None,sha(parent/'summary.json')):raise ValueError('reference actual parent differs')
  source_checkpoint=parent/('three.checkpoint_'+checkpoint.read_text().split()[3]+'.txt')
  if pm['raw_hashes'].get(source_checkpoint.name)!=sha(checkpoint) or sha(source_checkpoint)!=sha(checkpoint):raise ValueError('exact hash-bound actual parent checkpoint required')
  for f,d in pm['source_hashes'].items():
   if sha(parent/'sources'/f)!=d:raise ValueError('qualified parent model changed')
   if f.startswith('models/') and not f.endswith('/EndpointControlledRows.h') and rm['source_hashes'].get(f)!=d:raise ValueError('same parent/reference model required:'+f)
 forecast=2*rm['process']['runtime_s']+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');shutil.copy2(ref/'sources/models/film_coupled_collocation/EndpointControlledRows.h',archive/'models/film_coupled_collocation/EndpointControlledRows.h')
 path=archive/'models/film_three_finger/ThreeFilmOwner.cpp';text=path.read_text()
 if 'endpointControlledRows' in text:
  known=ROOT/'results/autonomous_film_20261118_lateral_activegap_actual1480/sources/models/film_three_finger/ThreeFilmOwner.cpp'
  if sha(path)!=sha(known):raise ValueError('only qualified controlled owner source can be retained')
 else:
  lines=text.splitlines();old=next(x for x in lines if x.lstrip().startswith('auto result=[&]'));new='''  auto controlled=regrip_collocation::endpointControlledRows(system.shared.M,rayleighMass.getValue(),q,v,last,dt,[&](const auto&x,double t){return system.force(x,applied(t));},[&](const auto&x){return system.geometry(x);},[&](const auto&x){return system.clearance(x);});
   auto result=controlled.accepted.back();double gap=system.clearance(q);result.momentumResidual=0;result.velocityResidual=0;result.iterations=0;result.evaluations=0;for(const auto&micro:controlled.accepted){result.momentumResidual=std::max(result.momentumResidual,micro.momentumResidual);result.velocityResidual=std::max(result.velocityResidual,micro.velocityResidual);result.iterations+=micro.iterations;result.evaluations+=micro.evaluations;for(const auto&stage:micro.stages)gap=std::min(gap,system.clearance(stage.q));}if(gap< -1e-10||!result.q.allFinite()||!result.v.allFinite())throw std::runtime_error("unchanged controlled whole-stage gate");'''
  text=text.replace(old,new);row=next(x for x in lines if x.lstrip().startswith('for(unsigned k=0;k<3;++k){const auto&position='));changed=row.replace(':q;',':microQ;').replace(':v;',':microV;').replace('last+dt*(k==0?0:k==1?.5:1)','(k?result.stages[k-1].time:microTime)')
  text=text.replace(row,'  {Eigen::VectorXd microQ=q,microV=v;double microTime=last;for(const auto&result:controlled.accepted){\n'+changed+'\n microQ=result.q;microV=result.v;microTime=result.stages[1].time;}}')
  text='#include "../film_coupled_collocation/EndpointControlledRows.h"\n'+text;path.write_text(text)
 if a.stage_labels:
  path=archive/'models/film_three_finger/ThreeFilmOwner.cpp';text=path.read_text();changes={
   'jacobian,stage_q,stage_v\\n':'jacobian,stage_q,stage_v,local_macro,micro,stage,used_h_s,force_kind\\n',
   'double microTime=last;for(const auto&result:controlled.accepted){':'double microTime=last;unsigned microIndex=0;for(const auto&result:controlled.accepted){double used_h=controlled.durations[microIndex];',
   "quote(rowJournal,velocity);rowJournal<<'\\n';":"quote(rowJournal,velocity);rowJournal<<','<<count<<','<<microIndex<<','<<k<<','<<used_h<<','<<(k?\"collocation_stage\":\"acceleration_constraint\")<<'\\n';",
   'microTime=result.stages[1].time;}}':'microTime=result.stages[1].time;++microIndex;}}'}
  for old,new in changes.items():
   if text.count(old)!=1:raise ValueError('passive stage-label anchor differs')
   text=text.replace(old,new)
  path.write_text(text)
 path=archive/'models/film_three_finger_resume/ThreeFilmResume.cpp';text=path.read_text().replace('REGRIP_LATERAL_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1');path.write_text(text)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 if a.reuse_build:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse_build);pr=json.loads((prior/'summary.json').read_text())
  if pr['status']!='PASS' or pr['source_hashes']!=sources or pr['sdk_runner_sha256']!=sha(SDK/'bin/runSofa-26.06.00'):raise ValueError('exact ALL-source qualified binary reuse required')
  build=ROOT/pr['build_relative']
  if sha(build/'libReGripThreeFilmResume.so')!=pr['binary_sha256']:raise ValueError('reused binary changed')
  configure=dict(exit_code=0,reused_from=a.reuse_build);compile=dict(exit_code=0,reused_from=a.reuse_build)
 else:
  build=ROOT/'build'/('lateral_controlled_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 r=dict(status='FAIL',scope='ACTUAL source-bound lateral persistent contact-admissibility continuation;NOT full time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),parent_status=pm['status'],position_projection=False,tolerance_relaxed=False,root_work=None,actual_steps=rm['macros'],start_time_s=float(checkpoint.read_text().split()[1]),dt_s=float(checkpoint.read_text().split()[2]))
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK mismatch')
  tokens=checkpoint.read_text().split();time,h=float(tokens[1]),float(tokens[2]);identity=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),input=sha(checkpoint)),sort_keys=True).encode()).hexdigest();original=tokens.copy();tokens[0]='REGRIP_LATERAL_CONTROLLED_V1';tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[1:4]+tokens[5:]!=original[1:4]+original[5:]:raise ValueError('physical checkpoint changed')
  end=time
  for _ in range(rm['macros']):end+=h
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE') if scene.find('RoutedThreeFilmResumeODE') is not None else scene.find('RoutedThreeFilmContactTransferODE');owner.tag='RoutedThreeFilmResumeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',identity);owner.set('endTime',format(end,'.17g'));owner.set('reuseJournalRows','1');owner.attrib.pop('ownerCostFilename',None)
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith(('/libReGripThreeFilmResume.so','/libReGripThreeFilmTransfer.so')):node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=identity,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'))
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(rm['macros']),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and not errors:
   states=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((ref/'states.csv').open()));rows=list(csv.DictReader((out/'three.rows.csv').open()));micro=list(csv.DictReader((ref/'states.csv.micro.csv').open()));api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected)) for k in ('q','v')};stageError=0.;clocks=len(rows)==3*len(micro)
   for index,target in enumerate(micro):
    for f in range(3):
     row=rows[3*index+f];clocks=clocks and row['time']==target['time'];stageError=max(stageError,abs(float(row['force'])-np.fromstring(target['force'],sep=' ')[f]),*(float(np.max(abs(np.fromstring(row['stage_'+k],sep=' ')-np.fromstring(target[k],sep=' ')))) for k in ('q','v')))
   r.update(status='PASS' if len(states)==len(expected)==rm['macros'] and max(api.values())<=1e-12 and stageError<=1e-12 and clocks and all(x['time']==y['time'] for x,y in zip(states,expected)) else 'FAIL',reference_max_abs=api,all_micro_stage_max_abs=stageError,all_micro_clocks_exact=clocks,end_time_s=float(states[-1]['time']),minimum_gap_mm=min(float(x['minimum_gap']) for x in states),momentum_Ns=max(float(x['momentum_residual']) for x in states))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
