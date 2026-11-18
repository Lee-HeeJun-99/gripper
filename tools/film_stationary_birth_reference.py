"""Isolated numerical birth from the preserved rejected stationary-closing step.

Qualifies ONLY the accepted free prefix, not the failed full horizon.
"""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_stationary_to230_1547';m=json.loads((parent/'summary.json').read_text());cp=parent/'three.checkpoint_101.txt'
 if m['status']!='FAIL' or m['process']['exit_code']==0 or 'NEW rest-closing birth detected;NO unvalidated contact commit' not in (parent/'process/stderr.log').read_text() or sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('preserved explicit stationary birth rejection and accepted prefix required')
 for f,d in m['raw_hashes'].items():
  if sha(parent/f)!=d:raise ValueError('raw changed')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('actual model archive changed')
 rows=list(csv.DictReader((parent/'three.states.csv').open()));ref=list(csv.DictReader((parent/'reference.csv').open()));n=1953;tokens=cp.read_text().split();last=rows[-1]
 if tokens[0]!='REGRIP_LATERAL_REST_FREE_V1' or tokens[4]!=m['identity'] or float(tokens[1])!=float(last['time']) or not np.array_equal(np.array(tokens[5:5+n],float),np.fromstring(last['q'],sep=' ')) or not np.array_equal(np.array(tokens[5+n:5+2*n],float),np.fromstring(last['v'],sep=' ')):raise ValueError('accepted physical checkpoint/state mismatch')
 delta={k:max(float(np.max(abs(np.fromstring(x[k],sep=' ')-np.fromstring(y[k],sep=' ')))) for x,y in zip(rows,ref)) for k in ('q','v')}
 if len(rows)!=18 or any(x['time']!=y['time'] for x,y in zip(rows,ref)) or max(delta.values())>1e-12:raise ValueError('18 accepted prefix steps require strict actual API qualification')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(cp,out/'input.checkpoint');archive=out/'sources';shutil.copytree(parent/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);shutil.copy2(parent/'sources/diagnostics/film_three_finger/RestCheckpoint.h',diag/'RestCheckpoint.h');cpp=diag/'StationaryBirth.cpp';cpp.write_text('''#include "RestCheckpoint.h"
#include "../../models/film_three_finger_event/BracketedBirth.h"
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double t,h;regrip_routed_checkpoint::read(argv[1],s,q,v,t,h);regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;auto b=regrip_three_event::bracketedBirth(s,q,v,t,h/4,h,c);std::ofstream out(argv[2]);out<<std::setprecision(17)<<"start_time,event_time,lower_time,gap_mm,rows,rank,momentum_Ns,impact_loss_Nmm,minimum_vplus_mm_s,qminus,vminus,vplus,impulse_Ns\\n"<<t<<','<<b.time<<','<<b.lowerTime<<','<<b.gap<<','<<b.rows.size()<<','<<b.impact.rank<<','<<b.momentumResidual<<','<<b.impact.state.energyLoss<<','<<b.impact.state.normalVelocity.minCoeff();for(const auto*z:{&b.before.q,&b.before.v,&b.impact.state.velocity,&b.impact.state.impulse}){out<<",\\\"";for(double x:*z)out<<x<<' ';out<<'\\\"';}out<<'\\n';out.flush();std::ofstream rows(std::string(argv[2])+".rows.csv");rows<<std::setprecision(17)<<"finger,triangle,feature,gap_mm,vminus_mm_s,vplus_mm_s,impulse_Ns\\n";for(unsigned i=0;i<b.rows.size();++i){const auto&r=b.rows[i];rows<<r.finger<<','<<r.triangle<<','<<r.feature<<','<<r.gap<<','<<r.normalBefore<<','<<r.normalAfter<<','<<b.impact.state.impulse(i)<<'\\n';}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\\n';return 1;}}
''');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'birth.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent EXTERNALLY ISOLATED stationary-origin numerical endpoint-family birth/impact;NOT actual contact/grasp or globally earliest continuous CCD',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(cp),accepted_prefix_steps=18,accepted_prefix_API_max_abs=delta,parent_horizon_status='FAIL preserved;no rejected contact state committed',compile=compile,process=run,root_reaction_impulse=None,global_momentum_certification='NOT measured;reduced momentum only',external_force_N=[0]*3,gravity=[0]*3)
 if run and run['exit_code']==0:
  x=next(csv.DictReader((out/'birth.csv').open()));metrics={k:float(x[k]) for k in ('start_time','event_time','lower_time','gap_mm','rows','rank','momentum_Ns','impact_loss_Nmm','minimum_vplus_mm_s')};imp=np.fromstring(x['impulse_Ns'],sep=' ');r.update(status='PASS' if abs(metrics['gap_mm'])<=1e-12 and metrics['event_time']-metrics['lower_time']<=1e-13 and metrics['momentum_Ns']<=1e-17 and metrics['minimum_vplus_mm_s']>=-1e-10 and imp.min()>=0 and metrics['impact_loss_Nmm']>=0 else 'FAIL',metrics=metrics,binary_sha256=sha(out/'reference'))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
