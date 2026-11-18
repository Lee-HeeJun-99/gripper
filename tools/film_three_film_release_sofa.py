"""Actual isolated acceleration-contact release,strict independent q/v comparison."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',default='20261118_three_film_acc_local1075');a=p.parse_args()
 ref=ROOT/'results'/('autonomous_film_'+a.reference);proof=json.loads((ref/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261118_three_film_edge_unload1061';pm=json.loads((parent/'summary.json').read_text());checkpoint=parent/'three.checkpoint_170.txt'
 if proof['status']!='PASS' or proof.get('acc_grid')!=64 or sha(checkpoint)!=proof['checkpoint_sha256'] or sha(checkpoint)!=pm['raw_hashes'][checkpoint.name] or sha(ref/'rejected.csv')!=proof['rejected_csv_sha256']:raise ValueError('qualified complete independent release and accepted prefix required')
 for name,digest in proof['sources'].items():
  if name.endswith('.h') and sha(ROOT/name)!=digest:raise ValueError('reference physics header changed:'+name)
 forecast=2*proof['run']['runtime_s']+30
 if forecast>480:raise ValueError('profiled isolated release forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('three_film_release_'+a.tag);build.mkdir(exist_ok=False)
 configure=guarded(['cmake','-S',archive/'models/film_three_finger_release','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual isolated20us acceleration-complementarity release plus80us free midpoint;NOT full time/energy/Unload/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,sdk=str(SDK),configure=configure,compile=compile,predicted_runtime_s=forecast,reference_summary_sha256=sha(ref/'summary.json'),initial_scope='individually accepted27ms prefix of FAILED1061,not a completed parent horizon',root_reaction_work=None,legacy_sampled_work='new private origin,NOT continuous')
 write_json(out/'summary.json',result)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripThreeFilmRelease.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in s and '=> /' in s and str(SDK) not in s for s in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),checkpoint=sha(checkpoint)),sort_keys=True).encode()).hexdigest();tokens=checkpoint.read_text().split();tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n');tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',tokens[1]);owner=scene.find('ThreeFilmEdgeODE');owner.tag='ThreeFilmAccelerationReleaseODE';owner.set('identity',token);owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime','.03')
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmPrimitive.so'):node.set('pluginName',str(binary))
  tree.write(out/'scene.scn');result.update(binary_sha256=sha(binary),identity=token,scene_sha256=sha(out/'scene.scn'),input_checkpoint_sha256=sha(out/'input.checkpoint'))
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=run;result['sofa_errors']=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'))
  if run['exit_code']==0 and not result['sofa_errors']:
   states=list(csv.DictReader((out/'three.states.csv').open()));expected=next(csv.DictReader((ref/'rejected.csv').open()));metrics=next(csv.DictReader((out/'three.release.metrics.csv').open()))
   if len(states)!=1:raise ValueError('exactly one actual accepted release step required')
   errors={k:float(np.max(abs(np.fromstring(states[0][k],sep=' ')-np.fromstring(expected[k],sep=' ')))) for k in ('q','v')};clock=abs(float(states[0]['time'])-float(expected['time']));rows=list(csv.DictReader((out/'three.release.stages.csv').open()));minimum_force=min(float(np.min(np.fromstring(r['force'],sep=' '))) for r in rows)
   free=list(csv.DictReader((out/'three.release.free.csv').open()));join_exact=len(free)==3 and float(free[0]['time'])==float(rows[-1]['time']) and float(free[-1]['time'])==float(states[0]['time'])
   result.update(status='PASS' if max(errors.values())<1e-12 and clock==0 and len(rows)==256 and join_exact and minimum_force>=0 and float(metrics['minimum_gap_mm'])>=-1e-10 and float(metrics['momentum_Ns'])<=1e-17 and float(metrics['outgoing_normal_velocity_min_mm_s'])>0 else 'FAIL',reference_max_abs=errors,time_error_s=clock,absolute_api_gate=1e-12,metrics=metrics,actual_RK_rows=len(rows),accumulated_stage_join_exact=join_exact,minimum_applied_normal_force_N=minimum_force,normal_constraint_residual_after_release=None,output_free_checkpoint_resume='NOT RUN')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','configure','compile','raw_hashes','process')}))
if __name__=='__main__':main()
