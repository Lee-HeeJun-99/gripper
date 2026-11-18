#define REGRIP_LATERAL_REST_RESUME_EMBEDDED
#include "../film_lateral_rest_resume/RestResume.cpp"
#include "FirstImpact.h"
namespace regrip_three_resume {
class StationaryImpactODE:public LateralRestResumeODE {
public:
 SOFA_CLASS(StationaryImpactODE,LateralRestResumeODE);
 double lastImpactTime=0;
 std::string outputCheckpointMagic()const override{return "REGRIP_STATIONARY_CONTACT_V1";}
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&s,const Eigen::VectorXd&q,double time)override{
  out<<"CONTACT_ROWS 3\n";for(unsigned f=0;f<3;++f){auto row=s.selected(q,f);out<<f<<' '<<row.triangle<<' '<<row.feature<<'\n';}out<<"ROWS_OBSERVED_AT "<<time<<"\nLAST_IMPACT_TIME "<<lastImpactTime<<"\nINITIAL_CONDITION STATIONARY_SEPARATED\nACCUMULATED_TIME "<<time<<'\n';
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count!=0||dt!=savedDt||dt!=.0002||getContext()->getTime()!=initialTime||externalForce.getValue()!=sofa::type::Vec3(0,0,0))throw std::runtime_error("isolated actual stationary-origin impact fixture required");
  last=getContext()->getTime();SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);auto r=regrip_stationary_contact::firstImpact(s,q,v,last,dt);lastImpactTime=r.birth.time;
  auto open=[&](const char*suffix){std::string path=filename.getValue()+suffix;if(std::ifstream(path))throw std::runtime_error("stationary impact journal exists");std::ofstream out(path);out<<std::setprecision(17);return out;};
  auto event=open(".stationary.event.csv");event<<"time,event_time,rows,rank,gap_mm,momentum_bound_Ns,impact_loss_Nmm,q,v,impulse_Ns\n"<<last+dt<<','<<r.birth.time<<','<<r.birth.rows.size()<<','<<r.birth.impact.rank<<','<<r.minimumGap<<','<<r.momentumBound<<','<<r.birth.impact.state.energyLoss;quote(event,r.after.q);quote(event,r.after.v);quote(event,r.birth.impact.state.impulse);event<<'\n';event.flush();
  auto impulse=open(".stationary.impulses.csv");impulse<<"event_time,impact_row,finger,triangle,feature,gap_mm,vminus_mm_s,vplus_mm_s,impulse_Ns,jacobian\n";for(unsigned i=0;i<r.birth.rows.size();++i){const auto&row=r.birth.rows[i];impulse<<r.birth.time<<','<<i<<','<<row.finger<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<row.normalBefore<<','<<row.normalAfter<<','<<r.birth.impact.state.impulse(i);quote(impulse,r.birth.J.row(i));impulse<<'\n';}impulse.flush();
  auto birth=open(".stationary.birth.csv");birth<<"event_time,qminus,vminus,vplus,impulse_Ns\n"<<r.birth.time;quote(birth,r.birth.before.q);quote(birth,r.birth.before.v);quote(birth,r.birth.impact.state.velocity);quote(birth,r.birth.impact.state.impulse);birth<<'\n';birth.flush();
  auto stages=open(".stationary.stages.csv");stages<<"micro,stage,time,h_s,force,q,v\n";Eigen::VectorXd x=r.birth.before.q,vel=r.birth.impact.state.velocity;double time=r.birth.time;unsigned iterations=0,evaluations=0;double velocityResidual=0;
  for(unsigned i=0;i<r.after.accepted.size();++i){const auto&step=r.after.accepted[i];iterations+=step.iterations;evaluations+=step.evaluations;velocityResidual=std::max(velocityResidual,step.velocityResidual);
   for(unsigned k=0;k<3;++k){const auto&position=k?step.stages[k-1].q:x;const auto&velocity=k?step.stages[k-1].v:vel;const auto&force=k?step.stages[k-1].force:step.initialForce;const double clock=k?step.stages[k-1].time:time;stages<<i<<','<<k<<','<<clock<<','<<r.after.durations[i];quote(stages,force);quote(stages,position);quote(stages,velocity);stages<<'\n';auto geo=s.geometry(position);for(unsigned f=0;f<3;++f){auto row=s.selected(position,f);Eigen::Vector3d normal=s.layout.mount[f].R*row.normal,point=s.layout.mount[f].origin+s.layout.mount[f].R*row.contact;rowJournal<<clock<<','<<f<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<force(f)<<','<<geo.J.row(f).dot(velocity);for(double y:normal)rowJournal<<','<<y;for(double y:point)rowJournal<<','<<y;quote(rowJournal,geo.J.row(f));quote(rowJournal,position);quote(rowJournal,velocity);rowJournal<<'\n';}}
   x=step.q;vel=step.v;time=step.stages[1].time;
  }stages.flush();rowJournal.flush();commitActual(s,r.after.q,r.after.v,last+dt);accepted<<last+dt<<','<<r.minimumGap<<','<<r.momentumBound<<','<<velocityResidual<<','<<iterations<<','<<evaluations;quote(accepted,r.after.q);quote(accepted,r.after.v);accepted<<'\n';accepted.flush();++count;save(last+dt);
 }
};
}
void registerFilmLateralField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStationaryImpact";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmLateralField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated C2-driven stationary-origin first impact/remainder;NOT global CCD/time/energy/grasp").add<regrip_three_resume::StationaryImpactODE>());}
}
