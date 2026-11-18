"""Strict actual edge resume vs completed existing reference,exact clock bridge."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference-offset',type=int,default=0);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);ref=ROOT/'results/autonomous_film_20261118_routed_edge_reference1339';m=json.loads((src/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_routed_edge_actual1336';pm=json.loads((provider/'summary.json').read_text())
 if m['status']!='EXPERIMENTAL' or m['process']['exit_code'] or m['sofa_errors'] or r['status']!='PASS' or m['binary_sha256']!=pm['binary_sha256']:raise ValueError('complete actual edge continuation and completed reference required')
 for path,meta in ((src,m),(ref,r)):
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('actual/reference evidence changed')
 for f,d in pm['source_hashes'].items():
  if r['source_hashes'].get(f)!=d:raise ValueError('actual/reference physical model differs')
 actual=list(csv.DictReader((src/'three.states.csv').open()));reference=list(csv.DictReader((ref/'states.csv').open()));x=(src/'input.checkpoint').read_text().split();y=(ref/'input.checkpoint').read_text().split();offset=a.reference_offset;count=len(actual);n=1953
 if offset<0 or len(reference)<offset+count or count!=m['actual_steps']:raise ValueError('complete exact reference slice absent')
 if offset==0:
  if m['input_checkpoint_sha256']!=r['input_checkpoint_sha256']:raise ValueError('identical physical initial checkpoint required')
 else:
  before=reference[offset-1]
  if float(x[1])!=float(before['time']) or any(not np.array_equal(np.array(x[start:start+n],float),np.fromstring(before[k],sep=' ')) for k,start in (('q',5),('v',5+n))):raise ValueError('EXACT physical q/v/clock bridge absent')
  start=5+2*n;end=start+4+693+36+3*1386
  if x[start:end]!=y[start:end]:raise ValueError('public quaternion/mass/root map changed')
  for f in range(3):
   s=end+1+10*f
   if x[s:s+6]!=y[s:s+6]:raise ValueError('edge identity/topology/birth lifetime changed')
 expected=reference[offset:offset+count];api={k:max(float(np.max(abs(np.fromstring(i[k],sep=' ')-np.fromstring(j[k],sep=' ')))) for i,j in zip(actual,expected)) for k in ('q','v')};clock=all(i['time']==j['time'] for i,j in zip(actual,expected));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];stages=list(csv.DictReader((src/'three.primitive.stages.csv').open()));masspos=5+2*n+4+693;Mb=np.array(x[masspos:masspos+36],float).reshape(6,6);energy=force=control=0.
 if len(stages)!=9*count:raise ValueError('all actual edge stage rows required')
 for i,rr in enumerate(expected):
  v=np.fromstring(actual[i]['v'],sep=' ');K=sum(float(f[i]['K']) for f in fields)+.5*v[-6:]@Mb@v[-6:];energy=max(energy,abs(K-float(rr['K'])),abs(sum(float(f[i]['U_shell']) for f in fields)-float(rr['U_shell'])),abs(sum(float(f[i]['U_attachment']) for f in fields)-float(rr['U_attachment'])));force=max(force,float(np.max(abs(np.array([float(z['force']) for z in stages[9*i+6:9*i+9]])-np.fromstring(rr['force'],sep=' ')))));control=max(control,max(abs(float(f[i]['T_per_rail'])-float(rr['T'])) for f in fields))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(api.values())<1e-12 and clock and energy<1e-12 and force<1e-12 and control==0 else 'FAIL',scope='finite actual routed material-edge q/v/clock/force/energy API consistency ONLY;NOT time convergence/full Unload/release/grasp',actual_summary_sha256=sha(src/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),reference_offset=offset,exact_physical_bridge=True,reference_max_abs=api,accumulated_clock_exact=clock,energy_max_abs_Nmm=energy,force_max_abs_N=force,control_max_abs_N=control,api_gate=1e-12,root_reaction_work=None,full_time_gate='FAIL remains');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
