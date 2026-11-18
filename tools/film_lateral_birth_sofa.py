"""Existing isolated transfer owner bound to source-verified lateral dynamics."""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=ROOT/'results/autonomous_film_20261118_lateral_birth_reference1478';proof=json.loads((ref/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_lateral_controlled_actual_two1472';m=json.loads((parent/'summary.json').read_text());checkpoint=ref/'input.checkpoint'
 if proof['status']!='PASS' or m['status']!='PASS' or proof['actual_summary_sha256']!=sha(parent/'summary.json') or proof['input_checkpoint_sha256']!=sha(checkpoint):raise ValueError('same qualified actual lateral IVP/reference required')
 for path,meta in ((ref,proof),(parent,m)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('source archive changed')
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('actual/reference raw changed')
 tokens=checkpoint.read_text().split();time,h=float(tokens[1]),float(tokens[2]);end=time+h
 if tokens[0]!='REGRIP_LATERAL_CONTROLLED_V1' or not .0233<time<.0235 or h!=.0002:raise ValueError('isolated lateral23.4ms200us fixture differs')
 forecast=2*proof['process']['runtime_s']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');path=archive/'models/film_three_finger_transfer/ThreeFilmTransfer.cpp';text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda m:'Routed'+m.group(),path.read_text());changes={'dt!=.0001||getContext()->getTime()!=initialTime||initialTime<.0233||initialTime>.0235':'dt!=.0002||getContext()->getTime()!=initialTime||initialTime<.0233||initialTime>.0235','extern "C" {':'void registerFilmLateralField(sofa::core::ObjectFactory*);\nextern "C" {','void registerObjects(sofa::core::ObjectFactory*f){':'void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);','return "ReGripThreeFilmTransfer";':'return "ReGripLateralThreeFilmTransfer";'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('existing transfer owner source anchor differs')
  text=text.replace(old,new)
 path.write_text(text);cmake=archive/'models/film_three_finger_transfer/CMakeLists.txt';text=cmake.read_text();anchor='SHARED ThreeFilmTransfer.cpp)'
 if text.count(anchor)!=1:raise ValueError('existing transfer build anchor differs')
 cmake.write_text(text.replace(anchor,'SHARED ThreeFilmTransfer.cpp ../film_lateral_tendon/Field.generated.cpp)'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('lateral_birth_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_transfer','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='ACTUAL isolated lateral124-to117 simultaneous birth/impact/old-row release;NOT global CCD/full Unload/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_work=None)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmTransfer.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  identity=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),checkpoint=sha(checkpoint)),sort_keys=True).encode()).hexdigest();original=tokens.copy();tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=original[:4]+original[5:]:raise ValueError('physical checkpoint changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE');owner.tag='RoutedThreeFilmContactTransferODE';owner.set('identity',identity);owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(end,'.17g'))
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmResume.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('parent executable changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=identity,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'))
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and not errors:
   actual=list(csv.DictReader((out/'three.states.csv').open()));event=next(csv.DictReader((out/'three.transfer.event.csv').open()));impulses=list(csv.DictReader((out/'three.transfer.impulses.csv').open()));expected=list(csv.DictReader((ref/'transfer.rows.csv').open()));state=(ref/'transfer.states.txt').read_text().splitlines();api={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(state[-2 if k=='q' else -1],sep=' ')))) for k in ('q','v')};imp=max(abs(float(x['impulse_Ns'])-float(y['impulse_Ns'])) for x,y in zip(impulses,expected));clock=float(actual[0]['time'])==float(state[-3].split()[1]);eventError=abs(float(event['event_time'])-float(proof['event_metrics']['event_time_s']));gap=float(event['minimum_stage_gap_mm']);momentum=float(event['momentum_Ns'])
   r.update(status='PASS' if len(actual)==1 and len(impulses)==len(expected)==6 and max(api.values())<=1e-12 and clock and imp<=1e-12 and eventError==0 and gap>=-1e-10 and momentum<=1e-17 and min(float(x['impulse_Ns']) for x in impulses)>=0 else 'FAIL',reference_max_abs=api,impulse_max_abs_Ns=imp,accumulated_clock_exact=clock,event_time_error_s=eventError,event_metrics=event)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes','event_metrics')}))
if __name__=='__main__':main()
