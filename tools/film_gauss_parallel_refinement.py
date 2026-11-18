"""Bounded fine-step window from actual50ms; exact parallel separated films."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_gauss_recovery_window import CPP
from film_gauss_newton_trace import temporal_arithmetic
from film_transmission_linear import mapping,shape

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--macros',type=int,choices=(2,8),default=2);p.add_argument('--profile');a=p.parse_args()
 provider=ROOT/'results/autonomous_film_20261119_stationary_parallel_actual1631';pm=json.loads((provider/'summary.json').read_text());fine=ROOT/'results/autonomous_film_20261119_gauss_fine_window1629';fm=json.loads((fine/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';cp=actual/'three.checkpoint_250.txt'
 if pm['status']!='PASS' or sha(cp)!=fm['input_checkpoint_sha256']:raise ValueError('same actual seed and exact parallel actual qualification required')
 forecast=2*fm['process']['runtime_s'] if a.macros==2 else None
 if a.macros==8:
  if not a.profile:raise ValueError('measured two-macro profile required before long window')
  pr=ROOT/'results'/('autonomous_film_'+a.profile);profile=json.loads((pr/'summary.json').read_text())
  if profile.get('completed_macros')!=2 or profile['input_checkpoint_sha256']!=sha(cp):raise ValueError('completed same-model profile required')
  forecast=profile['process']['runtime_s']*4*1.25+15
 if forecast>480:raise ValueError('policy forecast>480;NOT OS exhaustion')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('frozen parallel source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');header=archive/'models/film_transmission/Gauss.h';header.write_text(temporal_arithmetic(header.read_text(),'both'));helpers=archive/'tools';helpers.mkdir();shutil.copy2(ROOT/'tools/film_gauss_newton_trace.py',helpers/'film_gauss_newton_trace.py');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(fine/'sources/diagnostics/film_three_finger/FreeCheckpoint.h',diag/'FreeCheckpoint.h')
 code=CPP.replace('../../models/film_lateral_gauss/FreeBlock.h','../../models/film_lateral_gauss_parallel/FreeBlock.h').replace('{1u,2u,4u}','{16u,32u,64u}').replace('macro<8','macro<'+str(a.macros)).replace('regrip_three_event::freeGauss(s,q,v,time,h,c,','regrip_gauss_parallel::freeGaussParallel(s,q,v,time,h,c,3,');cpp=diag/'FineParallel.cpp';cpp.write_text(code);shutil.copy2(cp,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-pthread','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',cp,out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None
 r=dict(status='FAIL',scope='independent same-IVP cumulative50/25/12.5us Gauss with unchanged1e-18 Newton and0.1% time gates;NOT actual long SOFA or grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_checkpoint_sha256=sha(cp),parallel_qualification_sha256=sha(provider/'summary.json'),arithmetic='both;temporal sums only;AD2/material unchanged',workers=3,root_work=None,heat='NOT assigned',predicted_child_runtime_s=forecast,compile=compile,process=run,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'states.csv').open()));by={(x['substeps'],int(x['macro'])):x for x in rows};P=mapping();pairs={};defects={}
  for macro in range(1,a.macros+1):
   for l,h in (('16','32'),('32','64'),('16','64')):
    x,y=by[l,macro],by[h,macro]
    if x['time']!=y['time']:raise ValueError('common accumulated clock mismatch')
    quantities={k:(np.array([float(x[k])]),np.array([float(y[k])])) for k in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation','damping_work_Nmm','signed_partial_defect_Nmm')}
    for k in ('q','v'):quantities['all_film_'+k]=(np.fromstring(x[k],sep=' ')[:1947],np.fromstring(y[k],sep=' ')[:1947])
    qx,qy=np.fromstring(x['q'],sep=' '),np.fromstring(y['q'],sep=' ')
    for f in range(3):
     sx,sy=shape(P@qx[649*f:649*(f+1)]),shape(P@qy[649*f:649*(f+1)])
     for k in sx:quantities[f'finger{f}_'+k]=(np.array([sx[k]]),np.array([sy[k]]))
    pair={}
    for k,(u,v) in quantities.items():
     absolute=float(np.linalg.norm(u-v));scale=float(max(np.linalg.norm(u),np.linalg.norm(v)));relative=absolute/scale if scale else 0.;pair[k]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
    label=f'macro{macro}_{l}_{h}';defects[label]=pair.pop('signed_partial_defect_Nmm');pairs[label]=pair
  core=all(z['status']=='PASS' for pair in pairs.values() for z in pair.values());defect=all(z['status']=='PASS' for z in defects.values());r.update(status='PASS' if core and defect else 'FAIL',completed_macros=a.macros,core_state_energy_work_time='PASS' if core else 'FAIL',signed_partial_defect_relative_time='PASS' if defect else 'FAIL',time_pairs=pairs,signed_defect_pairs=defects,binary_sha256=sha(out/'reference'))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','time_pairs','signed_defect_pairs','compile','process')}))
if __name__=='__main__':main()
