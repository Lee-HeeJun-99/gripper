"""Same-binary separated-film parallel scheduling purity and measured cost."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_lateral_gauss_parallel/FreeBlock.h"
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,oldDt;regrip_routed_checkpoint::read(argv[1],s,q,v,time,oldDt);regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;std::array<std::vector<Eigen::VectorXd>,3>captured;std::array<regrip_three_event::FreeState,3>result;std::array<double,3>duration{};bool exact=true;
 for(unsigned repeat=0;repeat<3;++repeat){for(unsigned offset=0;offset<3;++offset){unsigned mode=(offset+repeat)%3;captured[mode].clear();auto observer=[&](unsigned,const auto&r,const auto&forces){for(unsigned j=0;j<2;++j){captured[mode].push_back(r.stageQ[j]);captured[mode].push_back(r.stageV[j]);captured[mode].push_back(forces[j]);}};auto begin=std::chrono::steady_clock::now();result[mode]=mode==0?regrip_three_event::freeGauss(s,q,v,time,.0008,c,observer):regrip_gauss_parallel::freeGaussParallel(s,q,v,time,.0008,c,mode==1?1:3,observer);duration[mode]+=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();}
  for(unsigned mode:{1u,2u}){exact=exact&&result[mode].q==result[0].q&&result[mode].v==result[0].v&&result[mode].momentumResidual==result[0].momentumResidual&&result[mode].mechanicalEvaluations==result[0].mechanicalEvaluations&&captured[mode].size()==captured[0].size();for(unsigned i=0;i<captured[0].size();++i)exact=exact&&std::memcmp(captured[mode][i].data(),captured[0][i].data(),sizeof(double)*captured[0][i].size())==0;}
 }
 std::cout<<std::setprecision(17)<<"{\"state_stages_forces_momentum_counts_EXACT\":"<<(exact?"true":"false")<<",\"original_seconds\":"<<duration[0]<<",\"new_serial_seconds\":"<<duration[1]<<",\"three_worker_seconds\":"<<duration[2]<<",\"three_over_original\":"<<duration[2]/duration[0]<<",\"repeats\":3,\"film_workers\":3}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_gauss800_actual1618';m=json.loads((src/'summary.json').read_text());parent=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';pm=json.loads((parent/'summary.json').read_text());cp=parent/'three.checkpoint_250.txt';reference=ROOT/'results/autonomous_film_20261119_stationary_gauss800_extended1616'
 if m['status']!='PASS' or sha(cp)!=m['source_checkpoint_sha256'] or pm['status']!='PASS':raise ValueError('qualified exact50ms/actual800us Gauss fixture required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('frozen compiled source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_lateral_gauss_parallel',archive/'models/film_lateral_gauss_parallel');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(reference/'sources/diagnostics/film_three_finger/FreeCheckpoint.h',diag/'FreeCheckpoint.h');cpp=diag/'ParallelProbe.cpp';cpp.write_text(CPP);shutil.copy2(cp,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-pthread','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe',cp],out/'process',180) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='same-binary independent separated numerical block scheduling benchmark ONLY;NOT end-to-end SOFA gain/general contact parallelism',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(cp),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,worker_safety='immutable numerical snapshots only;NO SOFA/clock/journal access on workers;serial ordered reduction',physics='same AD2/Gauss/mass/control;NO model/solver tolerance change')
 if run and run['exit_code']==0:
  result=json.loads((out/'process/stdout.log').read_text());r.update(result);r['status']='PASS' if result['state_stages_forces_momentum_counts_EXACT'] else 'FAIL';r['candidate']='needs actual same-binary A/B' if result['three_over_original']<1 else 'REJECTED:no measured kernel gain';r['binary_sha256']=sha(out/'probe')
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
