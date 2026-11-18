"""NEW stationary free sphere / zero external force C2 closing IVP.

Not a modified checkpoint or a continuation of the incoming-sphere experiment.
The separate owner rejects first contact until its event path is qualified.
"""
import argparse,csv,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(1,8,50),default=8);p.add_argument('--reuse');p.add_argument('--reuse-module');a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_lateral_release_actual1522';m=json.loads((parent/'summary.json').read_text())
 if m['status']!='PASS' or sha(parent/'scene.scn')!=m['scene_sha256']:raise ValueError('qualified actual mechanical scene required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('actual physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources'
 if a.reuse:shutil.copytree(ROOT/'results'/('autonomous_film_'+a.reuse)/'sources/models',archive/'models')
 else:
  shutil.copytree(parent/'sources/models',archive/'models')
  for folder in ('film_lateral_release','film_lateral_rest_closing'):shutil.copytree(ROOT/'models'/folder,archive/'models'/folder,dirs_exist_ok=True)
 diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);cpp=diag/'RestClosing.cpp';cpp.write_text('''#include "../../models/film_three_finger/SharedFilmSystem.h"
#include "../../models/film_three_finger_event/BlockFree.h"
#include <fstream>
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{
 using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());q(3*s.shared.nf+2)+=.0001;std::ifstream mass(argv[3]);s.shared.M.setZero();for(unsigned f=0;f<3;++f){auto&m=s.shared.films[f].film;for(unsigned i=0;i<m.model.size();++i){double x;mass>>x;if(!(x>0))throw std::runtime_error("positive public mass required");m.mass[i]=x;for(unsigned d=0;d<3;++d){unsigned a=3*i+d;int k=m.index[a];if(k>=0)s.shared.M(f*s.shared.nf+k,f*s.shared.nf+k)+=x*m.weight[a]*m.weight[a];}}}unsigned b=3*s.shared.nf;for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)mass>>s.shared.M(b+i,b+j);std::string extra;if(!mass||mass>>extra)throw std::runtime_error("exact public mass payload required");double t=0,h=.0002;std::ofstream out(argv[1]);out<<std::setprecision(17)<<"time,T_end,q,v\\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
 for(unsigned k=0;k<std::stoul(argv[2]);++k){auto r=regrip_three_event::freeMidpoint(s,q,v,t,h,c);q=r.q;v=r.v;t+=h;out<<t<<','<<c.sample(t).tension;for(const auto*z:{&q,&v}){out<<",\\\"";for(double x:*z)out<<x<<' ';out<<'\\\"';}out<<'\\n';}out.flush();
 }catch(const std::exception&e){std::cerr<<e.what()<<'\\n';return 1;}}
''');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};forecast=None;build=ROOT/'build'/('lateral_rest_'+a.tag)
 if a.reuse:
  old=ROOT/'results'/('autonomous_film_'+a.reuse);proof=json.loads((old/'summary.json').read_text());build=ROOT/proof['build_relative']
  if proof['status']!='PASS' or proof['source_hashes']!=sources or sha(build/'libReGripLateralRestClosing.so')!=proof['binary_sha256'] or sha(old/'reference')!=proof['reference_binary_sha256']:raise ValueError('exact compiled NEW fixture required')
  forecast=2*max(proof['process']['runtime_s'],proof['reference_process']['runtime_s'])*a.steps/proof['actual_steps']+30;shutil.copy2(old/'reference',out/'reference');configure=compile=rc=dict(exit_code=0,reused_from=a.reuse)
 elif a.reuse_module:
  old=ROOT/'results'/('autonomous_film_'+a.reuse_module);proof=json.loads((old/'summary.json').read_text());build=ROOT/proof['build_relative']
  if a.steps>8 or proof['status']!='FAIL' or proof['compile']['exit_code']!=0 or proof['reference_compile']['exit_code']==0 or 'process' in proof:raise ValueError('only compiled-module/reference-compile failure may supply unqualified module')
  for f,d in proof['source_hashes'].items():
   if sha(old/'sources'/f)!=d:raise ValueError('prior compile source changed')
  if {f:d for f,d in sources.items() if f.startswith('models/')}!={f:d for f,d in proof['source_hashes'].items() if f.startswith('models/')}:raise ValueError('ALL module physical/header/build sources must be EXACT')
  configure=compile=dict(exit_code=0,reused_compiled_module_from=a.reuse_module,qualification='UNQUALIFIED until actual API test',binary_sha256=sha(build/'libReGripLateralRestClosing.so'));rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 else:
  if a.steps>8:raise ValueError('measure bounded8-step actual cost before50-step closing')
  build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',archive/'models/film_lateral_rest_closing','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None;rc=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'reference_compile',120)
 r=dict(status='FAIL',scope='NEW actual stationary free sphere/C2 closing;NO incoming speed/external force/gravity;NOT wrapping/holding/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,source_scene_sha256=m['scene_sha256'],configure=configure,compile=compile,reference_compile=rc,build_relative=str(build.relative_to(ROOT)),actual_steps=a.steps,dt_s=.0002,predicted_child_runtime_s=forecast,sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),physical_input=dict(initial_body_velocity=[0]*6,external_force_N=[0]*3,gravity=[0]*3,initial_extra_gap_mm=.0001,Tmax_N_per_rail=.0001,C2_rise_s=.01,C2_release_s=[.02,.03]),root_work=None,contact_area=None,pressure=None,holding_capacity=None,time_convergence='NOT RUN')
 if forecast and forecast>480:r.update(status='BLOCKED',failure_reason='measured child forecast>480s;NOT OS exhaustion');write_json(out/'summary.json',r);return
 if compile and compile['exit_code']==0 and rc['exit_code']==0:
  binary=build/'libReGripLateralRestClosing.so';deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  cp=parent/'three.checkpoint_136.txt'
  if sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('immutable actual public mass source changed')
  tokens=cp.read_text().split();offset=5+2*1953+4;massfile=out/'public_mass.txt';massfile.write_text(' '.join(tokens[offset:offset+729])+'\n');r['public_mass_source_checkpoint_sha256']=sha(cp);r['public_mass_sha256']=sha(massfile)
  identity=hashlib.sha256(json.dumps(dict(sources=sources,binary=sha(binary)),sort_keys=True).encode()).hexdigest();ref=guarded([out/'reference',out/'reference.csv',str(a.steps),massfile],out/'reference_process',480);r['reference_process']=ref
  if ref['exit_code']==0:
   end=0.
   for _ in range(a.steps):end+=.0002
   tree=ET.parse(parent/'scene.scn');scene=tree.getroot();scene.set('time','0');owner=scene.find('LateralReleaseODE');owner.tag='LateralRestClosingODE';owner.set('checkpoint','');owner.set('externalForce','0 0 0');owner.set('identity',identity);owner.set('endTime',format(end,'.17g'));body=scene.find('./Node[@name="free_object"]/MechanicalObject');body.set('velocity','0 0 0 0 0 0')
   for node in scene.iter():
    if node.tag=='RequiredPlugin' and node.get('pluginName','').endswith('/libReGripLateralRelease.so'):node.set('pluginName',str(binary))
    for k,v in list(node.attrib.items()):
     if k in ('filename','displacementFilename','publicMassFilename') and v.startswith(str(parent)):node.set(k,str(out)+v[len(str(parent)):])
   tree.write(out/'scene.scn');r.update(binary_sha256=sha(binary),reference_binary_sha256=sha(out/'reference'),identity=identity,scene_sha256=sha(out/'scene.scn'));run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
   if run['exit_code']==0 and not errors:
    rows=list(csv.DictReader((out/'three.states.csv').open()));expected=list(csv.DictReader((out/'reference.csv').open()));delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,expected)) for k in ('q','v')};exact=len(rows)==len(expected)==a.steps and all(x['time']==y['time'] for x,y in zip(rows,expected));fields=[list(csv.DictReader((out/f'film_{f}.csv').open())) for f in range(3)];terror=max(abs(float(x['T_per_rail'])-float(y['T_end'])) for ff in fields for x,y in zip(ff,expected));gap=min(float(x['minimum_gap']) for x in rows);mom=max(float(x['momentum_residual']) for x in rows);r.update(status='PASS' if exact and max(delta.values())<=1e-12 and terror==0 and gap>=-1e-10 and mom<=1e-17 else 'FAIL',reference_max_abs=delta,accumulated_clock_exact=exact,actual_control_error_N=terror,minimum_whole_stage_gap_mm=gap,momentum_residual_Ns=mom,end_time_s=end,actual_contact='NONE on committed stages;first birth rejects commit')
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','configure','compile','reference_compile','reference_process','process')}))
if __name__=='__main__':main()
