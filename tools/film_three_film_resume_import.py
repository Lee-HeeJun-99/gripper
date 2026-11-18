"""Explicit dt contrast from a COMPLETE actual checkpoint;not a physical correction.
Requires an independently strict-qualified current-source resume DLL.
"""
import argparse,csv,hashlib,json,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--binary-case',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--dt',type=float,choices=(.0002,.0001,.00005),required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--end-time',type=float,required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text());qualified=ROOT/'results'/('autonomous_film_'+a.binary_case);qm=json.loads((qualified/'summary.json').read_text())
 if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors'] or qm['status']!='PASS' or max(qm['reference_max_abs'].values())>=1e-12:raise ValueError('complete parent and strict current DLL proof required')
 for n,h in meta['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('parent raw changed')
 for n,h in qm['sources'].items():
  if n.endswith('.h') or n in ('models/film_three_finger/ThreeFilmOwner.cpp','models/film_three_finger_resume/ThreeFilmResume.cpp','models/film_three_finger_resume/CMakeLists.txt'):
   if sha(qualified/'sources'/n)!=h or sha(ROOT/n)!=h:raise ValueError('compiled source bytes changed')
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';tokens=checkpoint.read_text().split();start=float(tokens[1])
 if not 1<=a.steps<=64 or start+a.steps*a.dt>a.end_time+1e-14 or not start<a.end_time<=.03:raise ValueError('bounded dt contrast window required')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();qscene=ET.parse(qualified/'scene.scn').getroot();binary=next(n.get('pluginName') for n in qscene.findall('RequiredPlugin') if n.get('pluginName','').endswith(('/libReGripThreeFilmResume.so','/libReGripThreeFilmTransfer.so')))
 if sha(binary)!=qm['binary_sha256']:raise ValueError('resume binary changed')
 # Event-root work in a transfer parent is not the cost of persistent steps.
 # Use measured qualified persistent-owner cost for the first small bridge.
 profile=qm if 'isolated' in meta.get('scope','') else meta
 estimate=2*profile['process']['runtime_s']*a.steps/profile['steps']+30
 if estimate>480:raise ValueError('measured forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');token=hashlib.sha256(json.dumps(dict(parent=sha(src/'summary.json'),checkpoint=sha(checkpoint),binary=sha(binary),dt=a.dt),sort_keys=True).encode()).hexdigest();tokens[2]=format(a.dt,'.17g');tokens[4]=token;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n');scene.set('dt',tokens[2]);scene.set('time',tokens[1]);owner=scene.find('ThreeFilmResumeODE');owner=scene.find('ThreeFilmContactTransferODE') if owner is None else owner;owner.tag='ThreeFilmResumeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',token);owner.set('endTime',format(a.end_time,'.17g'))
 for node in scene.iter():
  for k,v in list(node.attrib.items()):
   if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
  if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith(('/libReGripThreeFilmResume.so','/libReGripThreeFilmTransfer.so')):node.set('pluginName',binary)
 tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result=dict(status='FAIL',scope='actual numerical dt contrast from SAME physical checkpoint;NOT time convergence certificate or grasp',source_commit=qm['source_commit'],binary_case=a.binary_case,binary_sha256=sha(binary),parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),prior_checkpoint_sha256=sha(checkpoint),checkpoint_sha256=sha(out/'input.checkpoint'),identity=token,scene_sha256=sha(out/'scene.scn'),sdk=str(SDK),start_time=start,dt=a.dt,steps=a.steps,predicted_runtime_s=estimate,process=run,sofa_errors=errors,legacy_sampled_work='new private ledger;not continuous work',root_reaction_work=None)
 if run['exit_code']==0 and not errors:
  states=list(csv.DictReader((out/'three.states.csv').open()));gap=min(float(r['minimum_gap']) for r in states);mom=max(float(r['momentum_residual']) for r in states);vn=max(float(r['normal_velocity_residual']) for r in states);clock=start
  for r in states:
   clock+=a.dt
   if float(r['time'])!=clock:raise ValueError('accumulated clock mismatch')
  result.update(status='EXPERIMENTAL' if len(states)==a.steps and gap>=-1e-10 and mom<=1e-17 and vn<=1e-10 else 'FAIL',end_time=clock,minimum_gap_mm=gap,momentum_max_Ns=mom,normal_velocity_max_mm_s=vn)
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('raw_hashes','process')}))
if __name__=='__main__':main()
