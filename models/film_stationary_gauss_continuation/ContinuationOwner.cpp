// Separate experimental numerical continuation;old midpoint owner is preserved.
#define REGRIP_STATIONARY_RELEASE_EMBEDDED
#include "../film_stationary_release/StationaryRelease.cpp"
#include "../film_lateral_gauss_parallel/FreeBlock.h"
#include "GaussFooter.h"
namespace regrip_three_resume {
class StationaryGaussContinuationODE:public StationaryFreeODE {
public:
 SOFA_CLASS(StationaryGaussContinuationODE,StationaryFreeODE);
 sofa::core::objectmodel::Data<bool> gaussResume;
 std::ofstream gaussStages,gaussClearance;
 StationaryGaussContinuationODE():gaussResume(initData(&gaussResume,false,"gaussResume","Typed Gauss checkpoint instead of original50ms midpoint FREE checkpoint")){}
 std::string inputCheckpointMagic()const override{return gaussResume.getValue()?"REGRIP_STATIONARY_GAUSS_FREE_V1":"REGRIP_STATIONARY_FREE_V1";}
 std::string outputCheckpointMagic()const override{return "REGRIP_STATIONARY_GAUSS_FREE_V1";}
 double maximumResumeEndTime()const override{return .0564;}
 bool permittedResumeDt(double h)const override{return gaussResume.getValue()?h==.00005:h==.0002;}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v)override{
  if(!gaussResume.getValue()){StationaryFreeODE::readContactCheckpoint(in,s,q,v);return;}
  provenance=regrip_stationary_gauss::readFooter(in,initialTime);lastImpactTime=provenance.lastImpact;if(s.clearance(q)<=0)throw std::runtime_error("typed Gauss FREE separation required");
 }
 void init()override{
  StationaryFreeODE::init();if(!ready)return;
  auto open=[&](std::ofstream&stream,const char*suffix,const char*header){std::string path=filename.getValue()+suffix;if(std::ifstream(path))throw std::runtime_error("Gauss continuation journal exists");stream.open(path);stream<<std::setprecision(17)<<header<<'\n';};
  open(gaussStages,".gauss.stages.csv","step,finger,stage,time,weight_s,force_N,local_q,local_v");
  open(gaussClearance,".gauss.clearance.csv","time,start_gap_mm,film_speed_bound_mm_s,body_path_speed_mm_s,numerical_path_gap_lower_bound_mm");
 }
 void bwdInit()override{
  StationaryFreeODE::bwdInit();if(!restored||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("exact stationary zero-load checkpoint required");
  if(gaussResume.getValue()){if(initialTime<.05||savedDt!=.00005)throw std::runtime_error("typed Gauss continuation time/dt mismatch");return;}
  if(initialTime<.0499||initialTime>.0501||savedDt!=.0002)throw std::runtime_error("only qualified original50ms FREE origin allowed");
  SharedFilmSystem s(Layout(),{0,0,0},true,true);Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);auto before=body->read(sofa::core::vec_id::read_access::position)->getValue()[0].getOrientation();double old=savedDt;savedDt=.00005;clocks(initialTime,savedDt);Eigen::VectorXd x=q,w=v;readActual(s,x,w);auto after=body->read(sofa::core::vec_id::read_access::position)->getValue()[0].getOrientation();bool same=q==x&&v==w;for(unsigned i=0;i<4;++i)same=same&&before[i]==after[i];if(!same)throw std::runtime_error("Gauss dt transition changed physical state");
  std::string path=filename.getValue()+".dt_transition.csv";if(std::ifstream(path))throw std::runtime_error("transition journal exists");std::ofstream out(path);out<<std::setprecision(17)<<"absolute_time,checkpoint_dt,new_dt,physical_qv_quaternion_EXACT,verified_contexts\n"<<initialTime<<','<<old<<','<<savedDt<<",1,11\n";
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||dt!=.00005||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("bounded zero-load50us Gauss continuation clock required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);double start=s.clearance(q),speed=0;if(!(start>0))throw std::runtime_error("Gauss FREE initial separation lost");regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
  auto r=regrip_gauss_parallel::freeGaussParallel(s,q,v,last,dt,c,3,[&](unsigned f,const auto&step,const auto&forces){auto a=s.shared.films[f].film.expand(step.stageV[0]),b=s.shared.films[f].film.expand(step.stageV[1]);double delta=std::sqrt(3.)/6;for(unsigned i=0;i<a.size();++i){Eigen::Vector3d x(a[i][0],a[i][1],a[i][2]),y(b[i][0],b[i][1],b[i][2]);speed=std::max(speed,((x+y)/2).norm()+.5*((y-x)/(2*delta)).norm());}for(unsigned j=0;j<2;++j){gaussStages<<priorSteps+count+1<<','<<f<<','<<j<<','<<last+dt*(.5+(j?delta:-delta))<<','<<dt/2;quote(gaussStages,forces[j]);quote(gaussStages,step.stageQ[j]);quote(gaussStages,step.stageV[j]);gaussStages<<'\n';}});gaussStages.flush();double bodySpeed=((v.segment<3>(3*s.shared.nf)+r.v.segment<3>(3*s.shared.nf))/2).norm(),lower=start-dt*(speed+bodySpeed);if(!(lower>0)||s.clearance(r.q)<=0)throw std::runtime_error("Gauss FREE numerical-path clearance failed;NO commit");gaussClearance<<last+dt<<','<<start<<','<<speed<<','<<bodySpeed<<','<<lower<<'\n';gaussClearance.flush();commitActual(s,r.q,r.v,last+dt);accepted<<last+dt<<','<<lower<<','<<r.momentumResidual<<",null,0,"<<r.mechanicalEvaluations;quote(accepted,r.q);quote(accepted,r.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStationaryGaussContinuation";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL typed separated stationary Gauss50us continuation;NOT whole energy/time/grasp certification").add<regrip_three_resume::StationaryGaussContinuationODE>());}
}
