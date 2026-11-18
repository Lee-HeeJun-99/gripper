"""Same actual50ms seed,6.4ms cumulative Gauss window at800/400/200us."""
import argparse,csv,json,math,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
from film_gauss_newton_trace import temporal_arithmetic
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_lateral_gauss/FreeBlock.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q0,v0;double start,saved;regrip_routed_checkpoint::read(argv[1],s,q0,v0,start,saved);unsigned nf=s.shared.nf,body=3*nf;regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
 auto energy=[&](const Eigen::VectorXd&q,const Eigen::VectorXd&v){std::array<long double,6>E{};for(unsigned f=0;f<3;++f){auto&film=s.shared.films[f].film;auto x=film.expand(q.segment(f*nf,nf));film.model.elements(x,0,[&](const Element&e){if(e.kind==0)E[e.ids.front()<105?0:1]+=e.energy.v;if(e.kind==1)E[2]+=e.energy.v;});}for(unsigned i=0;i<q.size();++i)E[i<body?3:i<body+3?4:5]+=.5L*s.shared.M(i,i)*v(i)*v(i);return E;};auto E0=energy(q0,v0);long double initial=0;for(auto x:E0)initial+=x;std::ofstream out(argv[2]);out<<std::setprecision(17)<<"substeps,macro,time,gap_bound_mm,momentum_sum_Ns,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation,damping_work_Nmm,signed_partial_defect_Nmm,q,v\n";
 for(unsigned count:{1u,2u,4u}){auto q=q0,v=v0;double time=start,gap=s.clearance(q),momentum=0;long double loss=0;
  for(unsigned macro=0;macro<8;++macro){double finish=time+.0008;
   for(unsigned micro=0;micro<count;++micro){double h=count==1?.0008:micro+1==count?finish-time:.0008/count;double speed=0;auto before=v;long double filmLoss=0;auto r=regrip_three_event::freeGauss(s,q,v,time,h,c,[&](unsigned f,const auto&step,const auto&){auto a=s.shared.films[f].film.expand(step.stageV[0]),b=s.shared.films[f].film.expand(step.stageV[1]);for(unsigned i=0;i<a.size();++i){Eigen::Vector3d x(a[i][0],a[i][1],a[i][2]),y(b[i][0],b[i][1],b[i][2]);speed=std::max(speed,((x+y)/2).norm()+.5*((y-x)/(std::sqrt(3.)/3)).norm());}for(unsigned j=0;j<2;++j)for(unsigned i=0;i<nf;++i)filmLoss+=static_cast<long double>(h)*s.shared.M(f*nf+i,f*nf+i)*step.stageV[j](i)*step.stageV[j](i);});Eigen::Vector3d middle=(v.segment<3>(body)+r.v.segment<3>(body))/2;double lower=s.clearance(q)-h*(speed+middle.norm());if(!(lower>0))throw std::runtime_error("window numerical-path clearance bound fails");gap=std::min(gap,lower);momentum+=r.momentumResidual;if(momentum>1e-17)throw std::runtime_error("window summed momentum bound fails;NOT relaxed");loss+=filmLoss+2*static_cast<long double>(h)*middle.dot(s.shared.M.block<3,3>(body,body)*middle);q=r.q;v=r.v;time+=h;}
   if(time!=finish)throw std::runtime_error("common accumulated macro endpoint differs");auto E=energy(q,v);long double total=0;for(auto x:E)total+=x;out<<count<<','<<macro+1<<','<<time<<','<<gap<<','<<momentum;for(auto x:E)out<<','<<x;out<<','<<loss<<','<<total-initial+loss;for(const auto*z:{&q,&v}){out<<",\"";for(double x:*z)out<<x<<' ';out<<'\"';}out<<'\n';out.flush();
  }
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--arithmetic',choices=('baseline','position','residual','both'),default='baseline');p.add_argument('--coarse-us',type=int,choices=(200,800),default=800);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_gauss800_extended1616';m=json.loads((src/'summary.json').read_text());actual=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';am=json.loads((actual/'summary.json').read_text());cp=actual/'three.checkpoint_250.txt';probe=ROOT/('results/autonomous_film_20261119_stationary_gauss_probe1606' if a.coarse_us==200 else 'results/autonomous_film_20261119_stationary_gauss800_probe1615');pm=json.loads((probe/'summary.json').read_text());forecast=2*pm['process']['runtime_s']*(224 if a.coarse_us==200 else 56)/7+30
 if m['status']!='PASS' or am['status']!='PASS' or sha(cp)!=m['input_checkpoint_sha256'] or forecast>480:raise ValueError('same-IVP measured800us profile and policy budget required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('qualified source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');helper=archive/'tools/film_gauss_newton_trace.py';helper.parent.mkdir(parents=True);shutil.copy2(ROOT/'tools/film_gauss_newton_trace.py',helper);header=archive/'models/film_transmission/Gauss.h';header.write_text(temporal_arithmetic(header.read_text(),a.arithmetic));diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(src/'sources/diagnostics/film_three_finger/FreeCheckpoint.h',diag/'FreeCheckpoint.h');cpp=diag/'GaussWindow.cpp';cpp.write_text(CPP.replace('{1u,2u,4u}','{4u,8u,16u}') if a.coarse_us==200 else CPP);shutil.copy2(cp,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',cp,out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent50→56.4ms Gauss recovery-window time/work test ONLY;NOT actual SOFA/full trajectory/grasp',coarse_us=a.coarse_us,arithmetic=a.arithmetic,arithmetic_helper_sha256=sha(helper),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(actual/'summary.json'),qualification_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(cp),predicted_child_runtime_s=forecast,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,root_work=None,tendon_work_Nmm=0,external_work_Nmm=0,normal_work_Nmm=0,work_zero_basis='declared zero-tension/zero-load/separated certified numerical path;NOT prior cumulative work',heat='NOT assigned')
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'states.csv').open()));by={(x['substeps'],x['macro']):x for x in rows};P=mapping();errors={};defects={}
  for macro in range(1,9):
   for left,right in ((('4','8'),('8','16'),('4','16')) if a.coarse_us==200 else (('1','2'),('2','4'),('1','4'))):
    x,y=by[(left,str(macro))],by[(right,str(macro))]
    if x['time']!=y['time']:raise ValueError('common actual accumulated time differs')
    quantities={}
    for key in ('U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation','damping_work_Nmm','signed_partial_defect_Nmm'):quantities[key]=(np.array([float(x[key])]),np.array([float(y[key])]))
    for key in ('q','v'):quantities['all_film_'+key]=(np.fromstring(x[key],sep=' ')[:1947],np.fromstring(y[key],sep=' ')[:1947])
    qx,qy=np.fromstring(x['q'],sep=' '),np.fromstring(y['q'],sep=' ')
    for f in range(3):
     sx,sy=shape(P@qx[649*f:649*(f+1)]),shape(P@qy[649*f:649*(f+1)])
     for key in sx:quantities[f'finger{f}_'+key]=(np.array([sx[key]]),np.array([sy[key]]))
    label=f'macro{macro}_{left}_{right}';pair={}
    for key,(u,v) in quantities.items():
     absolute=float(np.linalg.norm(u-v));scale=float(max(np.linalg.norm(u),np.linalg.norm(v)));relative=absolute/scale if scale else 0.;pair[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
    defects[label]=pair.pop('signed_partial_defect_Nmm');errors[label]=pair
  core=all(z['status']=='PASS' for pair in errors.values() for z in pair.values());defect=all(z['status']=='PASS' for z in defects.values());r.update(status='PASS' if len(rows)==24 and core and defect else 'FAIL',core_state_energy_work_time='PASS' if core else 'FAIL',signed_partial_defect_relative_time='PASS' if defect else 'FAIL',time_pairs=errors,signed_defect_pairs=defects,relative_gate=.001,binary_sha256=sha(out/'reference'),whole_energy='BLOCKED;root work unmeasured/global gates absent')
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','process','time_pairs','signed_defect_pairs')}))
if __name__=='__main__':main()
