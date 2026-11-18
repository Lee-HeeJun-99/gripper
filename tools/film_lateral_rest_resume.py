"""Typed stationary-origin continuation; zero external load, not incoming IVP."""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--parent',default='20261119_lateral_stationary_peak_public1541');p.add_argument('--checkpoint-step',type=int,default=50);p.add_argument('--steps',type=int,choices=(1,8,32),default=1);p.add_argument('--reuse-build');p.add_argument('--compare');a=p.parse_args();parent=ROOT/'results'/('autonomous_film_'+a.parent);m=json.loads((parent/'summary.json').read_text());cp=parent/f'three.checkpoint_{a.checkpoint_step}.txt'
 if m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors'] or sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('complete qualified actual stationary-origin checkpoint required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('actual source archive changed')
 tokens=cp.read_text().split();time,h=float(tokens[1]),float(tokens[2]);end=time
 if tokens[0]!='REGRIP_LATERAL_REST_FREE_V1' or tokens[4]!=m['identity'] or h!=.0002:raise ValueError('typed stationary-origin clock required')
 for _ in range(a.steps):end+=h
 if end>.05:raise ValueError('explicit50ms physical horizon')
 forecast=2*m['process']['runtime_s']*a.steps/m['actual_steps']+30
 if a.steps>1 and not a.reuse_build:raise ValueError('initial new owner must be profiled with one step')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 if a.reuse_build:shutil.copytree(ROOT/'results'/('autonomous_film_'+a.reuse_build)/'sources/models',archive/'models')
 else:
  shutil.copytree(parent/'sources/models',archive/'models')
  for folder in ('film_lateral_release','film_lateral_rest_closing','film_lateral_rest_resume'):shutil.copytree(ROOT/'models'/folder,archive/'models'/folder,dirs_exist_ok=True)
 diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);loader=(ROOT/'diagnostics/film_three_finger/RoutedCheckpoint.h').read_text().replace('REGRIP_ROUTED_PERSISTENT_V1','REGRIP_LATERAL_REST_FREE_V1').replace('time<.03','time<=.05');i=loader.index(' for(unsigned f=0;f<3;++f){unsigned triangle,feature;');loader=loader[:i]+''' std::string label,value;unsigned active;double clock;in>>label>>active;if(label!="FREE_ACTIVE_COUNT"||active!=0)throw std::runtime_error("empty stationary-origin active set required");in>>label>>value;if(label!="INITIAL_CONDITION"||value!="STATIONARY_SEPARATED")throw std::runtime_error("stationary origin required");in>>label>>clock;std::string extra;if(!in||label!="ACCUMULATED_TIME"||clock!=time||in>>extra||s.clearance(q)<=0)throw std::runtime_error("exact separated clock/footer required");
}
}
''';(diag/'RestCheckpoint.h').write_text(loader);cpp=diag/'RestResume.cpp';cpp.write_text('''#include "RestCheckpoint.h"
#include "../../models/film_three_finger_event/BlockFree.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double t,h;regrip_routed_checkpoint::read(argv[1],s,q,v,t,h);std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,T_end,q,v\\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;for(unsigned k=0;k<std::stoul(argv[3]);++k){auto r=regrip_three_event::freeMidpoint(s,q,v,t,h,c);q=r.q;v=r.v;t+=h;out<<t<<','<<c.sample(t).tension;for(const auto*z:{&q,&v}){out<<",\\\"";for(double x:*z)out<<x<<' ';out<<'\\\"';}out<<'\\n';}out.flush();}catch(const std::exception&e){std::cerr<<e.what()<<'\\n';return 1;}}
''');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('lateral_rest_resume_'+a.tag)
 if a.reuse_build:
  old=ROOT/'results'/('autonomous_film_'+a.reuse_build);proof=json.loads((old/'summary.json').read_text());build=ROOT/proof['build_relative']
  if proof['status']!='PASS' or proof['source_hashes']!=sources or sha(build/'libReGripLateralRestResume.so')!=proof['binary_sha256'] or sha(old/'reference')!=proof['reference_binary_sha256'] or sha(SDK/'bin/runSofa-26.06.00')!=proof['sdk_runner_sha256']:raise ValueError('EXACT compiled sources/binaries/SDK required')
  shutil.copy2(old/'reference',out/'reference');configure=compile=rc=dict(exit_code=0,reused_from=a.reuse_build)
 else:
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_lateral_rest_resume','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 r=dict(status='FAIL',scope='actual stationary-origin zero-load FREE continuation;first birth rejects;NOT incoming-object history or grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(cp),configure=configure,compile=compile,reference_compile=rc,build_relative=str(build.relative_to(ROOT)),actual_steps=a.steps,start_time_s=time,dt_s=h,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),external_force_N=[0]*3,gravity=[0]*3,root_work=None,time_convergence='NOT RUN',contact_area=None,pressure=None,holding_capacity=None)
 if forecast>480:r.update(status='BLOCKED',failure_reason='measured policy forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
 if compile and compile['exit_code']==0 and rc['exit_code']==0:
  binary=build/'libReGripLateralRestResume.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  identity=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary)),sort_keys=True).encode()).hexdigest();before=tokens.copy();tokens[4]=identity;(out/'input.checkpoint').write_text(' '.join(tokens)+'\n')
  if tokens[:4]+tokens[5:]!=before[:4]+before[5:]:raise ValueError('physical state changed')
  ref=guarded([out/'reference',out/'input.checkpoint',out/'reference.csv',str(a.steps)],out/'reference_process',480);r['reference_process']=ref
  if ref['exit_code']==0:
   tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time',format(time,'.17g'));owner=scene.find('LateralRestClosingODE')
   if owner is None:owner=scene.find('LateralRestResumeODE')
   if owner is None or owner.get('externalForce')!='0 0 0':raise ValueError('stationary-origin actual owner missing')
   owner.tag='LateralRestResumeODE';owner.set('checkpoint',str(out/'input.checkpoint'));owner.set('identity',identity);owner.set('endTime',format(end,'.17g'))
   for node in scene.iter():
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith(('/libReGripLateralRestClosing.so','/libReGripLateralRestResume.so')):
     if sha(node.get('pluginName'))!=m['binary_sha256']:raise ValueError('parent actual binary changed')
     node.set('pluginName',str(binary))
    for k,v in list(node.attrib.items()):
     if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
   tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),reference_binary_sha256=sha(out/'reference'),identity=identity,input_checkpoint_sha256=sha(out/'input.checkpoint'),scene_sha256=sha(out/'scene.scn'));run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
   if run['exit_code']==0 and not errors:
    rows=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((out/'reference.csv').open()));delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,expected)) for k in ('q','v')};exact=len(rows)==len(expected)==a.steps and all(x['time']==y['time'] for x,y in zip(rows,expected));fields=[list(csv.DictReader((out/f'film_{f}.csv').open())) for f in range(3)];T=max(abs(float(x['T_per_rail'])-float(y['T_end'])) for ff in fields for x,y in zip(ff,expected));gap=min(float(x['minimum_gap']) for x in rows);mom=max(float(x['momentum_residual']) for x in rows);r.update(status='PASS' if exact and max(delta.values())<=1e-12 and T==0 and gap>=-1e-10 and mom<=1e-17 else 'FAIL',reference_max_abs=delta,accumulated_clock_exact=exact,actual_control_error_N=T,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=mom,end_time_s=end)
    if a.compare:
     other=ROOT/'results'/('autonomous_film_'+a.compare);om=json.loads((other/'summary.json').read_text())
     if om['status']!='PASS' or om['binary_sha256']!=sha(binary) or any(sha(other/f)!=d for f,d in om['raw_hashes'].items()):raise ValueError('qualified actual suffix required')
     old={x['time']:x for x in csv.DictReader((other/'three.states.csv').open())};diff={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(old[x['time']][k],sep=' ')))) for x in rows) for k in ('q','v')};stages={(x['macro'],x['kind'],x['time']):x for x in csv.DictReader((other/'three.free.stages.csv').open())};stage_exact=all(stages.get((x['macro'],x['kind'],x['time']))==x for x in csv.DictReader((out/'three.free.stages.csv').open()));cp_exact=all((other/f.name).exists() and f.read_text().split()==(other/f.name).read_text().split() for f in out.glob('three.checkpoint_*.txt'));r.update(suffix_max_abs=diff,all_free_stages_exact=stage_exact,full_checkpoint_tokens_exact=cp_exact)
     if max(diff.values())>1e-12 or not stage_exact or not cp_exact:r['status']='FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','configure','compile','reference_compile','reference_process','process')}))
if __name__=='__main__':main()
