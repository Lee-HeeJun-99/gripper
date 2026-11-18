"""Independent path chain-rule diagnostic,not a corrected trajectory or SOFA run."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text())
 # A failed parent may supply ONLY its individually committed prefix for diagnosis.
 # It never becomes a completed/passing parent experiment through this tool.
 for n,h in meta['raw_hashes'].items():
  if sha(src/n)!=h:raise ValueError('parent raw changed')
 states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));n=len(states)
 if len(rows)!=9*n or n==0:raise ValueError('incomplete prefix stage records')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/ConstraintPath.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/ConstraintPath.cpp',cpp);samples=[];weights={};owners=[];q_error=0
 for i in range(n):
  group=[rows[9*i+3*k:9*i+3*k+3] for k in range(3)];ids=[[(r['triangle'],r['feature']) for r in g] for g in group]
  if ids[0]!=ids[1] or ids[0]!=ids[2]:raise ValueError('feature transition:do not use a single smooth branch')
  owner=' '.join(t+' '+f for t,f in ids[0]);owners.append(ids[0]);q=[np.fromstring(g[0]['stage_q'],sep=' ') for g in group];v=[np.fromstring(g[0]['stage_v'],sep=' ') for g in group];h=float(group[-1][0]['time'])-float(group[0][0]['time']);q_error=max(q_error,float(np.max(abs(q[0]+h*(v[0]+4*v[1]+v[2])/6-q[-1]))))
  for k in range(3):samples.append((f'{i}_stage{k}',owner,q[k],v[k]))
  for order in (8,16):
   nodes,w=np.polynomial.legendre.leggauss(order);weights[i,order]=h*w/2
   for j,s in enumerate((nodes+1)/2):
    # v(s) is quadratic Lobatto interpolation;q(s) is its cubic integral.
    vv=(2*s*s-3*s+1)*v[0]+(4*s-4*s*s)*v[1]+(2*s*s-s)*v[2]
    qq=q[0]+h*((2*s**3/3-1.5*s*s+s)*v[0]+(2*s*s-4*s**3/3)*v[1]+(2*s**3/3-.5*s*s)*v[2]);samples.append((f'{i}_g{order}_{j}',owner,qq,vv))
 (out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(name+' '+owner+' '+' '.join(format(x,'.17g') for x in q)+' '+' '.join(format(x,'.17g') for x in v) for name,owner,q,v in samples)+'\n');binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'samples.txt',out/'observed.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent cubic numerical-path chain rule using actual accepted prefix;NOT continuous ODE solution/new SOFA success',parent_status=meta['status'],parent_summary_sha256=sha(src/'summary.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run,cubic_endpoint_q_error_mm=q_error)
 if run and run['exit_code']==0:
  obs={r['sample']:r for r in csv.DictReader((out/'observed.csv').open())};records=[]
  for i in range(n):
   h=float(rows[9*i+6]['time'])-float(rows[9*i]['time'])
   for f in range(3):
    delta=float(obs[f'{i}_stage2'][f'gap{f}'])-float(obs[f'{i}_stage0'][f'gap{f}']);simpson=h*sum(w*float(obs[f'{i}_stage{k}'][f'rate{f}']) for k,w in enumerate((1/6,2/3,1/6)));integrals={order:sum(float(w)*float(obs[f'{i}_g{order}_{j}'][f'rate{f}']) for j,w in enumerate(weights[i,order])) for order in (8,16)};records.append(dict(time=rows[9*i+6]['time'],finger=f,gap_change_mm=delta,collocation_normal_integral_mm=simpson,gauss8_integral_mm=integrals[8],gauss16_integral_mm=integrals[16],chain_rule_abs_error_mm=abs(delta-integrals[16]),collocation_defect_mm=delta-simpson))
  with (out/'defects.csv').open('w') as stream:w=csv.DictWriter(stream,fieldnames=records[0]);w.writeheader();w.writerows(records)
  error=max(r['chain_rule_abs_error_mm'] for r in records);result.update(status='PASS' if error<1e-12 and q_error<1e-12 else 'FAIL',accepted_prefix_steps=n,owned_features_constant=len(set(str(x) for x in owners))==1,max_chain_rule_error_mm=error,max_collocation_defect_mm=max(abs(r['collocation_defect_mm']) for r in records),sum_collocation_defect_finger0_mm=sum(r['collocation_defect_mm'] for r in records if r['finger']==0),max_gauss8_16_difference_mm=max(abs(r['gauss8_integral_mm']-r['gauss16_integral_mm']) for r in records),binary_sha256=sha(binary),observed_sha256=sha(out/'observed.csv'))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
