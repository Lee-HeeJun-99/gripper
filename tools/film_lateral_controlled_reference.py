"""Same actual23ms IVP;bounded contact-admissibility controller,not dt certification."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
LOOP=r'''
 std::ofstream microOut(std::string(argv[4])+".micro.csv");microOut<<std::setprecision(17)<<"macro,micro,stage,time,h,q,v,force\n";
 for(unsigned macro=0;macro<macros;++macro){double end=time+nominal;Eigen::VectorXd lambda;double gap=1e9,momentum=0,velocity=0;
 auto controlled=regrip_collocation::endpointControlledRows(s.shared.M,2,q,v,time,nominal,[&](const auto&x,double t){return s.force(x,control.sample(t).tension);},[&](const auto&x){return s.geometry(x);},[&](const auto&x){return s.clearance(x);},63,5,[&](const auto&r,const auto&q0,const auto&v0,double start,double h){std::ofstream probe(std::string(argv[4])+".release_trial.csv");probe<<std::setprecision(17)<<"stage,time,h,finger,triangle,feature,gap,normal_velocity,reaction,q,v\n";for(unsigned k=0;k<3;++k){const auto&x=k?r.stages[k-1].q:q0;const auto&vel=k?r.stages[k-1].v:v0;auto geo=s.geometry(x);for(unsigned f=0;f<3;++f){auto row=s.selected(x,f);probe<<k<<','<<(k?r.stages[k-1].time:start)<<','<<h<<','<<f<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<geo.J.row(f).dot(vel)<<','<<(k?r.stages[k-1].force[f]:r.initialForce[f]);for(const auto*z:{&x,&vel}){probe<<',';for(int i=0;i<z->size();++i)probe<<(i?" ":"")<<(*z)(i);}probe<<'\n';}}});
 for(unsigned micro=0;micro<controlled.accepted.size();++micro){const auto&result=controlled.accepted[micro];double h=controlled.durations[micro];
  for(unsigned k=0;k<3;++k){const auto&x=k?result.stages[k-1].q:q;const auto&vel=k?result.stages[k-1].v:v;const auto&force=k?result.stages[k-1].force:result.initialForce;auto J=s.geometry(x).J;double t=k?result.stages[k-1].time:time,weight=h*(k==1?2./3:1./6);W+=weight*control.sample(t).tension*cablePower(s,x,vel);We+=weight*s.external.dot(vel.segment<3>(body));D+=weight*2*vel.dot(s.shared.M*vel);C+=weight*force.dot(J*vel);gap=std::min(gap,s.clearance(x));microOut<<macro<<','<<micro<<','<<k<<','<<t<<','<<h;for(const auto*z:{&x,&vel,&force}){microOut<<',';for(int i=0;i<z->size();++i)microOut<<(i?" ":"")<<(*z)(i);}microOut<<'\n';microOut.flush();}
  momentum=std::max(momentum,result.momentumResidual);velocity=std::max(velocity,result.velocityResidual);q=result.q;v=result.v;lambda=result.stages[1].force;time=result.stages[1].time;
 }if(time!=end||gap< -1e-10||momentum>1e-17||velocity>1e-10)throw std::runtime_error("unchanged whole-stage/clock/momentum gates failed");
 auto e=stored(s,q);out<<time<<','<<gap<<','<<momentum<<','<<velocity<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<.5*v.dot(s.shared.M*v)<<','<<W<<','<<We<<','<<D<<','<<C;for(const auto*z:{&lambda,&q,&v}){out<<',';for(int i=0;i<z->size();++i)out<<(i?" ":"")<<(*z)(i);}out<<','<<control.sample(time).tension<<','<<controlled.attempts<<','<<controlled.stageRejected<<','<<controlled.endpointRejected<<','<<controlled.accepted.size()<<'\n';out.flush();
 }
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--macros',type=int,choices=(1,2,4,8),default=1);p.add_argument('--profile');p.add_argument('--reuse');p.add_argument('--parent');p.add_argument('--checkpoint-step',type=int);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+(a.parent or '20261118_lateral_gap_probe1461'));m=json.loads((src/'summary.json').read_text())
 checkpoint=src/f'three.checkpoint_{a.checkpoint_step}.txt' if a.parent else src/'input.checkpoint'
 if a.parent:
  if m['status']!='PASS' or not a.checkpoint_step or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('qualified actual controlled/contact-event checkpoint required')
 elif m['status']!='EXPERIMENTAL' or not m['accepted_prefix_qv_time_exact'] or sha(checkpoint)!=m['checkpoint_sha256']:raise ValueError('exact accepted actual23ms IVP required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('source archive changed')
 forecast=None
 if a.macros>1:
  if not a.profile:raise ValueError('same-controller measured runtime profile required')
  prof=ROOT/'results'/('autonomous_film_'+a.profile);pm=json.loads((prof/'summary.json').read_text())
  if pm['status']!='PASS' or pm['checkpoint_sha256']!=sha(checkpoint) or sha(prof/'sources/models/film_coupled_collocation/EndpointControlledRows.h')!=sha(ROOT/'models/film_coupled_collocation/EndpointControlledRows.h'):raise ValueError('profile physical/controller IVP differs')
  forecast=2*pm['process']['runtime_s']*a.macros/pm['macros']+30
  if forecast>480:raise ValueError('measured policy forecast>480s;NOT OS exhaustion')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');shutil.copytree(src/'sources/models',out/'sources/models');template=ROOT/'results/autonomous_film_20261118_lateral_gap_probe1461/sources/diagnostics/film_three_finger/RoutedHoldReference.cpp';dest=out/'sources/diagnostics/film_three_finger/RoutedHoldReference.cpp';dest.parent.mkdir(parents=True);shutil.copy2(template,dest);shutil.copy2(ROOT/'models/film_coupled_collocation/EndpointControlledRows.h',out/'sources/models/film_coupled_collocation/EndpointControlledRows.h')
 cpp=out/'sources/diagnostics/film_three_finger/RoutedHoldReference.cpp';text=cpp.read_text();text=text.replace('REGRIP_LATERAL_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1') if a.parent else text;begin=text.index(' for(unsigned macro=0;macro<macros;++macro)');end=text.index(' std::cout',begin);text=text[:begin]+LOOP+text[end:];text='#include "../../models/film_coupled_collocation/EndpointControlledRows.h"\n'+text;text=text.replace('(macros!=8&&macros!=32)','(macros!=1&&macros!=2&&macros!=4&&macros!=8)').replace('force,q,v,T_per_rail\\n','force,q,v,T_per_rail,attempts,stage_rejected,endpoint_rejected,micro_steps\\n');cpp.write_text(text)
 sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()}
 if a.reuse:
  reused=ROOT/'results'/('autonomous_film_'+a.reuse);reuse=json.loads((reused/'summary.json').read_text())
  if reuse['status']!='PASS' or reuse['source_hashes']!=sources or sha(reused/'reference')!=reuse['binary_sha256']:raise ValueError('exact compiled-source reference reuse required')
  shutil.copy2(reused/'reference',out/'reference');compile=dict(exit_code=0,reused_from=a.reuse)
 else:
  compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 run=guarded([out/'reference',out/'input.checkpoint',str(a.macros),'1',out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='same actual IVP shared-kernel contact-admissibility refinement ONLY;NOT actual SOFA/global time/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),checkpoint_sha256=sha(out/'input.checkpoint'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},compile=compile,process=run,macros=a.macros,predicted_child_runtime_s=forecast,parent_actual_summary_sha256=(sha(src/'summary.json') if a.parent else None),position_projection=False,tolerance_relaxed=False)
 if r['status']=='PASS':r.update(endpoint=list(csv.DictReader((out/'states.csv').open()))[-1],binary_sha256=sha(out/'reference'),raw_sha256=sha(out/'states.csv'))
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','endpoint')}))
if __name__=='__main__':main()
