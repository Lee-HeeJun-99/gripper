"""Actual separated FREE V3 continuation and optional byte-exact resume proof."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--compare',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text())
 if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('complete qualified actual parent required')
 for name,digest in meta['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('parent raw changed')
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2]);clock=time
 for _ in range(a.steps):clock+=dt
 if tokens[0]!='REGRIP_FREE_V3' or not 1<=a.steps<=64 or dt!=.0001 or clock>.03+1e-14:raise ValueError('bounded separated FREE V3 physical window required')
 forecast=2*meta['process']['runtime_s']*a.steps/meta.get('steps',1)+30
 if forecast>480:raise ValueError('measured child forecast exceeds480s')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();binary=next(n.get('pluginName') for n in scene.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripThreeFilmRelease.so'))
 if sha(binary)!=meta['binary_sha256']:raise ValueError('qualified release/free DLL changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');scene.set('time',tokens[1]);scene.set('dt',tokens[2]);owner=scene.find('ThreeFilmFreeODE');owner=scene.find('ThreeFilmAccelerationReleaseODE') if owner is None else owner;owner.tag='ThreeFilmFreeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',tokens[4]);owner.set('endTime','.03')
 for node in scene.iter():
  for key,value in list(node.attrib.items()):
   if key in ('filename','displacementFilename','publicMassFilename') and value.startswith(str(src)):node.set(key,str(out)+value[len(str(src)):])
 tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result=dict(status='FAIL',scope='actual FREE V3 separated continuation with whole dense numerical-path reimpact rejection;NOT full time/energy/recovery/grasp',parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),binary_sha256=sha(binary),sdk=str(SDK),input_checkpoint_sha256=sha(checkpoint),scene_sha256=sha(out/'scene.scn'),dt=dt,start_time=time,steps=a.steps,predicted_runtime_s=forecast,process=run,sofa_errors=errors,root_reaction_work=None,legacy_sampled_work='new private origin,NOT continuous',active_contact_count=0)
 if run['exit_code']==0 and not errors:
  rows=list(csv.DictReader((out/'three.states.csv').open()));expected_time=time
  for row in rows:
   expected_time+=dt
   if float(row['time'])!=expected_time:raise ValueError('global accumulated clock changed')
  gap=min(float(r['minimum_gap']) for r in rows);momentum=max(float(r['momentum_residual']) for r in rows);result.update(status='EXPERIMENTAL' if len(rows)==a.steps and gap>=-1e-10 and momentum<=1e-17 else 'FAIL',end_time=expected_time,minimum_gap_mm=gap,momentum_Ns=momentum,normal_constraint_residual=None)
  if a.compare:
   original=list(csv.DictReader((src/'three.states.csv').open()));indices=[i for i,r in enumerate(original) if float(r['time'])==time]
   if len(indices)!=1 or len(original)<indices[0]+1+a.steps:raise ValueError('existing complete comparison window required')
   start=indices[0]+1;reference=original[start:start+a.steps];state_errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,reference)) for k in ('q','v')};expected_stages=[r for r in csv.DictReader((src/'three.free.stages.csv').open()) if int(r['macro'])>a.checkpoint_step][:3*a.steps];stages=list(csv.DictReader((out/'three.free.stages.csv').open()));field_error=0
   for f in range(3):
    actual=list(csv.DictReader((out/f'film_{f}.csv').open()));expected=list(csv.DictReader((src/f'film_{f}.csv').open()))[start:start+a.steps]
    for x,y in zip(actual,expected):
     for k in x:
      if k!='tendon_work':field_error=max(field_error,float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))))
   snapshots={str(a.checkpoint_step+i+1):sha(out/f'three.checkpoint_{a.checkpoint_step+i+1}.txt')==sha(src/f'three.checkpoint_{a.checkpoint_step+i+1}.txt') for i in range(a.steps)};result.update(status='PASS' if result['status']=='EXPERIMENTAL' and max(state_errors.values())<1e-12 and field_error<1e-12 and stages==expected_stages and all(snapshots.values()) else 'FAIL',reference_max_abs=state_errors,actual_field_max_abs=field_error,all_stages_exact=stages==expected_stages,serialized_snapshots_byte_exact=snapshots,absolute_api_gate=1e-12)
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.txt','.csv')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('process','raw_hashes')}))
if __name__=='__main__':main()
