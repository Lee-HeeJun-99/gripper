"""Bind EXISTING isolated124→117 transfer owner to routed forces and fixture.
Original owner/SDK remain unchanged;all new guards describe24.2ms200us IVP.
"""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',default='20261118_routed_birth_transfer1327');a=p.parse_args();ref=ROOT/'results'/('autonomous_film_'+a.reference);proof=json.loads((ref/'summary.json').read_text());prefix=ROOT/'results/autonomous_film_20261118_routed_drift_probe1319';pm=json.loads((prefix/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_routed_unload_to2761312';m=json.loads((parent/'summary.json').read_text());checkpoint=prefix/'input.checkpoint'
 if proof['status']!='PASS' or proof['mode'] not in ('detected-birth','smooth-birth') or proof['input_checkpoint_sha256']!=sha(checkpoint) or pm['actual_summary_sha256']!=sha(parent/'summary.json') or not pm['accepted_prefix_qv_time_exact'] or m['status']!='FAIL':raise ValueError('independent transfer and exact accepted prefix of preserved failed horizon required')
 for f,d in proof['source_hashes'].items():
  if sha(ref/'sources'/f)!=d:raise ValueError('qualified reference source changed')
 for f,d in proof['raw_hashes'].items():
  if sha(ref/f)!=d:raise ValueError('qualified transfer output changed')
 tokens=checkpoint.read_text().split();time,h=float(tokens[1]),float(tokens[2]);end=time+h
 if not .0241<time<.0243 or h!=.0002 or tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1':raise ValueError('new200us24.2ms isolated fixture differs')
 forecast=2*proof['process']['runtime_s']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');path=archive/'models/film_three_finger_transfer/ThreeFilmTransfer.cpp';text=path.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda m:'Routed'+m.group(),text)
 changes={'dt!=.0001||getContext()->getTime()!=initialTime||initialTime<.0233||initialTime>.0235':'dt!=.0002||getContext()->getTime()!=initialTime||initialTime<.0241||initialTime>.0243','extern "C" {':'void registerFilmRoutedField(sofa::core::ObjectFactory*);\nextern "C" {','void registerObjects(sofa::core::ObjectFactory*f){':'void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);','return "ReGripThreeFilmTransfer";':'return "ReGripRoutedThreeFilmTransfer";'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('routed transfer exact generation anchor differs')
  text=text.replace(old,new)
 path.write_text(text);cmake=archive/'models/film_three_finger_transfer/CMakeLists.txt';text=cmake.read_text();anchor='SHARED ThreeFilmTransfer.cpp)'
 if text.count(anchor)!=1:raise ValueError('transfer CMake anchor differs')
 cmake.write_text(text.replace(anchor,'SHARED ThreeFilmTransfer.cpp ../film_routed_tendon/Field.generated.cpp)'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('routed_birth_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_transfer','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='actual isolated routed124→117 simultaneous birth/impact/old-row release ONLY;NOT global CCD/full Unload/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),prefix_summary_sha256=sha(prefix/'summary.json'),old_horizon_status='FAIL remains',source_checkpoint_sha256=sha(checkpoint),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_reaction_work=None,legacy_sampled_work='NOT restored;exclude ALL sampled-work values')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmTransfer.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('routed transfer SDK ABI mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),source_checkpoint=sha(checkpoint),reference=sha(ref/'summary.json')),sort_keys=True).encode()).hexdigest();original=tokens.copy();tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=original[:4]+original[5:]:raise ValueError('physical payload changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE');owner.tag='RoutedThreeFilmContactTransferODE';owner.set('identity',token);owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(end,'.17g'));owner.attrib.pop('ownerCostFilename',None);legacy=json.loads((ROOT/'results/autonomous_film_20261118_three_film_first_peak_actual1002/summary.json').read_text())
  for node in scene.iter():
   if node.tag=='RequiredPlugin':
    value=node.get('pluginName','')
    if value.endswith('/libReGripThreeFilmResume.so'):
     if sha(value)!=m['binary_sha256']:raise ValueError('parent executable changed')
     node.set('pluginName',str(binary))
    elif value.startswith('/') and sha(value)!=legacy['plugins'].get(value):raise ValueError('mapping dependency changed')
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=token,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),physical_checkpoint_payload_exact=True)
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')))
  if run['exit_code']==0 and not r['sofa_errors']:
   actual=list(csv.DictReader((out/'three.states.csv').open()));event=next(csv.DictReader((out/'three.transfer.event.csv').open()));impulses=list(csv.DictReader((out/'three.transfer.impulses.csv').open()));expected_rows=list(csv.DictReader((ref/'transfer.rows.csv').open()));expected=(ref/'transfer.states.txt').read_text().splitlines();api={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(expected[-2 if k=='q' else -1],sep=' ')))) for k in ('q','v')};p_error=max(abs(float(x['impulse_Ns'])-float(y['impulse_Ns'])) for x,y in zip(impulses,expected_rows));clock=float(actual[0]['time'])==float(expected[-3].split()[1]);event_error=abs(float(event['event_time'])-float(proof['event_metrics']['event_time_s']));gap=float(event['minimum_stage_gap_mm']);momentum=float(event['momentum_Ns']);minimum_p=min(float(x['impulse_Ns']) for x in impulses)
   r.update(status='PASS' if len(actual)==1 and len(impulses)==len(expected_rows)==6 and max(api.values())<1e-12 and clock and p_error<1e-12 and event_error==0 and gap>=-1e-10 and momentum<=1e-17 and minimum_p>=0 else 'FAIL',reference_max_abs=api,accumulated_clock_exact=clock,event_time_error_s=event_error,impulse_max_abs_Ns=p_error,minimum_impulse_Ns=minimum_p,event_metrics=event,api_gate=1e-12)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes','event_metrics')}))
if __name__=='__main__':main()
