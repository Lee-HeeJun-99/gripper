#define REGRIP_STATIONARY_GAUSS_EMBEDDED
#include "../film_stationary_gauss/GaussOwner.cpp"
#include "../film_lateral_gauss_parallel/FreeBlock.h"
#include <chrono>
namespace regrip_three_resume {
class StationaryGaussParallelPilotODE:public StationaryGaussExpandedPilotODE {
public:
 SOFA_CLASS(StationaryGaussParallelPilotODE,StationaryGaussExpandedPilotODE);
 sofa::core::objectmodel::Data<unsigned> filmWorkers;
 StationaryGaussParallelPilotODE():filmWorkers(initData(&filmWorkers,unsigned(1),"filmWorkers","One or three immutable numerical film workers;SOFA access remains serial")){}
 std::string outputCheckpointMagic()const override{return "REGRIP_STATIONARY_GAUSS_PARALLEL_PILOT_V1";}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0008||getContext()->getTime()!=initialTime||initialTime<.0499||initialTime>.0501||externalForce.getValue()!=sofa::type::Vec3(0,0,0)||(filmWorkers.getValue()!=1&&filmWorkers.getValue()!=3))throw std::runtime_error("isolated exact50ms zero-load1/3-worker pilot fixture required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);double startGap=s.clearance(q),speedBound=0;std::string path=filename.getValue()+".gauss.stages.csv";if(std::ifstream(path))throw std::runtime_error("parallel Gauss stage journal exists");std::ofstream stages(path);stages<<std::setprecision(17)<<"finger,stage,time,weight_s,force_N,local_q,local_v\n";regrip_film_impact::EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;
  auto begin=std::chrono::steady_clock::now();auto result=regrip_gauss_parallel::freeGaussParallel(s,q,v,last,dt,c,filmWorkers.getValue(),[&](unsigned f,const auto&r,const auto&forces){auto a=s.shared.films[f].film.expand(r.stageV[0]),b=s.shared.films[f].film.expand(r.stageV[1]);double delta=std::sqrt(3.)/6;for(unsigned i=0;i<a.size();++i){Eigen::Vector3d x(a[i][0],a[i][1],a[i][2]),y(b[i][0],b[i][1],b[i][2]);speedBound=std::max(speedBound,((x+y)/2).norm()+.5*((y-x)/(2*delta)).norm());}for(unsigned j=0;j<2;++j){stages<<f<<','<<j<<','<<last+dt*(.5+(j?delta:-delta))<<','<<dt/2;quote(stages,forces[j]);quote(stages,r.stageQ[j]);quote(stages,r.stageV[j]);stages<<'\n';}});double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-begin).count();stages.flush();
  double bodySpeed=((v.segment<3>(3*s.shared.nf)+result.v.segment<3>(3*s.shared.nf))/2).norm(),lower=startGap-dt*(speedBound+bodySpeed);if(!(lower>0)||s.clearance(result.q)<=0)throw std::runtime_error("parallel Gauss numerical-path clearance fails;NO contact substitute");
  std::ofstream proof(filename.getValue()+".gauss.clearance.csv");proof<<std::setprecision(17)<<"time,start_gap_mm,film_speed_bound_mm_s,body_path_speed_mm_s,numerical_path_gap_lower_bound_mm\n"<<last+dt<<','<<startGap<<','<<speedBound<<','<<bodySpeed<<','<<lower<<'\n';std::ofstream execution(filename.getValue()+".gauss.execution.csv");execution<<std::setprecision(17)<<"workers,kernel_inclusive_seconds,mechanical_evaluations\n"<<filmWorkers.getValue()<<','<<seconds<<','<<result.mechanicalEvaluations<<'\n';
  commitActual(s,result.q,result.v,last+dt);accepted<<last+dt<<','<<lower<<','<<result.momentumResidual<<",null,0,"<<result.mechanicalEvaluations;quote(accepted,result.q);quote(accepted,result.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStationaryGaussParallelPilot";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL exact separated-film1/3-worker scheduling pilot;NOT contact parallelism or whole time/energy/grasp").add<regrip_three_resume::StationaryGaussParallelPilotODE>());}
}
