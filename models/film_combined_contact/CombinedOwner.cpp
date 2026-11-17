#include "CombinedStep.h"
#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled {
class CoupledEventLobattoODE final:public CoupledSphereODE {
public:
 SOFA_CLASS(CoupledEventLobattoODE,CoupledSphereODE);
 sofa::core::objectmodel::Data<double>startTime{initData(&startTime,0.,"startTime","Explicit actual pre-impact initial clock")};
 sofa::core::objectmodel::Data<double>maximumDuration{initData(&maximumDuration,4e-5,"maximumDuration","Explicit profiled combined coupon<=1ms;not full-cycle certification")};
 sofa::core::objectmodel::Data<bool>sparseStage{initData(&sparseStage,false,"sparseStage","Opt-in exact-zero nonsymmetric SparseLU;false is same-binary original dense control")};
 std::ofstream stages;
 void init()override{
  CoupledSphereODE::init();auto*c=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());if(!c||!std::isfinite(startTime.getValue())||startTime.getValue()<0||startTime.getValue()>1)throw std::runtime_error("explicit finite isolated combined clock required");c->setTime(startTime.getValue());auto path=filename.getValue()+".stages.csv";if(std::ifstream(path))throw std::runtime_error("combined stage journal exists");stages.open(path);stages<<std::setprecision(17)<<"macro_start,persistent_start,stage_time,triangle,feature,gap,normal_force,normal_velocity,weighted_time,momentum_residual,velocity_residual,q,v\n";
  auto policyPath=filename.getValue()+".policy.csv";if(std::ifstream(policyPath))throw std::runtime_error("runtime policy journal exists");std::ofstream policy(policyPath);if(!policy)throw std::runtime_error("runtime policy journal unavailable");policy<<std::setprecision(17)<<"component,sparse_stage,start_time,maximum_duration,strict_newton,midpoint_contact,rayleigh_mass\n"<<getClassName()<<','<<sparseStage.getValue()<<','<<startTime.getValue()<<','<<maximumDuration.getValue()<<','<<strictNewton.getValue()<<','<<midpointContact.getValue()<<','<<rayleighMass.getValue()<<'\n';
 }
 Result advanceSystem(const System&original,double time,const EventControl&control)override{
  if(!(maximumDuration.getValue()>0&&maximumDuration.getValue()<=.001)||original.film.h>1e-5||time+original.film.h-startTime.getValue()>maximumDuration.getValue()+1e-14)throw std::runtime_error("combined prototype horizon/step budget");System s=original;s.absoluteNewtonResidual=1e-17;s.contactSolveGap=1e-14;auto accepted=combinedStep(s,time,control,sparseStage.getValue());
  if(accepted.persistent){auto&contact=*accepted.persistent;auto&result=contact.result;double h=time+s.film.h-accepted.persistentStart;
   Eigen::VectorXd q=Eigen::VectorXd::Zero(s.n),v;if(accepted.result.event){q.head(s.nf)=s.film.pack(accepted.result.postImpact.q);q.segment<3>(s.nf)=accepted.result.postImpact.body.center;v=s.pack(accepted.result.postImpact);}else{q.head(s.nf)=s.film.pack(s.before.q);q.segment<3>(s.nf)=s.before.body.center;v=s.pack(s.before);}
   for(unsigned k=0;k<3;++k){auto&row=result.contactRows[k];Eigen::VectorXd qq=k?contact.stages.stages[k-1].q:q,vv=k?contact.stages.stages[k-1].v:v;double force=k?contact.stages.stages[k-1].force:contact.stages.initialForce;stages<<time<<','<<accepted.persistentStart<<','<<result.contactTimes[k]<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<force<<','<<row.gradient.dot(vv)<<','<<h*(k==1?2./3:1./6)<<','<<contact.stages.momentumResidual<<','<<contact.stages.velocityResidual;quote(stages,qq);quote(stages,vv);stages<<'\n';}stages.flush();
  }return accepted.result;
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCombinedContact";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated coupled event+Lobatto remainder;NOT global CCD/release/grasp").add<regrip_coupled::CoupledEventLobattoODE>());}
}
