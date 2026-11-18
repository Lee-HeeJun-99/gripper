"""Source-bound actual release using existing primitive API commit/mass owner."""
import argparse,csv,hashlib,json,re,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();ref=ROOT/'results/autonomous_film_20261118_lateral_release128_1518';proof=json.loads((ref/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_lateral_to270_actual1509';m=json.loads((parent/'summary.json').read_text());checkpoint=ref/'input.checkpoint'
 if proof['status']!='PASS' or proof['grid']!=128 or m['status']!='PASS' or proof['input_checkpoint_sha256']!=sha(checkpoint):raise ValueError('qualified release reference and actual IVP required')
 for path,meta in ((ref,proof),(parent,m)):
  for f,d in meta['source_hashes'].items():
   if sha(path/'sources'/f)!=d:raise ValueError('source archive changed')
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('actual/reference raw changed')
 tokens=checkpoint.read_text().split();time,h=float(tokens[1]),float(tokens[2]);forecast=2*proof['process']['runtime_s']+30
 if tokens[0]!='REGRIP_LATERAL_CONTROLLED_V1' or h!=.0002 or not .0269<time<.0271:raise ValueError('explicit actual27ms fixture differs')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ref/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_lateral_release',archive/'models/film_lateral_release');path=archive/'models/film_three_finger_primitive/ThreeFilmPrimitive.cpp';path.write_text(re.sub(r'\bThreeFilm[A-Za-z0-9_]*ODE\b',lambda m:'Routed'+m.group(),path.read_text()));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('lateral_release_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_lateral_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='ACTUAL lateral deformed release27..27.2ms ONLY;NOT full time/energy/recovery/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,reference_summary_sha256=sha(ref/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(checkpoint),configure=configure,compile=compile,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_work=None,legacy_sampled_work='NOT restored/spliced',edge_birth_history='UNMEASURED;NOT invented',momentum_metric='sum of segment residual norms,not independent global vector defect',release_time='collocation admissibility/RK stages,not certified continuous exit root')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripLateralRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  identity=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary),input=sha(checkpoint)),sort_keys=True).encode()).hexdigest();original=tokens.copy();tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=original[:4]+original[5:]:raise ValueError('physical checkpoint changed')
  tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE');owner.tag='LateralReleaseODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',identity);owner.set('endTime',format(time+h,'.17g'));owner.attrib.pop('ownerCostFilename',None)
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
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((ref/'states.csv').open()));metrics=next(csv.DictReader((out/'three.release.metrics.csv').open()));aa=list(csv.DictReader((out/'three.release.rk.csv').open()));bb=list(csv.DictReader((ref/'states.csv.rk.csv').open()));api={k:float(np.max(abs(np.fromstring(actual[0][k],sep=' ')-np.fromstring(expected[0][k],sep=' ')))) for k in ('q','v')};stage=0.;clock=len(aa)==len(bb)==512
   for x,y in zip(aa,bb):
    clock=clock and all(float(x[k])==float(y[k]) for k in ('time','weight_s','mask'));stage=max(stage,*(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for k in ('q','v','force')))
   end=float(actual[0]['time']);r.update(status='PASS' if len(actual)==1 and max(api.values())<=1e-12 and stage<=1e-12 and clock and end==float(expected[0]['time']) and float(metrics['minimum_gap_mm'])>=-1e-10 and float(metrics['momentum_bound_Ns'])<=1e-17 and int(metrics['final_mask'])==0 and float(metrics['outgoing_normal_velocity_mm_s'])>0 else 'FAIL',reference_max_abs=api,RK_stage_max_abs=stage,all_RK_times_weights_masks_exact=clock,end_time_s=end,release_metrics=metrics)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
