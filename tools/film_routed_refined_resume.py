"""Explicit projected-state preserving100us continuation;not arbitrary dt skip."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--qualification',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--steps',type=int,choices=(4,8,16,32),default=16);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((src/'summary.json').read_text());qp=ROOT/'results'/('autonomous_film_'+a.qualification);qm=json.loads((qp/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_routed_resume1278';proof=json.loads((provider/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt'
 if m['status']!='EXPERIMENTAL' or m['process']['exit_code'] or m['sofa_errors'] or qm['status']!='PASS' or qm['actual_summary_sha256']!=sha(src/'summary.json') or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('qualified completed actual source checkpoint required')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('routed physical source archive changed')
 if sha(src/'scene.scn')!=m['scene_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=m['sdk_runner_sha256']:raise ValueError('source Scene/SDK changed')
 tokens=checkpoint.read_text().split();time,used=float(tokens[1]),float(tokens[2]);end=time
 if tokens[0]!='REGRIP_ROUTED_PERSISTENT_V1' or used!=.0002 or int(tokens[3])!=a.checkpoint_step or tokens[4]!=m['identity']:raise ValueError('initial explicit V1 200→100us transition only')
 for i in range(a.steps):end+=.0001
 if not .01<=time<end<=.03:raise ValueError('bounded C2 contact window')
 forecast=2*m['process']['runtime_s']*a.steps/m['actual_steps']+30
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_routed_refined_resume',archive/'models/film_routed_refined_resume');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('routed_refined_'+a.tag);build.mkdir(exist_ok=False)
 configure=guarded(['cmake','-S',archive/'models/film_routed_refined_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;r=dict(status='FAIL',scope='actual explicit100us one-step continuation;NOT adaptive/full time/energy/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,source_parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),qualification_summary_sha256=sha(qp/'summary.json'),source_checkpoint_sha256=sha(checkpoint),configure=configure,compile=compile,predicted_child_runtime_s=forecast,start_time_s=time,prior_used_dt_s=used,dt_s=.0001,actual_steps=a.steps,expected_end_time_s=end,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),root_reaction_work=None,legacy_sampled_work='NOT restored;excluded')
 if compile and compile['exit_code']==0:
  binary=build/'libReGripRoutedRefinedResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  token=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary),source_checkpoint=sha(checkpoint),next_dt_s=.0001),sort_keys=True).encode()).hexdigest();oldtoken=tokens[4];tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if (out/'input.checkpoint').read_text().split()[:4]+(out/'input.checkpoint').read_text().split()[5:]!=checkpoint.read_text().split()[:4]+checkpoint.read_text().split()[5:]:raise ValueError('physical checkpoint payload changed')
  tree=ET.parse(src/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('RoutedThreeFilmResumeODE');owner.tag='RoutedHalfStepResumeODE';owner.set('identity',token);owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(end,'.17g'));owner.attrib.pop('ownerCostFilename',None);owner.set('reuseJournalRows','1')
  for node in scene.iter():
   if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripThreeFilmResume.so'):
    if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('parent executable changed')
    node.set('pluginName',str(binary))
   for k,v in list(node.attrib.items()):
    if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
  tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),build_relative=str(build.relative_to(ROOT)),identity=token,source_identity=oldtoken,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'),physical_checkpoint_tokens_exact_except_provenance=True)
  if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
  run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);r.update(process=run,sofa_errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log')))
  if run['exit_code']==0 and not r['sofa_errors']:
   rows=list(csv.DictReader((out/'three.states.csv').open()));restart=next(csv.DictReader((out/'three.restart.csv').open()));clock=time;exact=True
   for row in rows:clock+=.0001;exact=exact and float(row['time'])==clock
   r.update(status='EXPERIMENTAL' if len(rows)==a.steps and exact and float(restart['prior_used_dt'])==used and float(restart['next_dt'])==.0001 else 'FAIL',accumulated_clock_exact=exact,end_time_s=clock,minimum_whole_stage_gap_mm=min(float(x['minimum_gap']) for x in rows),momentum_residual_Ns=max(float(x['momentum_residual']) for x in rows),normal_velocity_residual_mm_s=max(float(x['normal_velocity_residual']) for x in rows))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','configure','compile','process','raw_hashes')}))
if __name__=='__main__':main()
