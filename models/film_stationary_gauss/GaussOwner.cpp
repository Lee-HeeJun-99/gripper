#define REGRIP_STATIONARY_RELEASE_EMBEDDED
#include "../film_stationary_release/StationaryRelease.cpp"
#include "../film_lateral_gauss/FreeBlock.h"
namespace regrip_three_resume {
class StationaryGaussPilotODE:public StationaryFreeODE {
public:
 SOFA_CLASS(StationaryGaussPilotODE,StationaryFreeODE);
 double maximumResumeEndTime()const override{return .0502;}
 std::string outputCheckpointMagic()const override{return "REGRIP_STATIONARY_GAUSS_PILOT_V1";}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0002||getContext()->getTime()!=initialTime||initialTime<.0499||initialTime>.0501||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("isolated actual50ms Gauss pilot fixture required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);double startGap=s.clearance(q),speedBound=0;std::string path=filename.getValue()+".gauss.stages.csv";if(std::ifstream(path))throw std::runtime_error("Gauss stage journal exists");std::ofstream stages(path);stages<<std::setprecision(17)<<"finger,stage,time,weight_s,force_N,local_q,local_v\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
  auto result=regrip_three_event::freeGauss(s,q,v,last,dt,c,[&](unsigned f,const auto&r,const auto&forces){auto a=s.shared.films[f].film.expand(r.stageV[0]),b=s.shared.films[f].film.expand(r.stageV[1]);double delta=std::sqrt(3.)/6;for(unsigned i=0;i<a.size();++i){Eigen::Vector3d x(a[i][0],a[i][1],a[i][2]),y(b[i][0],b[i][1],b[i][2]);speedBound=std::max(speedBound,((x+y)/2).norm()+.5*((y-x)/(2*delta)).norm());}for(unsigned j=0;j<2;++j){stages<<f<<','<<j<<','<<last+dt*(.5+(j?delta:-delta))<<','<<dt/2;quote(stages,forces[j]);quote(stages,r.stageQ[j]);quote(stages,r.stageV[j]);stages<<'\n';}});stages.flush();
  // Defined Gauss position polynomial has linear derivative interpolating the
  // two stage velocities;the rigid midpoint position path is linear. Distance
  // to a moving triangle is1-Lipschitz in maximum nodal/centre displacement.
  double bodySpeed=((v.segment<3>(3*s.shared.nf)+result.v.segment<3>(3*s.shared.nf))/2).norm();double lower=startGap-dt*(speedBound+bodySpeed);if(!(lower>0)||s.clearance(result.q)<=0)throw std::runtime_error("Gauss numerical-path separation bound fails;NO contact substitute");
  std::ofstream proof(filename.getValue()+".gauss.clearance.csv");proof<<std::setprecision(17)<<"time,start_gap_mm,film_speed_bound_mm_s,body_path_speed_mm_s,numerical_path_gap_lower_bound_mm\n"<<last+dt<<','<<startGap<<','<<speedBound<<','<<bodySpeed<<','<<lower<<'\n';
  commitActual(s,result.q,result.v,last+dt);accepted<<last+dt<<','<<lower<<','<<result.momentumResidual<<",null,0,"<<result.mechanicalEvaluations;quote(accepted,result.q);quote(accepted,result.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStationaryGaussPilot";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated50ms separated Gauss film pilot;NOT whole time/energy/grasp").add<regrip_three_resume::StationaryGaussPilotODE>());}
}
