"""SAME actual50ms IVP:200us free midpoint interval,1/2/4 substeps."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_three_finger_event/BlockFree.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;
 SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q0,v0;double start,macro;regrip_routed_checkpoint::read(argv[1],s,q0,v0,start,macro);const double end=start+macro;unsigned nf=s.shared.nf,body=3*nf;std::ofstream out(argv[2]);out<<std::setprecision(17)<<"steps,time,gap_mm,momentum_bound_Ns,U_skin,U_rails,U_attachment,K_film,K_linear,K_rotation,q,v\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
 for(unsigned count:{1u,2u,4u}){auto q=q0,v=v0;double time=start,gap=s.clearance(q),momentum=0;
  for(unsigned step=0;step<count;++step){double h=step+1==count?end-time:macro/count;if(!(h>0))throw std::runtime_error("positive actual interval required");auto r=regrip_three_event::freeMidpoint(s,q,v,time,h,c);Eigen::VectorXd middle=(q+r.q)/2;gap=std::min({gap,s.clearance(middle),s.clearance(r.q)});momentum+=r.momentumResidual;q=r.q;v=r.v;time+=h;}
  if(time!=end||gap<=0||momentum>1e-17)throw std::runtime_error("common actual endpoint/separation/momentum gate failed");double skin=0,rails=0,bond=0;long double Kf=0,Kl=0,Kr=0;
  for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f].film;auto local=film.expand(q.segment(f*nf,nf));film.model.elements(local,0,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)skin+=e.energy.v;else rails+=e.energy.v;}if(e.kind==1)bond+=e.energy.v;});}
  for(unsigned i=0;i<q.size();++i){long double K=.5L*s.shared.M(i,i)*v(i)*v(i);if(i<body)Kf+=K;else if(i<body+3)Kl+=K;else Kr+=K;}
  out<<count<<','<<time<<','<<gap<<','<<momentum<<','<<skin<<','<<rails<<','<<bond<<','<<Kf<<','<<Kl<<','<<Kr;for(const auto*z:{&q,&v}){out<<",\"";for(double x:*z)out<<x<<' ';out<<'\"';}out<<'\n';out.flush();
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--extended',action='store_true',help='Resolve observed nonmonotone velocity comparison with8/16/32,not an automatic PASS');p.add_argument('--gauss',action='store_true',help='Separate existing Gauss4 film candidate;NOT a baseline replacement');p.add_argument('--trace-failed32',action='store_true',help='Passive detailed rejection diagnostic ONLY;unchanged gates');p.add_argument('--span-us',type=int,choices=(200,800),default=200);p.add_argument('--profile');a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';m=json.loads((src/'summary.json').read_text());cp=src/'three.checkpoint_250.txt';provider=ROOT/'results/autonomous_film_20261119_stationary_free_actual1590';pm=json.loads((provider/'summary.json').read_text())
 if a.span_us!=200 and not a.gauss:raise ValueError('separate Gauss step-size probe only;old midpoint experiment preserved')
 if a.trace_failed32 and (a.gauss or a.extended):raise ValueError('one-variable passive failure trace only')
 if a.gauss and a.extended:
  profile=a.profile or '20261119_stationary_gauss_probe1606';probe=json.loads((ROOT/'results'/('autonomous_film_'+profile)/'summary.json').read_text())
  if probe.get('span_us',200)!=a.span_us:raise ValueError('same-span initial measured profile required')
  if probe['status']!='PASS' or 'Gauss4' not in probe['solver']:raise ValueError('initial Gauss1/2/4 cost/physics probe required')
 if m['status']!='PASS' or sha(cp)!=m['raw_hashes'][cp.name] or pm['status']!='PASS':raise ValueError('qualified actual50ms and FREE loader required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual compiled archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);loader=provider/'sources/diagnostics/film_three_finger/FreeCheckpoint.h'
 if a.gauss:shutil.copytree(ROOT/'models/film_lateral_gauss',archive/'models/film_lateral_gauss')
 if sha(loader)!=pm['source_hashes']['diagnostics/film_three_finger/FreeCheckpoint.h']:raise ValueError('qualified FREE reader changed')
 forecast=None
 if a.extended:
  profile_case=(a.profile or '20261119_stationary_gauss_probe1606') if a.gauss else '20261119_stationary_free_time1603';old=json.loads((ROOT/'results'/('autonomous_film_'+profile_case)/'summary.json').read_text());forecast=2*old['process']['runtime_s']*63/7+30
  if old['status']!='PASS' or old['input_checkpoint_sha256']!=sha(cp) or forecast>480:raise ValueError('same-IVP measured extended63-substep budget required;NOT OS exhaustion')
 shutil.copy2(loader,diag/'FreeCheckpoint.h');cpp=diag/'FreeRefinement.cpp';text=CPP.replace('{1u,2u,4u}','{1u,2u,4u,8u,16u,32u}') if a.extended else CPP
 if a.span_us==800:text=text.replace('const double end=start+macro;','macro=.0008;const double end=start+macro;')
 if a.trace_failed32:
  text=text.replace('{1u,2u,4u}','{32u}');anchor='if(time!=end||gap<=0||momentum>1e-17)'
  text=text.replace(anchor,'std::cerr<<std::setprecision(17)<<"TRACE count="<<count<<" actual_end="<<time<<" common_end="<<end<<" clock_defect="<<time-end<<" gap="<<gap<<" sum_residual_norms="<<momentum<<"\\n";'+anchor)
 if a.gauss:text=text.replace('film_three_finger_event/BlockFree.h','film_lateral_gauss/FreeBlock.h').replace('regrip_three_event::freeMidpoint','regrip_three_event::freeGauss')
 cpp.write_text(text);shutil.copy2(cp,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent actual50ms IVP free200us local time refinement ONLY;NOT actual SOFA beyond50ms/full trajectory/energy/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(cp),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,gate_relative=.001,predicted_child_runtime_s=forecast,solver='existing Gauss4 films+existing midpoint free body' if a.gauss else 'existing free midpoint',common_time='last interval is actual positive endpoint-minus-accumulated-clock;NO clock reset',root_work=None,tendon_work='exactly0 in this post30ms zero-tension reference interval;NOT prior cumulative work',history_convergence='NOT RUN')
 r.update(span_us=a.span_us,checkpoint_dt_s=.0002,scope=f'independent actual50ms IVP free{a.span_us}us local time refinement ONLY;NOT actual SOFA/full trajectory/energy/grasp certification')
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'states.csv').open()));pairs={}
  for i,j in ((i,j) for i in range(len(rows)) for j in range(i+1,len(rows))):
   errors={}
   for key in ('q','v','U_skin','U_rails','U_attachment','K_film','K_linear','K_rotation'):
    x=np.fromstring(rows[i][key],sep=' ') if key in ('q','v') else np.array([float(rows[i][key])]);y=np.fromstring(rows[j][key],sep=' ') if key in ('q','v') else np.array([float(rows[j][key])]);absolute=float(np.linalg.norm(x-y));scale=float(max(np.linalg.norm(x),np.linalg.norm(y)));relative=absolute/scale if scale else 0.;errors[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
   pairs[rows[i]['steps']+'_'+rows[j]['steps']]=errors
  r.update(status='PASS' if len(rows)==(6 if a.extended else 3) and all(v['status']=='PASS' for pair in pairs.values() for v in pair.values()) else 'FAIL',pairs=pairs,span_us=a.span_us,checkpoint_dt_s=.0002,common_endpoint_s=rows[0]['time'],binary_sha256=sha(out/'reference'))
  if a.extended:
   baseline=(a.profile or '20261119_stationary_gauss_probe1606') if a.gauss else '20261119_stationary_free_time1603';oldrows=list(csv.DictReader((ROOT/'results'/('autonomous_film_'+baseline)/'states.csv').open()));r['original_three_rows_EXACT']=rows[:3]==oldrows
   if not r['original_three_rows_EXACT']:r['status']='FAIL'
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
