"""Reuse qualified actual Gauss binary for a bounded typed FREE window."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_stationary_gauss_resume import CPP
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--provider',required=True);p.add_argument('--parent',required=True);p.add_argument('--checkpoint-step',type=int,required=True);p.add_argument('--steps',type=int,choices=(4,8,16,28,32),default=16);p.add_argument('--reuse-reference');a=p.parse_args();provider=ROOT/'results'/('autonomous_film_'+a.provider);pm=json.loads((provider/'summary.json').read_text());parent=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((parent/'summary.json').read_text());folder=parent/'whole' if a.parent==a.provider else parent;cp=folder/('three.checkpoint_'+str(a.checkpoint_step)+'.txt');qualification=ROOT/'results/autonomous_film_20261119_gauss_parallel_full1634';qm=json.loads((qualification/'summary.json').read_text())
 if pm['status']!='PASS' or m['status']!='PASS' or qm['core_state_energy_work_time']!='PASS':raise ValueError('actual resume and independent cumulative core time qualification required;energy FAIL retained')
 raw=pm['trials']['whole']['raw_hashes'] if a.parent==a.provider else m['raw_hashes']
 if sha(cp)!=raw[cp.name]:raise ValueError('qualified actual checkpoint changed')
 tokens=cp.read_text().split();time=float(tokens[1]);h=float(tokens[2]);finish=time
 for _ in range(a.steps):finish+=h
 if tokens[0]!='REGRIP_STATIONARY_GAUSS_FREE_V1' or tokens[4]!=pm['identity'] or h!=.00005 or finish>.0564:raise ValueError('typed same-binary checkpoint/time domain required')
 binary=ROOT/pm['build_relative']/'libReGripStationaryGaussContinuation.so'
 if sha(binary)!=pm['binary_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=pm['sdk_runner_sha256']:raise ValueError('qualified binary/SDK changed')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('frozen compiled source changed')
 profile=max(pm['trials']['whole']['process']['runtime_s']/4,pm['reference_process']['runtime_s']/4);forecast=profile*a.steps*2+20
 if forecast>480:raise ValueError('profile forecast>480;NOT OS exhaustion')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources',archive);reader=archive/'diagnostics/film_three_finger/FreeCheckpoint.h';text=reader.read_text();anchor='if(magic!="REGRIP_STATIONARY_FREE_V1"||token.size()!=64||h!=.0002||!(time>0&&time<.05))'
 if text.count(anchor)!=1:raise ValueError('exact old diagnostic reader anchor required')
 text=text.replace('#include "../../models/film_stationary_release/FreeFooter.h"','#include "../../models/film_stationary_gauss_continuation/GaussFooter.h"').replace(anchor,'if(magic!="REGRIP_STATIONARY_GAUSS_FREE_V1"||token.size()!=64||h!=.00005||!(time>=.05&&time<.0564))').replace('regrip_stationary_release::readFreeFooter(in,time);','regrip_stationary_gauss::readFooter(in,time);');reader.write_text(text);cpp=archive/'diagnostics/film_three_finger/GaussWindowActual.cpp';cpp.write_text(CPP);shutil.copy2(cp,out/'input.checkpoint')
 if a.reuse_reference:
  reuse=ROOT/'results'/('autonomous_film_'+a.reuse_reference);rm=json.loads((reuse/'summary.json').read_text());sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
  if rm['status']!='PASS' or sources!=rm['source_hashes'] or sha(reuse/'reference')!=rm['reference_binary_sha256']:raise ValueError('ALL reference sources and qualified binary must match exactly')
  shutil.copy2(reuse/'reference',out/'reference');rc=dict(exit_code=0,reused_summary_sha256=sha(reuse/'summary.json'),ALL_source_hashes_EXACT=True)
 else:rc=guarded(['g++','-O2','-std=c++17','-pthread','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 rr=guarded([out/'reference',cp,out/'reference.csv',str(a.steps)],out/'reference_process',480) if rc['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual bounded50us separated stationary Gauss continuation ONLY;NOT full energy/time/recovery/grasp',provider_summary_sha256=sha(provider/'summary.json'),parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(cp),input_checkpoint_sha256=sha(out/'input.checkpoint'),source_commit=pm['source_commit'],binary_sha256=sha(binary),build_relative=pm['build_relative'],identity=pm['identity'],sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compiled_plugin_source_hashes=pm['source_hashes'],reference_compile=rc,reference_process=rr,predicted_child_runtime_s=forecast,root_work=None,legacy_sampled_work='NOT resumed;do not splice legacy cumulative work')
 if rr and rr['exit_code']==0:
  tree=ET.parse(provider/'whole/scene.scn');scene=tree.getroot();scene.set('time',tokens[1]);scene.set('dt',tokens[2]);owner=scene.find('StationaryGaussContinuationODE');owner.set('gaussResume','1');owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('endTime',format(finish,'.17g'))
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if v.startswith(str(provider/'whole')):node.set(k,str(out)+v[len(str(provider/'whole')):])
  tree.write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and errors==0:
   actual=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((out/'reference.csv').open()));delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};stages=list(csv.DictReader((out/'three.gauss.stages.csv').open()))==list(csv.DictReader((out/'reference.csv.stages.csv').open()));clocks=[x['time'] for x in actual]==[x['time'] for x in expected];zero=all(float(z['T_per_rail'])==0 for f in range(3) for z in csv.DictReader((out/f'film_{f}.csv').open()));r.update(status='PASS' if len(actual)==len(expected)==a.steps and max(delta.values())<=1e-12 and stages and clocks and zero and max(float(x['momentum_residual']) for x in actual)<=1e-17 else 'FAIL',reference_max_abs=delta,ALL_Gauss_stages_EXACT=stages,accumulated_clocks_EXACT=clocks,actual_tension_zero=zero,end_time_s=float(actual[-1]['time']),completed_steps=len(actual),minimum_numerical_path_gap_bound_mm=min(float(x['numerical_path_gap_lower_bound_mm']) for x in csv.DictReader((out/'three.gauss.clearance.csv').open())))
 r['reference_binary_sha256']=sha(out/'reference') if (out/'reference').exists() else None
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compiled_plugin_source_hashes','raw_hashes','reference_compile','reference_process','process')}))
if __name__=='__main__':main()
