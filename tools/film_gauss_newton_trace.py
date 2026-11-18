"""Minimum failing independent54.8ms reference state;passive Gauss Newton trace."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def temporal_arithmetic(text,variant):
 if variant not in ('baseline','position','residual','both'):raise ValueError('explicit temporal arithmetic variant required')
 if variant in ('position','both'):
  old='e.q[j]=q;for(int k=0;k<2;++k)e.q[j]+=h*A[j][k]*trial.segment(k*n,n);';new='e.q[j].resize(n);for(int a=0;a<n;++a){long double sum=q(a);for(int k=0;k<2;++k)sum+=static_cast<long double>(h)*A[j][k]*trial(k*n+a);e.q[j](a)=static_cast<double>(sum);}'
  if text.count(old)!=1:raise ValueError('exact position accumulation anchor differs')
  text=text.replace(old,new)
 if variant in ('residual','both'):
  old='e.residual.segment(i*n,n)=M*(e.v[i]-v);for(int j=0;j<2;++j)e.residual.segment(i*n,n)-=h*A[i][j]*e.total[j];';new='Eigen::VectorXd inertia=M*(e.v[i]-v);for(int a=0;a<n;++a){long double sum=inertia(a);for(int j=0;j<2;++j)sum-=static_cast<long double>(h)*A[i][j]*e.total[j](a);e.residual(i*n+a)=static_cast<double>(sum);}'
  if text.count(old)!=1:raise ValueError('exact residual accumulation anchor differs')
  text=text.replace(old,new)
 return text
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_lateral_gauss/FreeBlock.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double actualTime,dt;regrip_routed_checkpoint::read(argv[1],s,q,v,actualTime,dt);std::ifstream in(argv[2]);double time;in>>time;for(double&x:q)in>>x;for(double&x:v)in>>x;if(!in||!q.allFinite()||!v.allFinite()||s.clearance(q)<=0)throw std::runtime_error("finite separated independent reference prefix required");regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;auto result=regrip_three_event::freeGauss(s,q,v,time,.0008,c);std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time,q,v\n"<<time+.0008;for(const auto*z:{&result.q,&result.v}){out<<",\"";for(double x:*z)out<<x<<' ';out<<'\"';}out<<'\n';std::cout<<"REFERENCE STEP COMPLETED;NOT actual SOFA/global qualification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--arithmetic',choices=('baseline','position','residual','both'),default='baseline');p.add_argument('--fd',action='store_true',help='existing three directional FD checks per film;unchanged1e-8 gate');a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_gauss_window1619';m=json.loads((src/'summary.json').read_text());rows=list(csv.DictReader((src/'states.csv').open()));last=rows[-1]
 if m['status']!='FAIL' or m['failure_reason']!='Gauss residual line search failed' or sha(src/'states.csv')!=m['raw_hashes']['states.csv'] or last['substeps']!='1' or last['macro']!='6':raise ValueError('specific preserved1619 failing reference prefix required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('immutable reference archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(src/'sources/diagnostics/film_three_finger/FreeCheckpoint.h',diag/'FreeCheckpoint.h');cpp=diag/'GaussTrace.cpp';cpp.write_text(CPP);header=archive/'models/film_transmission/Gauss.h';text=header.read_text();text='#include <iostream>\n#include <iomanip>\n'+text
 edits={
 'auto e=evaluate(x);':'auto e=evaluate(x);std::cerr<<std::setprecision(17)<<"BEGIN time="<<time<<" h="<<h<<" n="<<n<<"\\n";',
 'double norm=e.residual.norm();if(norm<=gaussNewtonTolerance)break;':'double norm=e.residual.norm();std::cerr<<"ITER "<<iteration<<" norm="<<norm<<" threshold="<<gaussNewtonTolerance<<"\\n";if(norm<=gaussNewtonTolerance)break;',
 'Eigen::VectorXd delta=lu.solve(-e.residual);':'Eigen::VectorXd delta=lu.solve(-e.residual);std::cerr<<"LINEAR norm="<<(e.tangent*delta+e.residual).norm()<<" delta="<<delta.norm()<<"\\n";',
 'auto next=evaluate(trial);if(next.residual.norm()':'auto next=evaluate(trial);std::cerr<<"TRIAL cut="<<cut<<" alpha="<<alpha<<" norm="<<next.residual.norm()<<"\\n";if(next.residual.norm()'}
 for old,new in edits.items():
  if text.count(old)!=1:raise ValueError('exact passive trace anchor differs: '+old)
  text=text.replace(old,new)
 text=temporal_arithmetic(text,a.arithmetic)
 if a.fd:
  block=archive/'models/film_lateral_gauss/FreeBlock.h';bt=block.read_text()
  if bt.count('return value;});')!=1:raise ValueError('exact Gauss FD flag anchor differs')
  block.write_text(bt.replace('return value;});','return value;},true);'));anchor='if(out.tangentError>1e-8)'
  if text.count(anchor)!=1:raise ValueError('existing unchanged directional FD gate missing')
  text=text.replace(anchor,'std::cerr<<"FD relative="<<out.tangentError<<" gate=1e-8\\n";'+anchor)
 header.write_text(text);shutil.copy2(src/'input.checkpoint',out/'actual50_mass.checkpoint');(out/'reference_prefix.txt').write_text(last['time']+' '+last['q']+' '+last['v']+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'actual50_mass.checkpoint',out/'reference_prefix.txt',out/'endpoint.csv'],out/'process',180) if compile['exit_code']==0 else None;r=dict(status=('PASS' if a.arithmetic!='baseline' and run and run['exit_code']==0 else 'EXPERIMENTAL' if run and run['exit_code']==1 and 'Gauss residual line search failed' in (out/'process/stderr.log').read_text() else 'FAIL'),scope='isolated independent Newton arithmetic/trace trial ONLY;NOT actual SOFA accepted state or general solver fix',arithmetic=a.arithmetic,directional_FD=a.fd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),failed_summary_sha256=sha(src/'summary.json'),prefix_source_csv_sha256=sha(src/'states.csv'),prefix_time_s=float(last['time']),prefix_type='accepted mathematical-reference prefix of FAILED window,NOT an actual SOFA checkpoint',actual_mass_checkpoint_sha256=sha(out/'actual50_mass.checkpoint'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,physical_parameters='unchanged;only specified Gauss temporal summation arithmetic and passive logging differ;AD2 force/Hessian code untouched',tolerance='unchanged1e-18',binary_sha256=sha(out/'reference') if (out/'reference').exists() else None);r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
