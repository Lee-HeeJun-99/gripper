"""Snapshot a MATCHED finite accepted prefix;never relabel failed horizons."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--edge',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);ref=ROOT/'results'/('autonomous_film_'+a.reference);m=json.loads((src/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt'
 if m['status']!='FAIL' or r['status']!='FAIL' or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('preserved failed pair and actual accepted checkpoint required')
 if not a.edge and not m.get('physical_checkpoint_payload_exact'):raise ValueError('explicit post-event physical handoff proof required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual accepted evidence changed')
 for f,d in r['source_hashes'].items():
  if sha(ref/'sources'/f)!=d:raise ValueError('reference source archive changed')
 if a.edge:
  provider=ROOT/'results/autonomous_film_20261118_routed_edge_actual1336';pm=json.loads((provider/'summary.json').read_text())
  if m['binary_sha256']!=pm['binary_sha256'] or m['input_checkpoint_sha256']!=r['input_checkpoint_sha256'] or m['reference'] or not r['reference']:raise ValueError('same exact V2 IVP/module required')
  dependency=pm['source_hashes']
 else:dependency=m['compiled_dependency_closure']
 for f,d in dependency.items():
  if r['source_hashes'].get(f)!=d:raise ValueError('actual/reference compiled physical dependency differs')
 x=list(csv.DictReader((src/'three.states.csv').open()));y=list(csv.DictReader((ref/'states.csv').open()));tokens=checkpoint.read_text().split();n=1953
 if not x or len(x)!=len(y) or float(tokens[1])!=float(x[-1]['time']) or int(tokens[3])!=a.checkpoint_step:raise ValueError('whole observed accepted prefix and checkpoint endpoint required')
 for i,j in zip(x,y):
  if i['time']!=j['time'] or any(not np.array_equal(np.fromstring(i[k],sep=' '),np.fromstring(j[k],sep=' ')) for k in ('q','v')):raise ValueError('observed accepted prefix differs')
 for k,start in (('q',5),('v',5+n)):
  if not np.array_equal(np.array(tokens[start:start+n],float),np.fromstring(x[-1][k],sep=' ')):raise ValueError('checkpoint is not actual last accepted q/v')
 if min(float(z['minimum_gap']) for z in x)<-1e-10 or max(float(z['momentum_residual']) for z in x)>1e-17 or max(float(z['normal_velocity_residual']) for z in x)>1e-10:raise ValueError('accepted prefix physical gate fails')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');shutil.copytree(ref/'sources/models',out/'sources/models');sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()};result=dict(status='EXPERIMENTAL',scope='read-only MATCHED accepted prefix of FAILED pair ONLY;NOT completed horizon/time/grasp certification',actual_case=a.case,actual_summary_sha256=sha(src/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),reference_prefix_observed_sha256=sha(ref/'states.csv'),accepted_prefix_states=len(x),accepted_prefix_qv_time_exact=True,source_checkpoint_sha256=sha(checkpoint),checkpoint_step=a.checkpoint_step,actual_time_s=float(tokens[1]),source_hashes=sources,old_horizon_status='FAIL remains');write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'}))
if __name__=='__main__':main()
