"""Actual routed Face→material Edge transfer,using existing owner/law."""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=ROOT/'results/autonomous_film_20261118_routed_next_face_edge1334';proof=json.loads((ref/'summary.json').read_text());prefix=ROOT/'results/autonomous_film_20261118_routed_post_birth_prefix1333';pm=json.loads((prefix/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_routed_after_birth1332';m=json.loads((parent/'summary.json').read_text());checkpoint=prefix/'input.checkpoint'
 if proof['status']!='PASS' or proof['mode']!='face-edge' or pm['actual_summary_sha256']!=sha(parent/'summary.json') or proof['input_checkpoint_sha256']!=sha(checkpoint) or not pm['accepted_prefix_qv_time_exact']:raise ValueError('matched accepted prefix and qualified face-edge reference required')
 for f,d in proof['source_hashes'].items():
  if sha(ref/'sources'/f)!=d:raise ValueError('reference source archive changed')
 for f,d in proof['raw_hashes'].items():
  if sha(ref/f)!=d:raise ValueError('reference state changed')
 tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);end=time+dt;expected=list(csv.DictReader((ref/'states.csv').open()))
 if len(expected)!=2 or [x['state'] for x in expected]!=['event','post'] or float(expected[-1]['time'])!=end or float(expected[0]['time'])!=time+proof['event_h_s'] or tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1':raise ValueError('true source/result clocks or physical schema differ')
 forecast=2*proof['process']['runtime_s']+30;out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');path=archive/'models/film_three_finger_primitive/ThreeFilmPrimitive.cpp';text=path.read_text();text=re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda x:'Routed'+x.group(),text)
 for old,new in {'"REGRIP_EDGE_V2"':'"REGRIP_ROUTED_EDGE_V2"','"REGRIP_PERSISTENT_V1"':'"REGRIP_ROUTED_PERSISTENT_V1"'}.items():
  if text.count(old)!=(2 if 'EDGE' in old else 1):raise ValueError('route-bound primitive schema anchor differs')
  text=text.replace(old,new)
 changes={'extern "C" {':'void registerFilmRoutedField(sofa::core::ObjectFactory*);\nextern "C" {','void registerObjects(sofa::core::ObjectFactory*f){':'void registerObjects(sofa::core::ObjectFactory*f){registerFilmRoutedField(f);','return "ReGripThreeFilmPrimitive";':'return "ReGripRoutedThreeFilmPrimitive";'}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('primitive generation anchor differs')
  text=text.replace(old,new)
 path.write_text(text);cmake=archive/'models/film_three_finger_primitive/CMakeLists.txt';text=cmake.read_text();anchor='SHARED ThreeFilmPrimitive.cpp)'
 if text.count(anchor)!=1:raise ValueError('primitive CMake differs')
 cmake.write_text(text.replace(anchor,'SHARED ThreeFilmPrimitive.cpp ../film_routed_tendon/Field.generated.cpp)'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('routed_edge_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_three_finger_primitive','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='actual isolated routed Face→Edge C1 event,no impulse;NOT full Unload/object release/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),prefix_summary_sha256=sha(prefix/'summary.json'),source_checkpoint_sha256=sha(checkpoint),reference_stale_scope_label=proof['scope'],verified_true_start_time_s=time,dt_s=dt,expected_end_time_s=end,configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_reaction_work=None,legacy_sampled_work='NOT restored;exclude ALL sampled-work values',old_horizon_status='FAIL remains')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmPrimitive.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('routed Edge SDK ABI mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),checkpoint=sha(checkpoint),reference=sha(ref/'summary.json')),sort_keys=True).encode()).hexdigest();old=tokens.copy();tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=old[:4]+old[5:]:raise ValueError('physical checkpoint payload changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE');owner.tag='RoutedThreeFilmFaceEdgeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime',format(end,'.17g'));owner.attrib.pop('ownerCostFilename',None)
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmResume.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('parent executable changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=token,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),physical_checkpoint_payload_exact=True)
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')))
  if run['exit_code']==0 and not r['sofa_errors']:
   states=list(csv.DictReader((out/'three.states.csv').open()));event=next(csv.DictReader((out/'three.primitive.events.csv').open()));actual=next(csv.DictReader((out/'three.primitive.actual.csv').open()));body_event={'q':event['event_q'],'v':event['event_v']};api={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in ((states[0],expected[-1]),(body_event,expected[0]))) for k in ('q','v')};clock=float(states[0]['time'])==end and float(event['time'])==float(expected[0]['time'])
   # Preserve exact actual control values;no independently reconstructed pulse.
   control=max(abs(float(next(csv.DictReader((out/f'film_{f}.csv').open()))['T_per_rail'])-float(actual['endpoint_tension'])) for f in range(3));gap=min(float(x['minimum_gap']) for x in states);momentum=max(float(x['momentum_residual']) for x in states);vn=max(float(x['normal_velocity_residual']) for x in states);snapshots=list(out.glob('three.checkpoint_*.txt'));r.update(status='PASS' if len(states)==1 and max(api.values())<1e-12 and clock and control==0 and gap>=-1e-10 and momentum<=1e-17 and vn<=1e-10 and event['impulse_applied']=='false' and len(snapshots)==1 and snapshots[0].read_text().startswith('REGRIP_ROUTED_EDGE_V2 ') else 'FAIL',reference_max_abs=api,accumulated_clock_exact=clock,actual_control_error_N=control,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=momentum,normal_velocity_residual_mm_s=vn,event_time_s=float(event['time']),J_continuity_error=float(event['J_continuity_max']),impulse_applied=False,api_gate=1e-12)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
