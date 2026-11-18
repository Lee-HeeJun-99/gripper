"""Actual same-binary V2 material-edge restore;strict continuous-run comparison."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',default='20261118_three_film_primitive_actual1059');p.add_argument('--checkpoint-step',type=int,default=137);p.add_argument('--steps',type=int,default=4);p.add_argument('--compare',action='store_true');p.add_argument('--end-time',type=float,default=.025);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.parent);meta=json.loads((src/'summary.json').read_text())
 if meta['status'] not in ('PASS','EXPERIMENTAL') or meta['process']['exit_code'] or meta['sofa_errors']:raise ValueError('completed actual primitive parent required')
 for n,h in meta['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('parent raw changed')
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt';tokens=checkpoint.read_text().split();time,dt=float(tokens[1]),float(tokens[2])
 if tokens[0]!='REGRIP_EDGE_V2' or not 1<=a.steps<=64 or time+dt*a.steps>a.end_time+1e-14 or not time<a.end_time<=.03:raise ValueError('explicit V2 bounded continuation required')
 tree=ET.parse(src/'scene.scn');scene=tree.getroot();binary=next(n.get('pluginName') for n in scene.findall('RequiredPlugin') if n.get('pluginName','').endswith('/libReGripThreeFilmPrimitive.so'))
 if sha(binary)!=meta['binary_sha256']:raise ValueError('primitive binary changed')
 estimate=2*meta['process']['runtime_s']*a.steps/meta['steps']+30
 if estimate>480:raise ValueError('measured child forecast exceeds480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');scene.set('time',tokens[1]);scene.set('dt',tokens[2]);owner=scene.find('ThreeFilmFaceEdgeODE');owner=scene.find('ThreeFilmEdgeODE') if owner is None else owner;owner.tag='ThreeFilmEdgeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',tokens[4]);owner.set('endTime',format(a.end_time,'.17g'))
 for node in scene.iter():
  for k,v in list(node.attrib.items()):
   if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(src)):node.set(k,str(out)+v[len(str(src)):])
 tree.write(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/n).read_text(errors='replace').count('[ERROR]') for n in ('stdout.log','stderr.log'));result=dict(status='FAIL',scope='actual V2 material-edge checkpoint resume/continuation;NOT full Unload/release/time/grasp',parent=a.parent,parent_summary_sha256=sha(src/'summary.json'),binary_sha256=sha(binary),sdk=str(SDK),checkpoint_sha256=sha(checkpoint),identity=tokens[4],scene_sha256=sha(out/'scene.scn'),dt=dt,start_time=time,steps=a.steps,predicted_runtime_s=estimate,process=run,sofa_errors=errors,legacy_sampled_work='NEW private origin;not continuous',root_reaction_work=None)
 if run['exit_code']==0 and not errors:
  states=list(csv.DictReader((out/'three.states.csv').open()));gap=min(float(r['minimum_gap']) for r in states);mom=max(float(r['momentum_residual']) for r in states);vn=max(float(r['normal_velocity_residual']) for r in states);clock=time
  for r in states:
   clock+=dt
   if float(r['time'])!=clock:raise ValueError('actual accumulated clock changed')
  result.update(status='EXPERIMENTAL' if len(states)==a.steps and gap>=-1e-10 and mom<=1e-17 and vn<=1e-10 else 'FAIL',end_time=clock,minimum_gap_mm=gap,momentum_max_Ns=mom,normal_velocity_max_mm_s=vn)
  if a.compare:
   original=list(csv.DictReader((src/'three.states.csv').open()));indices=[i for i,r in enumerate(original) if float(r['time'])==time]
   if len(indices)!=1 or len(original)<indices[0]+1+a.steps:raise ValueError('continuous comparison window missing')
   start=indices[0]+1;expected=original[start:start+a.steps];state_errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(states,expected)) for k in ('q','v')};parent_rows=list(csv.DictReader((src/'three.primitive.stages.csv').open()));expected_rows=[r for r in parent_rows if int(r['macro'])>a.checkpoint_step][:9*a.steps];rows=list(csv.DictReader((out/'three.primitive.stages.csv').open()));exact_rows=rows==expected_rows;field_error=0
   for f in range(3):
    actual=list(csv.DictReader((out/f'film_{f}.csv').open()));reference=list(csv.DictReader((src/f'film_{f}.csv').open()))[start:start+a.steps]
    for x,y in zip(actual,reference):
     for k in x:
      if k!='tendon_work':field_error=max(field_error,float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))))
   snapshot_exact={f'three.checkpoint_{a.checkpoint_step+i+1}.txt':sha(out/f'three.checkpoint_{a.checkpoint_step+i+1}.txt')==sha(src/f'three.checkpoint_{a.checkpoint_step+i+1}.txt') for i in range(a.steps)};result.update(status='PASS' if result['status']=='EXPERIMENTAL' and max(state_errors.values())<1e-12 and exact_rows and field_error<1e-12 and all(snapshot_exact.values()) else 'FAIL',reference_max_abs=state_errors,all_stage_rows_exact=exact_rows,actual_field_max_abs=field_error,serialized_v2_checkpoints_byte_exact=snapshot_exact,absolute_api_gate=1e-12)
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('raw_hashes','process')}))
if __name__=='__main__':main()
