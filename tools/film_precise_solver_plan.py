"""Explicit early/late numerical plan, no old three-finger checkpoint reuse."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_c2_startup/Gauss4.h"
#include "../../models/film_solver_plan/Plan.h"
#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_lateral_tendon/Step.h"
#include "../../models/film_precise_tendon/Force.h"
#include <fstream>
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_transmission;if(argc!=4)throw std::runtime_error("public mass/output/steps required");auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);unsigned steps=std::stoul(argv[3]);auto control=control();std::vector<Point>q(m.size()),v(m.size());double time=0,momentum=0;std::ofstream states(argv[2]),stages(std::string(argv[2])+".stages.csv"),trace(std::string(argv[2])+".plan.csv");states<<std::setprecision(17)<<"time,q,v\n";stages<<std::setprecision(17)<<"macro,stage,time,weight_s,T,q,v,reduced_physical_force_N\n";trace<<std::setprecision(17)<<"macro,start,end,microsteps,tolerance,nonlinear_residual,iterations,transition_q_max_abs,transition_v_max_abs\n";
 for(unsigned k=0;k<steps;++k){double used=k+1==steps?.001-time:.001/steps;double h=(time+used)-time,finish=time+h;auto plan=regrip_solver_plan::select(k,steps,time,h);double clock=time,maxResidual=0;unsigned iterations=0;auto beforeQ=q,beforeV=v;
 for(unsigned micro=0;micro<plan.microsteps;++micro){double dt=micro+1==plan.microsteps?finish-clock:h/plan.microsteps;auto map=mechanics(m,q,v,dt,0,mass);auto r=regrip_c2_startup::gauss4(filmMass(map),map.pack(q),map.pack(v),clock,dt,[&](const Eigen::VectorXd&x,double t){return regrip_precise_tendon::parts(map,map.expand(x),control.sample(t).tension,6.);},false,plan.newtonTolerance);momentum+=r.residual;maxResidual=std::max(maxResidual,r.nonlinearResidual);iterations+=r.iterations;
 for(unsigned j=0;j<4;++j){double t=clock+dt*regrip_c2_startup::c[j];stages<<k+1<<','<<micro*4+j<<','<<t<<','<<dt*regrip_c2_startup::b[j]<<','<<control.sample(t).tension;quote(stages,map.expand(r.stageQ[j]));quote(stages,map.expand(r.stageV[j]));stages<<",\"";for(double x:r.internalForce[j])stages<<x<<' ';stages<<"\"\n";}q=map.expand(r.q);v=map.expand(r.v);clock+=dt;}
 if(clock!=finish)throw std::runtime_error("exact private/public accumulated clock required");time=finish;states<<time;quote(states,q);quote(states,v);states<<'\n';states.flush();trace<<k+1<<','<<time-h<<','<<time<<','<<plan.microsteps<<','<<plan.newtonTolerance<<','<<maxResidual<<','<<iterations<<",0,0\n";trace.flush();}
 if(time!=.001||momentum>1e-17)throw std::runtime_error("bounded endpoint/momentum failed");return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_tendon_gauss1715';m=json.loads((src/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('immutable qualified model changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');shutil.copytree(ROOT/'models/film_solver_plan',out/'sources/models/film_solver_plan');shutil.copy2(ROOT/'models/film_c2_startup/Gauss4.h',out/'sources/models/film_c2_startup/Gauss4.h');shutil.copy2(src/'public_mass.txt',out/'public_mass.txt');cpp=out/'sources/diagnostics/film_three_finger/SolverPlan.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP.replace('auto control=control();','auto input=control();').replace('control.sample','input.sample'))
 r=dict(status='INCOMPLETE',scope='independent1ms explicit solver-plan candidate;NOT actual SOFA/energy/contact/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},plan='first200us:8Gauss4 microsteps/macro,tol1e-24;later:1Gauss4/macro,tol1e-22;physical gates unchanged',transition='no state/time/integration-history correction;one-step Gauss has no multistep history',trials={})
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference')
  for steps in (40,80,160):
   folder=out/str(steps);folder.mkdir()
   if r['trials']:
    last=next(reversed(r['trials']));forecast=2*r['trials'][last]['runtime_s']*steps/int(last)+20
    if forecast>480:r.update(status='BLOCKED',reason='profile forecast exceeds child480s;NOT OS exhaustion');break
   r['trials'][str(steps)]=guarded([out/'reference',out/'public_mass.txt',folder/'state.csv',str(steps)],folder/'process',480);write_json(out/'progress.json',r)
   if r['trials'][str(steps)]['exit_code']!=0:break
  if r['status']!='BLOCKED':r['status']='COMPLETED_NOT_QUALIFIED' if len(r['trials'])==3 and all(x['exit_code']==0 for x in r['trials'].values()) else 'FAIL'
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','trials')}))
if __name__=='__main__':main()
