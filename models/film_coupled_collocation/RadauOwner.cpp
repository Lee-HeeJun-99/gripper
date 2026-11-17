#include "SystemRadau.h"
#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled {
class SingleRowRadauSphereODE final:public CoupledSphereODE {
public:
 SOFA_CLASS(SingleRowRadauSphereODE,CoupledSphereODE);
 sofa::core::objectmodel::Data<double>startTime{initData(&startTime,0.,"startTime","Explicit actual post-impact initial clock")};
 sofa::core::objectmodel::Data<bool>lobatto{initData(&lobatto,false,"lobatto","Separate fourth-order LobattoIIIA control;default RadauIIA preserved")};
 sofa::core::objectmodel::Data<double>maximumDuration{initData(&maximumDuration,1e-5,"maximumDuration","Explicit independently-qualified persistent window<=625us;default10us preserved")};
 std::ofstream stages;
 void init()override{CoupledSphereODE::init();auto*c=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());if(!c||startTime.getValue()<0||startTime.getValue()>1)throw std::runtime_error("explicit isolated post-impact clock required");c->setTime(startTime.getValue());std::string path=filename.getValue()+".stages.csv";if(std::ifstream(path))throw std::runtime_error("stage journal exists");stages.open(path);stages<<std::setprecision(17)<<"macro_start,stage_time,triangle,feature,gap,normal_force,normal_velocity,momentum_residual,velocity_residual,q,v\n";}
 Result advanceSystem(const System&s,double time,const EventControl&control)override{
  if(!(maximumDuration.getValue()>0&&maximumDuration.getValue()<=.000625)||s.film.h>1e-5||time+s.film.h-startTime.getValue()>maximumDuration.getValue()+1e-14)throw std::runtime_error("isolated persistent window/step budget;not general contact certification");
  auto step=singleRowRadauStep(s,time,control,lobatto.getValue());
  if(lobatto.getValue()){Eigen::VectorXd q=Eigen::VectorXd::Zero(s.n);q.head(s.nf)=s.film.pack(s.before.q);q.segment<3>(s.nf)=s.before.body.center;auto v=s.pack(s.before);auto&row=step.result.contactRows[0];stages<<time<<','<<time<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<step.stages.initialForce<<','<<row.gradient.dot(v)<<','<<step.stages.momentumResidual<<','<<step.stages.velocityResidual;quote(stages,q);quote(stages,v);stages<<'\n';}
  for(unsigned k=0;k<2;++k){auto&stage=step.stages.stages[k];auto&row=step.result.contactRows[k+unsigned(lobatto.getValue())];stages<<time<<','<<stage.time<<','<<row.triangle<<','<<row.feature<<','<<stage.geometry.gap<<','<<stage.force<<','<<stage.geometry.J.dot(stage.v)<<','<<step.stages.momentumResidual<<','<<step.stages.velocityResidual;quote(stages,stage.q);quote(stages,stage.v);stages<<'\n';}stages.flush();return step.result;
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCoupledRadau";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL isolated persistent single-row Radau;not impact/release/grasp").add<regrip_coupled::SingleRowRadauSphereODE>());}
}
