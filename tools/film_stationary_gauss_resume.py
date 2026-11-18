"""Actual four-step vs2+2 typed Gauss continuation;strict state/stage identity."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
from film_gauss_newton_trace import temporal_arithmetic
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_lateral_gauss_parallel/FreeBlock.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;regrip_routed_checkpoint::read(argv[1],s,q,v,time,h);h=.00005;std::ifstream input(argv[1]);std::string magic,id;unsigned prior;double oldtime,oldh;input>>magic>>oldtime>>oldh>>prior>>id;std::ofstream out(argv[2]),stages(std::string(argv[2])+".stages.csv");out<<std::setprecision(17)<<"time,q,v\n";stages<<std::setprecision(17)<<"step,finger,stage,time,weight_s,force_N,local_q,local_v\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;for(unsigned k=0;k<std::stoul(argv[3]);++k){auto r=regrip_gauss_parallel::freeGaussParallel(s,q,v,time,h,c,3,[&](unsigned f,const auto&step,const auto&forces){double d=std::sqrt(3.)/6;for(unsigned j=0;j<2;++j){stages<<prior+k+1<<','<<f<<','<<j<<','<<time+h*(.5+(j?d:-d))<<','<<h/2;for(const auto*z:{&forces[j],&step.stageQ[j],&step.stageV[j]}){stages<<",\"";for(double x:*z)stages<<x<<' ';stages<<'\"';}stages<<'\n';}});time+=h;q=r.q;v=r.v;out<<time;for(const auto*z:{&q,&v}){out<<",\"";for(double x:*z)out<<x<<' ';out<<'\"';}out<<'\n';out.flush();}}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_stationary_parallel_actual1631';pm=json.loads((provider/'summary.json').read_text());fine=ROOT/'results/autonomous_film_20261119_gauss_parallel_fine1632';fm=json.loads((fine/'summary.json').read_text());origin=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';cp=origin/'three.checkpoint_250.txt'
 if pm['status']!='PASS' or fm['core_state_energy_work_time']!='PASS' or fm['input_checkpoint_sha256']!=sha(cp):raise ValueError('qualified same-IVP scheduling and local core time gates required;whole-energy FAIL retained')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_stationary_gauss_continuation',archive/'models/film_stationary_gauss_continuation');header=archive/'models/film_transmission/Gauss.h';header.write_text(temporal_arithmetic(header.read_text(),'both'));diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(fine/'sources/diagnostics/film_three_finger/FreeCheckpoint.h',diag/'FreeCheckpoint.h');cpp=diag/'GaussResume.cpp';cpp.write_text(CPP);helpers=archive/'tools';helpers.mkdir();shutil.copy2(ROOT/'tools/film_gauss_newton_trace.py',helpers/'film_gauss_newton_trace.py')
 r=dict(status='FAIL',scope='actual50us separated stationary four-step vs2+2 checkpoint identity ONLY;NOT whole time/energy/recovery/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_checkpoint_sha256=sha(cp),parallel_qualification_sha256=sha(provider/'summary.json'),local_time_summary_sha256=sha(fine/'summary.json'),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),legacy_sampled_work='NOT resumed;stage-consistent origin remains separate',root_work=None)
 rc=guarded(['g++','-O2','-std=c++17','-pthread','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120);rr=guarded([out/'reference',cp,out/'reference.csv','4'],out/'reference_process',480) if rc['exit_code']==0 else None;r.update(reference_compile=rc,reference_process=rr)
 if not rr or rr['exit_code']!=0:write_json(out/'summary.json',r);return
 build=ROOT/'build'/('stationary_gauss_resume_'+a.tag);build.mkdir(exist_ok=False);cfg=guarded(['cmake','-S',archive/'models/film_stationary_gauss_continuation','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if cfg['exit_code']==0 else None;r.update(configure=cfg,compile=compile)
 if not compile or compile['exit_code']!=0:write_json(out/'summary.json',r);return
 binary=build/'libReGripStationaryGaussContinuation.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
 if 'not found' in deps or any('libSofa.' in z and '=> /' in z and str(SDK) not in z for z in deps.splitlines()):raise ValueError('SDK ABI mismatch')
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};identity=hashlib.sha256(json.dumps(dict(source=sources,binary=sha(binary)),sort_keys=True).encode()).hexdigest();r.update(source_hashes=sources,binary_sha256=sha(binary),reference_binary_sha256=sha(out/'reference'),identity=identity,build_relative=str(build.relative_to(ROOT)))
 def execute(name,input_cp,steps,resume):
  folder=out/name;folder.mkdir();tokens=input_cp.read_text().split();tokens[4]=identity;(folder/'input.checkpoint').write_text(' '.join(tokens)+'\n');time=float(tokens[1]);finish=time
  for _ in range(steps):finish+=.00005
  tree=ET.parse(provider/'trial0/scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));scene.set('dt',tokens[2]);owner=scene.find('StationaryGaussParallelPilotODE');owner.tag='StationaryGaussContinuationODE';owner.attrib.pop('filmWorkers');owner.set('gaussResume','1' if resume else '0');owner.set('identity',identity);owner.set('checkpoint',str(folder/'input.checkpoint'));owner.set('endTime',format(finish,'.17g'))
  for node in scene.iter():
   for k,v in list(node.attrib.items()):
    if k=='pluginName' and v.endswith('/libReGripStationaryGaussParallelPilot.so'):
     if sha(v)!=pm['binary_sha256']:raise ValueError('qualified provider binary changed')
     node.set(k,str(binary))
    elif v.startswith(str(provider/'trial0')):node.set(k,str(folder)+v[len(str(provider/'trial0')):])
  tree.write(folder/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',folder/'scene.scn'],folder/'process',480);errors=sum((folder/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));record=dict(process=run,sofa_errors=errors,scene_sha256=sha(folder/'scene.scn'),input_checkpoint_sha256=sha(folder/'input.checkpoint'));r.setdefault('trials',{})[name]=record
  if run['exit_code'] or errors:return None
  record['raw_hashes']={f.name:sha(f) for f in folder.iterdir() if f.suffix in ('.txt','.csv')};return folder
 whole=execute('whole',cp,4,False)
 if whole:
  prefix=execute('prefix',cp,2,False)
  suffix=execute('suffix',prefix/'three.checkpoint_252.txt',2,True) if prefix else None
  if suffix:
   actual=list(csv.DictReader((whole/'three.states.csv').open()));expected=list(csv.DictReader((out/'reference.csv').open()));delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(actual,expected)) for k in ('q','v')};stages=list(csv.DictReader((whole/'three.gauss.stages.csv').open()))==list(csv.DictReader((out/'reference.csv.stages.csv').open()));split=list(csv.DictReader((prefix/'three.states.csv').open()))+list(csv.DictReader((suffix/'three.states.csv').open()));split_stages=list(csv.DictReader((prefix/'three.gauss.stages.csv').open()))+list(csv.DictReader((suffix/'three.gauss.stages.csv').open()));cp_exact=sha(whole/'three.checkpoint_254.txt')==sha(suffix/'three.checkpoint_254.txt');field_zero=all(float(z['T_per_rail'])==0 for f in range(3) for z in csv.DictReader((whole/f'film_{f}.csv').open()));r.update(reference_max_abs=delta,ALL_Gauss_stages_EXACT=stages,split_accepted_rows_EXACT=actual==split,split_Gauss_stages_EXACT=list(csv.DictReader((whole/'three.gauss.stages.csv').open()))==split_stages,final_checkpoint_BYTES_EXACT=cp_exact,actual_tension_zero=field_zero,status='PASS' if len(actual)==4 and len(expected)==4 and max(delta.values())<=1e-12 and stages and actual==split and list(csv.DictReader((whole/'three.gauss.stages.csv').open()))==split_stages and cp_exact and field_zero else 'FAIL')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','trials','compile','configure','reference_compile','reference_process')}))
if __name__=='__main__':main()
