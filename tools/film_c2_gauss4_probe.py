"""Separate nonlinear Gauss4 kernel unit/FD and conditional first-FEM-step probe."""
import argparse,csv,importlib.util,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
CPP=r'''#include "../../models/film_c2_startup/Gauss4.h"
#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_lateral_tendon/Step.h"
#include <iostream>
#include <fstream>
#include <iomanip>
struct F{Eigen::VectorXd force;Eigen::MatrixXd stiffness;};
int main(int argc,char**argv){try{using namespace regrip_transmission;std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time,momentum_sum_Ns,tangent_FD,evaluations,q,v\n";
 if(std::string(argv[1])=="toy"){Eigen::MatrixXd M=Eigen::MatrixXd::Identity(2,2),K(2,2);K<<1,-1,-1,1;Eigen::VectorXd zero=Eigen::VectorXd::Zero(2);auto force=[&](const Eigen::VectorXd&q,double t){Eigen::VectorXd f=-K*q;f(0)+=t*t*t;return F{f,K};};auto a=regrip_c2_startup::gauss4(M,zero,zero,0,.001,force,false),b=regrip_c2_startup::gauss4(M,zero,zero,0,.001,force,true);if(a.q!=b.q||a.v!=b.v||a.stageQ!=b.stageQ||a.stageV!=b.stageV)throw std::runtime_error("FD queries changed accepted toy state");out<<.001<<','<<a.residual<<','<<b.tangentError<<','<<b.evaluations;for(const auto*z:{&b.q,&b.v}){out<<",\"";for(double x:*z)out<<x<<' ';out<<'\"';}out<<'\n';return 0;}
 auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[2]);std::vector<Point>q(m.size()),v(m.size());double finish=std::stod(argv[4]),clock=0,momentum=0,error=0;unsigned substeps=std::stoul(argv[5]),evaluations=0;bool fd=argc>6&&std::string(argv[6])=="fd";auto c=control();std::ofstream stages(std::string(argv[3])+".stages.csv");stages<<std::setprecision(17)<<"micro,stage,time,weight_s,T,q,v,reduced_physical_force_N\n";
 for(unsigned k=0;k<substeps;++k){double h=k+1==substeps?finish-clock:finish/substeps;auto map=mechanics(m,q,v,h,0,mass);auto r=regrip_c2_startup::gauss4(filmMass(map),map.pack(q),map.pack(v),clock,h,[&](const Eigen::VectorXd&x,double t){return regrip_lateral_tendon::parts(map,map.expand(x),c.sample(t).tension,6.);},fd&&k==0);momentum+=r.residual;error=std::max(error,r.tangentError);evaluations+=r.evaluations;for(unsigned j=0;j<4;++j){double t=clock+h*regrip_c2_startup::c[j];stages<<k<<','<<j<<','<<t<<','<<h*regrip_c2_startup::b[j]<<','<<c.sample(t).tension;quote(stages,map.expand(r.stageQ[j]));quote(stages,map.expand(r.stageV[j]));stages<<",\"";for(double x:r.internalForce[j])stages<<x<<' ';stages<<"\"\n";}clock+=h;q=map.expand(r.q);v=map.expand(r.v);}
 if(clock!=finish||momentum>1e-17)throw std::runtime_error("strict clock/momentum gate fails");out<<clock<<','<<momentum<<','<<error<<','<<evaluations;quote(out,q);quote(out,v);out<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
# Diagnostic-only trace adapter: no extra force queries or physical changes.
_old_fd='bool fd=argc>6&&std::string(argv[6])=="fd";'
if CPP.count(_old_fd)!=1:raise ValueError('exact diagnostic CLI adapter required')
CPP=CPP.replace(_old_fd,'bool fd=argc>7&&std::string(argv[7])=="fd";double tolerance=argc>6?std::stod(argv[6]):1e-18;')
CPP=CPP.replace('for(unsigned k=0;k<substeps;++k){','std::ofstream trace(std::string(argv[3])+".newton.csv");trace<<std::setprecision(17)<<"micro,start_time,h_s,tolerance_Ns,nonlinear_residual_Ns,iterations,Skin_stage_residual_Ns,Rail_stage_residual_Ns,force_queries_including_FD\\n";for(unsigned k=0;k<substeps;++k){')
CPP=CPP.replace('},fd&&k==0);momentum+=r.residual;','},fd&&k==0,tolerance);double skin2=0,rail2=0;if(map.freeSize!=649)throw std::runtime_error("explicit21-row trace partition required");for(unsigned j=0;j<4;++j){skin2+=r.finalStageResidual.segment(j*649,295).squaredNorm();rail2+=r.finalStageResidual.segment(j*649+295,354).squaredNorm();}trace<<k<<\',\'<<clock<<\',\'<<h<<\',\'<<tolerance<<\',\'<<r.nonlinearResidual<<\',\'<<r.iterations<<\',\'<<std::sqrt(skin2)<<\',\'<<std::sqrt(rail2)<<\',\'<<r.evaluations<<\'\\n\';trace.flush();momentum+=r.residual;')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--precise-attachment',action='store_true');p.add_argument('--substeps',type=int,choices=(8,16,32),default=8);p.add_argument('--reuse');p.add_argument('--newton-tol',type=float,choices=(1e-18,1e-20,1e-22,1e-24),default=1e-18);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_rail_aspect_api1654';pm=json.loads((provider/'summary.json').read_text());reference=ROOT/'results/autonomous_film_20261119_c2_frozen_startup1666';rm=json.loads((reference/'summary.json').read_text());table=ROOT/'results/autonomous_film_20261119_c2_transmission_startup1663';mass_provider=ROOT/'results/autonomous_film_20261119_rail_aspect_peak1652';mass=mass_provider/'public_mass.txt'
 if sha(mass)!=json.loads((mass_provider/'summary.json').read_text())['public_mass_sha256']:raise ValueError('qualified actual public mass changed')
 if pm['status']!='PASS' or rm['reference_flow_split_gate']!='PASS' or sha(reference/'startup_states.csv')!=rm['raw_hashes']['startup_states.csv']:raise ValueError('same physical model and independent reference required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('physical source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_c2_startup',archive/'models/film_c2_startup');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);cpp=diag/'Gauss4Probe.cpp';cpp.write_text(CPP);shutil.copy2(mass,out/'public_mass.txt');shutil.copy2(table/'runner.py',out/'tableau.py');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 if a.precise_attachment:
  shutil.copytree(ROOT/'models/film_precise_attachment',archive/'models/film_precise_attachment');code=CPP.replace('#include "../../models/film_lateral_tendon/Step.h"','#include "../../models/film_lateral_tendon/Step.h"\n#include "../../models/film_precise_attachment/Force.h"').replace('regrip_lateral_tendon::parts(map,','regrip_precise_attachment::parts(map,');cpp.write_text(code);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
 if a.reuse:
  reuse=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((reuse/'summary.json').read_text())
  if old.get('toy_gate')!='PASS' or not old.get('FD_query_state_stages_EXACT') or old['source_hashes']!=sources or sha(reuse/'reference')!=old['binary_sha256']:raise ValueError('ALL kernel/model sources and qualified binary must match')
  shutil.copy2(reuse/'reference',out/'reference');compile=dict(exit_code=0,reused_summary_sha256=sha(reuse/'summary.json'),ALL_source_hashes_EXACT=True)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 r=dict(status='FAIL',scope='independent Gauss4 same-law nonlinear startup kernel ONLY;NOT actual SOFA/time/grasp certification',substeps=a.substeps,Newton_tolerance_Ns=a.newton_tol,horizon_s=.0002,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),physical_model_summary_sha256=sha(provider/'summary.json'),frozen_reference_summary_sha256=sha(reference/'summary.json'),tableau_summary_sha256=sha(table/'summary.json'),public_mass_sha256=sha(out/'public_mass.txt'),source_hashes=sources,compile=compile,trials={},relative_gate=.001,selected_SOFA_method=None)
 r['attachment_variant']='reference-exact displacement-frame' if a.precise_attachment else 'legacy global-coordinate'
 if compile['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');toy=guarded([out/'reference','toy',out/'public_mass.txt',out/'toy.csv'],out/'toy_process',180);r['toy_process']=toy
  if toy['exit_code']==0:
   import mpmath as mp
   mp.mp.dps=100;spec=importlib.util.spec_from_file_location('qualified_tableau',out/'tableau.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);expected,res=module.discrete(mp.mpf('.001'),4);row=next(csv.DictReader((out/'toy.csv').open()));value=np.r_[np.fromstring(row['q'],sep=' '),np.fromstring(row['v'],sep=' ')];difference=max(float(abs(mp.mpf(float(x))-y)/abs(y)) for x,y in zip(value,expected));r.update(toy_high_precision_discrete_max_relative=difference,toy_FD=float(row['tangent_FD']),toy_gate='PASS' if difference<=1e-10 else 'FAIL')
  if r.get('toy_gate')!='PASS':
   r['failure_reason']='independent discrete kernel reference failed;FEM NOT RUN';r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);return
  for label,fd in (('plain',False),('FD',True)):
   run=guarded([out/'reference','fem',out/'public_mass.txt',out/(label+'.csv'),'.0002',str(a.substeps),str(a.newton_tol),*(['fd'] if fd else [])],out/(label+'_process'),180);r['trials'][label]=dict(process=run)
   if run['exit_code']!=0:break
  if all(x['process']['exit_code']==0 for x in r['trials'].values()):
   plain=next(csv.DictReader((out/'plain.csv').open()));checked=next(csv.DictReader((out/'FD.csv').open()));exact=all(plain[k]==checked[k] for k in ('time','momentum_sum_Ns','q','v')) and sha(out/'plain.csv.stages.csv')==sha(out/'FD.csv.stages.csv');truth=next(x for x in csv.DictReader((reference/'startup_states.csv').open()) if float(x['h_s'])==.0002 and x['kind']=='continuous_sparse_exponential');errors={}
   for key in ('q','v'):
    x,y=np.fromstring(plain[key],sep=' '),np.fromstring(truth[key],sep=' ')
    for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):errors[name+'_'+key]=float(np.linalg.norm(x[part]-y[part])/max(np.linalg.norm(x[part]),np.linalg.norm(y[part])))
   sx,sy=shape(np.fromstring(plain['q'],sep=' ')),shape(np.fromstring(truth['q'],sep=' '))
   for key in sx:errors[key]=abs(sx[key]-sy[key])/max(abs(sx[key]),abs(sy[key])) if max(abs(sx[key]),abs(sy[key])) else 0.
   r.update(status='EXPERIMENTAL' if r.get('toy_gate')=='PASS' and exact and float(checked['tangent_FD'])<=1e-8 else 'FAIL',FD_query_state_stages_EXACT=exact,nonlinear_stage_tangent_FD=float(checked['tangent_FD']),frozen_startup_comparison='PASS' if max(errors.values())<=.001 else 'FAIL',frozen_startup_relative_errors=errors,maximum_relative=max(errors.values()),warning='conditional rest-linearization comparison,NOT an exact nonlinear reference or full time gate')
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','trials','frozen_startup_relative_errors','toy_process')}))
if __name__=='__main__':main()
