"""Actual C2-driven first contact from the qualified stationary-origin prefix."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=ROOT/'results/autonomous_film_20261119_stationary_impact_remainder1550';proof=json.loads((ref/'summary.json').read_text());birth=ROOT/'results/autonomous_film_20261119_stationary_birth_reference1549';bp=json.loads((birth/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261119_stationary_to230_1547';m=json.loads((parent/'summary.json').read_text());cp=ref/'input.checkpoint'
 if proof['status']!='PASS' or bp['status']!='PASS' or bp['parent_summary_sha256']!=sha(parent/'summary.json') or proof['parent_summary_sha256']!=sha(birth/'summary.json') or sha(cp)!=proof['source_checkpoint_sha256'] or sha(cp)!=bp['source_checkpoint_sha256']:raise ValueError('qualified actual prefix plus independent birth/remainder required')
 for path,meta in ((ref,proof),(birth,bp),(parent,m)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('compiled physical source changed')
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('qualified raw changed')
 tokens=cp.read_text().split();time,h=float(tokens[1]),float(tokens[2]);out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_lateral_rest_contact',archive/'models/film_lateral_rest_contact',dirs_exist_ok=True)
 key='models/film_lateral_rest_contact/FirstImpact.h'
 if sha(archive/key)!=proof['source_hashes'][key]:raise ValueError('qualified impact/remainder law changed')
 # Owner registration embedding only; no physical/header or force changes.
 path=archive/'models/film_lateral_rest_resume/RestResume.cpp';text=path.read_text();anchor='void registerFilmLateralField(sofa::core::ObjectFactory*);'
 if text.count(anchor)!=1 or 'REGRIP_LATERAL_REST_RESUME_EMBEDDED' in text:raise ValueError('frozen standalone registration anchor differs')
 path.write_text(text.replace(anchor,'#ifndef REGRIP_LATERAL_REST_RESUME_EMBEDDED\n'+anchor)+'#endif\n')
 if path.read_text()!=(ROOT/'models/film_lateral_rest_resume/RestResume.cpp').read_text():raise ValueError('only exact declared registration embedding change permitted')
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('stationary_impact_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_lateral_rest_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;forecast=2*proof['process']['runtime_s']+30;r=dict(status='FAIL',scope='ACTUAL isolated stationary-origin C2 impact+remainder20.2..20.4ms;NOT global earliest CCD/time/energy/wrapping/holding/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,parent_summary_sha256=sha(parent/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),birth_reference_sha256=sha(birth/'summary.json'),source_checkpoint_sha256=sha(cp),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_reaction_impulse=None,global_momentum='NOT independently measured;reduced residual norm bound',whole_energy='BLOCKED',contact_area=None,pressure=None,holding_capacity=None)
 if forecast>480:r.update(status='BLOCKED',failure_reason='measured child forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
 if compile and compile['exit_code']==0:
  binary=build/'libReGripStationaryImpact.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  identity=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),input=sha(cp)),sort_keys=True).encode()).hexdigest();before=tokens.copy();tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=before[:4]+before[5:]:raise ValueError('physical state/time changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('LateralRestResumeODE');owner.tag='StationaryImpactODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',identity);owner.set('endTime',format(time+h,'.17g'))
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripLateralRestResume.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('actual parent binary changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=identity,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'));run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and not errors:
   actual=next(csv.DictReader((out/'three.stationary.event.csv').open()));expected=next(csv.DictReader((ref/'states.csv').open()));ab=next(csv.DictReader((out/'three.stationary.birth.csv').open()));eb=next(csv.DictReader((birth/'birth.csv').open()));delta={k:float(np.max(abs(np.fromstring(actual[k],sep=' ')-np.fromstring(expected[k],sep=' ')))) for k in ('q','v','impulse_Ns')};bd={k:float(np.max(abs(np.fromstring(ab[k],sep=' ')-np.fromstring(eb[k],sep=' ')))) for k in ('qminus','vminus','vplus','impulse_Ns')};stages=list(csv.DictReader((out/'three.stationary.stages.csv').open()));es=list(csv.DictReader((ref/'states.csv.stages.csv').open()));stage_exact=stages==es;metrics={k:float(actual[k]) for k in ('time','event_time','rows','rank','gap_mm','momentum_bound_Ns','impact_loss_Nmm')};metrics_exact=all(actual[k]==expected[k] for k in metrics);r.update(status='PASS' if max(delta.values())<=1e-12 and max(bd.values())<=1e-12 and stage_exact and metrics_exact and metrics['gap_mm']>=-1e-10 and metrics['momentum_bound_Ns']<=1e-17 else 'FAIL',reference_max_abs=delta,birth_reference_max_abs=bd,ALL_contact_stage_rows_exact=stage_exact,all_event_metrics_exact=metrics_exact,metrics=metrics)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','configure','compile','process')}))
if __name__=='__main__':main()
