"""Independent old-edge/new-face hypothesis, reusing isolated transfer law."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_stationary_to226_1561';m=json.loads((parent/'summary.json').read_text());cp=parent/'three.checkpoint_113.txt'
 if m['status']!='PASS' or sha(cp)!=m['raw_hashes'][cp.name]:raise ValueError('actual22.6ms qualified stationary state required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(cp,out/'input.checkpoint');shutil.copytree(parent/'sources',out/'sources');models=out/'sources/models';src=models/'film_three_finger_resume/IsolatedContactTransfer.h';text=src.read_text();anchor='row.feature!=6||other.feature!=6'
 if text.count(anchor)!=1:raise ValueError('original isolated source guard changed')
 text=text.replace('isolatedContactTransfer(', 'stationaryEdgeFaceTransfer(').replace('oldTriangle=124','oldTriangle=115').replace(anchor,'row.feature!=3||other.feature!=6').replace('unsigned newTriangle=117){','unsigned newTriangle=117,const std::function<void(const ContactTransfer&)>&eventObserver={}){')
 # The archived face-transfer reference uses analytic FACE extrapolation.
 # An old EDGE must use its qualified actual closest-edge branch instead.
 anchor='return faceBranchGeometry(s,x,out.old);'
 if text.count(anchor)!=1:raise ValueError('archived analytic old-face adapter differs')
 text=text.replace(anchor,'return ownedGeometry(s,x,out.old);')
 begin=text.index('if(minimumFaceParameter(s,out.pre.q,out.old)<=0)');finish=text.index('auto ng=ownedGeometry',begin)
 text=text[:begin]+'ownedGeometry(s,out.pre.q,out.old);for(const auto&stage:out.pre.stages)ownedGeometry(s,stage.q,out.old);'+text[finish:]
 if text.count(' out.post=')!=1:raise ValueError('single post-event solve expected')
 text=text.replace(' out.post=',' if(eventObserver)eventObserver(out);\n out.post=');header=models/'film_three_finger_resume/StationaryEdgeFace.generated.h';header.write_text(text);cpp=out/'sources/diagnostics/film_three_finger/StationaryEdgeFace.cpp';cpp.write_text('''#include "ContactCheckpoint.h"
#include "../../models/film_three_finger_resume/StationaryEdgeFace.generated.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_three_finger;using namespace regrip_three_resume;SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double t,h;regrip_routed_checkpoint::read(argv[1],s,q,v,t,h);std::ofstream event(std::string(argv[2])+".event.csv");event<<std::setprecision(17)<<"event_time,bracket_s,all_rows,active_rows,rank,J_difference_norm,new_min_vminus_mm_s,impact_loss_Nmm,momentum_Ns,qminus,vminus,vplus,impulse_Ns\\n";
 auto observe=[&](const ContactTransfer&r){double difference=0;for(unsigned f=0;f<3;++f)difference=std::max(difference,(r.eventGeometry.J.row(f)-r.eventGeometry.J.row(f+3)).norm());event<<t+r.fractionTime<<','<<r.bracketWidth<<','<<r.all.size()<<','<<r.active.size()<<','<<r.impact.rank<<','<<difference<<','<<(r.eventGeometry.J.bottomRows(3)*r.pre.v).minCoeff()<<','<<r.impact.state.energyLoss<<','<<r.impact.state.momentumResidual;for(const auto*z:{&r.pre.q,&r.pre.v,&r.impact.state.velocity,&r.impact.state.impulse}){event<<",\\\"";for(double x:*z)event<<x<<' ';event<<'\\\"';}event<<'\\n';event.flush();};
 auto r=stationaryEdgeFaceTransfer(s,q,v,t,h,115,117,observe);double vn=1e99;unsigned touching=0;for(unsigned f=0;f<3;++f){auto local=s.local(r.pre.q,f);for(unsigned k=0;k<s.shared.films[f].triangles.size();++k){auto row=s.shared.films[f].geometry(local,k);if(std::abs(row.gap)>1e-12)continue;Eigen::RowVectorXd J=Eigen::RowVectorXd::Zero(q.size());J.segment(f*s.shared.nf,s.shared.nf)=row.gradient.head(s.shared.nf).transpose();J.segment<3>(3*s.shared.nf)=row.gradient.segment<3>(s.shared.nf).transpose()*s.layout.mount[f].R.transpose();vn=std::min(vn,J.dot(r.impact.state.velocity));++touching;}}std::ofstream result(argv[2]);result<<std::setprecision(17)<<"time,gap_mm,linear_balance_Ns,angular_balance_Nmms,root_impulse_Ns,root_moment_Nmms,touching_rows,touching_min_vplus_mm_s,q,v\\n"<<t+h<<','<<r.minimumGap<<','<<r.linearBalance<<','<<r.angularBalance<<','<<r.rootImpulse.norm()<<','<<r.rootMoment.norm()<<','<<touching<<','<<vn;for(const auto*z:{&r.post.q,&r.post.v}){result<<",\\\"";for(double x:*z)result<<x<<' ';result<<'\\\"';}result<<'\\n';result.flush();
 }catch(const std::exception&e){std::cerr<<e.what()<<'\\n';return 1;}}
''');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'transfer.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent isolated EDGE115/FACE117 hypothesis;NOT actual SOFA/general CCD/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},parent_summary_sha256=sha(parent/'summary.json'),source_checkpoint_sha256=sha(cp),compile=compile,process=run,physical_change='existing transfer math;explicit old edge3 instead of face6;new target unchanged117;no force/control/tolerance/budget change',root_work=None)
 if run and run['exit_code']==0:
  x=next(csv.DictReader((out/'transfer.csv').open()));metrics={k:float(x[k]) for k in ('time','gap_mm','linear_balance_Ns','angular_balance_Nmms','root_impulse_Ns','root_moment_Nmms','touching_rows','touching_min_vplus_mm_s')};event=next(csv.DictReader((out/'transfer.csv.event.csv').open()));em={k:float(event[k]) for k in ('event_time','bracket_s','all_rows','active_rows','rank','J_difference_norm','new_min_vminus_mm_s','impact_loss_Nmm','momentum_Ns')};r.update(status='PASS' if metrics['gap_mm']>=-1e-10 and metrics['linear_balance_Ns']<=1e-17 and metrics['angular_balance_Nmms']<=1e-16 and metrics['touching_min_vplus_mm_s']>=-1e-10 else 'FAIL',metrics=metrics,event=em,binary_sha256=sha(out/'reference'))
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
