"""Archived dense kernel at actual SOFA macro clocks;no physical mutation."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--actual-flags',action='store_true');p.add_argument('--formula-clock',action='store_true');p.add_argument('--accumulated-clock',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text());summary=json.loads((src/'summary.json').read_text());ref=ROOT/'results'/('autonomous_film_'+meta['reference'])
 if summary['status']!='PASS' or meta['steps']>64:raise ValueError('completed bounded actual source required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copy2(ref/'input.txt',out/'input.txt');cpp=archive/'diagnostics/film_coupled_reintegrated/CombinedReplay.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/CombinedReplay.cpp',cpp)
 for name,digest in meta['sources'].items():
  if name.endswith('.h') and sha(archive/name)!=digest:raise ValueError('actual archived header differs:'+name)
 stages=list(csv.DictReader((src/'coupled.stages.csv').open()));actual=list(csv.DictReader((src/'coupled.states.csv').open()));clocks=[]
 for i in range(meta['steps']):
  end=float(actual[i]['time']);start=meta['start_time'] if i==0 else float(actual[i-1]['time']);matches=[float(s['macro_start']) for s in stages if start-1e-13<=float(s['macro_start'])<end-1e-13]
  if not matches:raise ValueError('actual macro clock unobservable')
  clocks.append(min(matches))
 actualClocks=clocks.copy();formulaClocks=[meta['start_time']+i*(meta['duration']/meta['steps']) for i in range(meta['steps'])]
 if a.formula_clock and a.accumulated_clock:raise ValueError('clock protocols mutually exclusive')
 accumulated=[];t=meta['start_time']
 for _ in range(meta['steps']):accumulated.append(t);t+=meta['duration']/meta['steps']
 if a.formula_clock:clocks=formulaClocks
 if a.accumulated_clock:clocks=accumulated
 (out/'clocks.txt').write_text(str(meta['steps'])+' '+format(meta['duration']/meta['steps'],'.17g')+'\n'+'\n'.join(format(t,'.17g') for t in clocks)+'\n')
 flags=['-std=gnu++20','-DNDEBUG','-fPIC','-fstack-protector','--param=ssp-buffer-size=4','-D_FORTIFY_SOURCE=2'] if a.actual_flags else ['-std=c++17']
 binary=out/'reference';compile=guarded(['g++','-O2','-ffp-contract=off',*flags,'-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',out/'clocks.txt',out/'states.csv'],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='independent actual-clock archived-kernel replay;NOT loosening reference gate',case=a.case,actual_flags=a.actual_flags,compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_hashes={f:sha(out/f) for f in ('input.txt','clocks.txt')},sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 result.update(formula_clock=a.formula_clock,accumulated_clock=a.accumulated_clock,clock_source='independent start+=dt,NOT copied actual clocks' if a.accumulated_clock else 'time0+k*dt' if a.formula_clock else 'actual observed macro clocks',maximum_actual_formula_clock_difference=max(abs(x-y) for x,y in zip(actualClocks,formulaClocks)),maximum_actual_accumulated_clock_difference=max(abs(x-y) for x,y in zip(actualClocks,accumulated)))
 if run and run['exit_code']==0:
  replay=list(csv.DictReader((out/'states.csv').open()));keys=('local_displacement','local_velocity','body_center','body_velocity');errors={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,replay)) for k in keys};per_step=[max(abs(np.fromstring(x['local_velocity'],sep=' ')-np.fromstring(y['local_velocity'],sep=' '))) for x,y in zip(actual,replay)];result.update(status='PASS' if len(replay)==len(actual) and max(errors.values())<=1e-12 else 'FAIL',errors=errors,velocity_error_by_step=per_step,first_velocity_gate_failure=next((i+1 for i,e in enumerate(per_step) if e>1e-12),None),binary_sha256=sha(binary))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','errors','first_velocity_gate_failure')}))
if __name__=='__main__':main()
