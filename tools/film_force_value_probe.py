"""Separate force-only ASSEMBLY benchmark;full AD2/old physical owner preserved."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "FreeCheckpoint.h"
#include "../../models/film_force_value/SharedValue.h"
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;regrip_routed_checkpoint::read(argv[1],s,q,v,time,h);double fullTime=0,valueTime=0,maxError=0;bool exact=true,Hsame=true;volatile double sink=0;
 for(unsigned trial=0;trial<3;++trial){Eigen::VectorXd x=q+(trial*h/2)*v;auto before=s.force(x,0);auto val=regrip_force_value::value(s,x,0);auto after=s.force(x,0);exact=exact&&std::memcmp(before.value.data(),val.data(),sizeof(double)*val.size())==0;Hsame=Hsame&&std::memcmp(before.negativeTangent.data(),after.negativeTangent.data(),sizeof(double)*before.negativeTangent.size())==0;maxError=std::max(maxError,(before.value-val).cwiseAbs().maxCoeff());
  for(unsigned repeat=0;repeat<4;++repeat){auto measure=[&](bool full){auto start=std::chrono::steady_clock::now();if(full){auto a=s.force(x,0);sink+=a.value.norm();}else{auto a=regrip_force_value::value(s,x,0);sink+=a.norm();}double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();if(full)fullTime+=elapsed;else valueTime+=elapsed;};measure(repeat%2==0);measure(repeat%2!=0);}
 }
 std::cout<<std::setprecision(17)<<"{\"force_bit_exact\":"<<(exact?"true":"false")<<",\"Hessian_unchanged\":"<<(Hsame?"true":"false")<<",\"max_abs_force_N\":"<<maxError<<",\"full_seconds\":"<<fullTime<<",\"value_seconds\":"<<valueTime<<",\"candidate_over_full\":"<<valueTime/fullTime<<",\"queries_per_variant\":12}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';m=json.loads((src/'summary.json').read_text());cp=src/'three.checkpoint_250.txt';provider=ROOT/'results/autonomous_film_20261119_stationary_free_actual1590';pm=json.loads((provider/'summary.json').read_text())
 if m['status']!='PASS' or sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('strict actual50ms IVP required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('immutable actual model changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copytree(ROOT/'models/film_force_value',archive/'models/film_force_value');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);loader=provider/'sources/diagnostics/film_three_finger/FreeCheckpoint.h'
 if sha(loader)!=pm['source_hashes']['diagnostics/film_three_finger/FreeCheckpoint.h']:raise ValueError('qualified reader changed')
 shutil.copy2(loader,diag/'FreeCheckpoint.h');cpp=diag/'ForceValue.cpp';cpp.write_text(CPP);shutil.copy2(cp,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe',out/'input.checkpoint'],out/'process',120) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent same-AD2 force-only global assembly benchmark ONLY;NOT actual SOFA end-to-end speedup',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(cp),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,AD_algorithm='original AD2 unchanged;unused global Hessian allocation/assembly skipped',heap_allocations=None,actual_state_time_energy_regression='NOT RUN;required before integration')
 if run and run['exit_code']==0:
  result=json.loads((out/'process/stdout.log').read_text());r.update(result);r['status']='PASS' if result['force_bit_exact'] and result['Hessian_unchanged'] and result['max_abs_force_N']==0 else 'FAIL';r['speed_candidate']='measured kernel gain only;needs actual A/B' if result['candidate_over_full']<1 else 'REJECTED:kernel not faster';r['binary_sha256']=sha(out/'probe')
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
