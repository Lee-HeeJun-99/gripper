#define REGRIP_THREE_RELEASE_EMBEDDED
#include "../film_three_finger_release/ThreeFilmRelease.cpp"
#include <sofa/simulation/AnimateEndEvent.h>
namespace regrip_three_resume {
class ThreeFilmRecoveryODE:public ThreeFilmFreeODE {
public:
 SOFA_CLASS(ThreeFilmRecoveryODE,ThreeFilmFreeODE);
 double maximumResumeEndTime()const override{return .032;}
 bool permittedResumeDt(double dt)const override{return dt==.0001||dt==.00005||dt==.000025;}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(!restored||count>=maxSteps.getValue()||dt!=savedDt||!permittedResumeDt(dt)||getContext()->getDt()!=dt||getContext()->getTime()<=last||getContext()->getTime()<.03-1e-14||getContext()->getTime()+dt>physicalEndLimit()+1e-14||externalForce.getValue()!=sofa::type::Vec3(0,0,-.001))throw std::runtime_error("separate bounded30..32ms FREE recovery/clock guard");
  last=getContext()->getTime();double finish=last+dt,h=finish-last;SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q=s.initial,v=Eigen::VectorXd::Zero(q.size());readActual(s,q,v);if(s.clearance(q)<=0)throw std::runtime_error("recovery initial surface is not separated");regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;
  auto after=regrip_three_event::freeMidpoint(s,q,v,last,h,control);auto path=regrip_three_event::denseSurfacePath(s,q,v,after,h);if(regrip_film_impact::earliestSurfaceEvent(path.path,path.triangles,{0,0,0},s.layout.bufferRadius))throw std::runtime_error("recovery dense numerical path reimpact;NOT committed");Eigen::VectorXd middle=(q+after.q)/2,middleV=(v+after.v)/2;double gap=std::min({s.clearance(q),s.clearance(middle),s.clearance(after.q)});if(gap< -1e-10)throw std::runtime_error("recovery whole force-stage clearance fails");
  for(unsigned i=0;i<3;++i){const auto&x=i==0?q:i==1?middle:after.q;const auto&vel=i==0?v:i==1?middleV:after.v;freeStages<<priorSteps+count+1<<','<<(i==0?"initial":i==1?"force_midpoint":"end")<<','<<(i==0?last:i==1?last+h/2:finish)<<','<<(i==1?h:0);quote(freeStages,x);quote(freeStages,vel);freeStages<<'\n';}freeStages.flush();
  commitActual(s,after.q,after.v,finish);accepted<<finish<<','<<gap<<','<<after.momentumResidual<<",null,0,"<<after.mechanicalEvaluations;quote(accepted,after.q);quote(accepted,after.v);accepted<<'\n';accepted.flush();++count;save(finish);
 }
};
// Observation experiment,not an unqualified replacement of persistent V3.
// Changes NEXT public dt,never positions/velocities or the accumulated time.
class ThreeFilmAlignedRecoveryODE:public ThreeFilmRecoveryODE {
public:
 SOFA_CLASS(ThreeFilmAlignedRecoveryODE,ThreeFilmRecoveryODE);
 sofa::core::objectmodel::Data<double>nominalStep{initData(&nominalStep,.0001,"nominalStep","Nominal100/50/25us;last interval is exactly target-current time")};
 sofa::core::objectmodel::Data<unsigned>observationSteps{initData(&observationSteps,8u,"observationSteps","Explicit8/16/32 bounded observation plan")};
 std::ofstream schedule;
 ThreeFilmAlignedRecoveryODE(){f_listening.setValue(true);}
 virtual unsigned observationBudget()const{return observationSteps.getValue();}
 virtual bool fullObservationInput()const{return true;}
 bool permittedResumeDt(double dt)const override{return (nominalStep.getValue()==.0001||nominalStep.getValue()==.00005||nominalStep.getValue()==.000025)&&dt>0&&dt<=2*nominalStep.getValue();}
 std::string outputCheckpointMagic()const override{return "REGRIP_OBSERVATION_V4";}
 void init()override{
  ThreeFilmRecoveryODE::init();if(!ready)return;unsigned n=observationSteps.getValue();if((n!=8&&n!=16&&n!=32)||nominalStep.getValue()!=.0008/n||(fullObservationInput()&&(getContext()->getDt()!=nominalStep.getValue()||endTime.getValue()!=getContext()->getTime()+.0008)))throw std::runtime_error("exact aligned observation plan invalid before restore");std::string path=filename.getValue()+".recovery.clock.csv";if(std::ifstream(path))throw std::runtime_error("aligned clock journal exists");schedule.open(path);schedule<<std::setprecision(17)<<"time,used_dt,next_dt,contexts,all_child_times_exact,target_reached\n";
 }
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&s,const Eigen::VectorXd&q,double time)override{
  ThreeFilmFreeODE::writeContactCheckpoint(out,s,q,time);double next=count<observationSteps.getValue()?(count+1==observationSteps.getValue()?endTime.getValue()-time:nominalStep.getValue()):savedDt;
  out<<"NOMINAL_DT "<<nominalStep.getValue()<<"\nOBSERVATION_END "<<endTime.getValue()<<"\nUSED_DT "<<savedDt<<"\nEXPECTED_NEXT_DT "<<next<<"\nSTEPS_REMAINING "<<observationSteps.getValue()-count<<'\n';
 }
 void solve(const sofa::core::ExecParams*p,SReal dt,sofa::core::MultiVecCoordId x,sofa::core::MultiVecDerivId v)override{if(count>=observationBudget())throw std::runtime_error("aligned observation plan complete;no extra step");ThreeFilmRecoveryODE::solve(p,dt,x,v);}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;double time=getContext()->getTime(),used=getContext()->getDt();if(!restored||count==0||count>observationBudget()||time!=last+used)throw std::runtime_error("aligned actual accumulated endpoint mismatch");
  bool done=count==observationBudget();double next=done?used:count+1==observationBudget()?endTime.getValue()-time:nominalStep.getValue();if(!(next>0&&next<=2*nominalStep.getValue())||(done&&time!=endTime.getValue()))throw std::runtime_error("aligned final fractional dt/target invalid");
  auto*root=dynamic_cast<sofa::core::objectmodel::BaseNode*>(getContext());std::set<sofa::core::objectmodel::BaseNode*>seen;std::function<void(sofa::core::objectmodel::BaseNode*)>apply=[&](auto*node){if(!seen.insert(node).second)return;if(node->getContext()->getTime()!=time)throw std::runtime_error("aligned child time differs;NO clock reset");node->getContext()->setDt(next);if(node->getContext()->getDt()!=next)throw std::runtime_error("aligned next dt rejected");for(auto*child:node->getChildren())apply(child);};if(!root)throw std::runtime_error("aligned scene node missing");apply(root);if(seen.size()!=11)throw std::runtime_error("aligned context topology changed");savedDt=next;schedule<<time<<','<<used<<','<<next<<','<<seen.size()<<",true,"<<done<<'\n';schedule.flush();
 }
};
class ThreeFilmPersistentRecoveryODE:public ThreeFilmAlignedRecoveryODE {
public:
 SOFA_CLASS(ThreeFilmPersistentRecoveryODE,ThreeFilmAlignedRecoveryODE);
 sofa::core::objectmodel::Data<bool>restartObservationPlan{initData(&restartObservationPlan,false,"restartObservationPlan","Explicit new bounded numerical plan ONLY after a completed V5;physical state/counter unchanged")};
 double planStart=0;unsigned planIndex=0,remainingPlan=0;
 bool v5Input()const{std::ifstream in(checkpoint.getValue());std::string magic;in>>magic;return magic=="REGRIP_PERSISTENT_OBSERVATION_V5";}
 bool fullObservationInput()const override{return !v5Input()||restartObservationPlan.getValue();}
 unsigned observationBudget()const override{return remainingPlan;}
 std::string inputCheckpointMagic()const override{return v5Input()?"REGRIP_PERSISTENT_OBSERVATION_V5":"REGRIP_FREE_V3";}
 std::string outputCheckpointMagic()const override{return "REGRIP_PERSISTENT_OBSERVATION_V5";}
 void readContactCheckpoint(std::istream&in,const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v)override{
  ThreeFilmFreeODE::readContactCheckpoint(in,s,q,v);
  if(!v5Input()){if(restartObservationPlan.getValue())throw std::runtime_error("new-plan flag requires completed V5");planStart=initialTime;planIndex=priorSteps;remainingPlan=observationSteps.getValue();return;}
  auto number=[&](const char*expected){std::string label;double x;in>>label>>x;if(!in||label!=expected||!std::isfinite(x))throw std::runtime_error("persistent V5 plan label/value invalid");return x;};
  double start=number("PLAN_START"),index=number("PLAN_INITIAL_INDEX"),nominal=number("NOMINAL_DT"),total=number("TOTAL_STEPS"),end=number("OBSERVATION_END"),used=number("USED_DT"),next=number("EXPECTED_NEXT_DT"),remaining=number("STEPS_REMAINING");
  if(index<0||index!=std::floor(index)||(total!=8&&total!=16&&total!=32)||remaining<0||remaining>total||remaining!=std::floor(remaining)||nominal!=.0008/total||used!=savedDt||end!=start+.0008||priorSteps!=index+total-remaining)throw std::runtime_error("persistent V5 counter/duration/current-dt invalid");
  double accumulated=start;for(unsigned i=0;i<unsigned(total-remaining);++i)accumulated=i+1==unsigned(total)?end:accumulated+nominal;
  if(accumulated!=initialTime||next!=(remaining==0?used:remaining==1?end-initialTime:nominal))throw std::runtime_error("persistent V5 accumulated clock/next-dt invalid");
  if(restartObservationPlan.getValue()){
   if(remaining!=0||initialTime!=end||getContext()->getDt()!=nominalStep.getValue()||endTime.getValue()!=initialTime+.0008)throw std::runtime_error("persistent V5 new plan requires completed source and explicit next dt/target");planStart=initialTime;planIndex=priorSteps;remainingPlan=observationSteps.getValue();savedDt=nominalStep.getValue();
  }else{
   if(remaining==0||nominal!=nominalStep.getValue()||total!=observationSteps.getValue()||end!=endTime.getValue()||getContext()->getDt()!=next)throw std::runtime_error("persistent V5 plan differs;no silent replan");planStart=start;planIndex=unsigned(index);remainingPlan=unsigned(remaining);savedDt=next;
  }
 }
 void writeContactCheckpoint(std::ostream&out,const SharedFilmSystem&s,const Eigen::VectorXd&q,double time)override{
  ThreeFilmFreeODE::writeContactCheckpoint(out,s,q,time);unsigned remaining=remainingPlan-count;double next=remaining==0?savedDt:remaining==1?endTime.getValue()-time:nominalStep.getValue();out<<"PLAN_START "<<planStart<<"\nPLAN_INITIAL_INDEX "<<planIndex<<"\nNOMINAL_DT "<<nominalStep.getValue()<<"\nTOTAL_STEPS "<<observationSteps.getValue()<<"\nOBSERVATION_END "<<endTime.getValue()<<"\nUSED_DT "<<savedDt<<"\nEXPECTED_NEXT_DT "<<next<<"\nSTEPS_REMAINING "<<remaining<<'\n';
 }
};
// Separate scope, never changes the legacy32ms qualification boundary.
// Admission runner binds this to the same-IVP 31.6..38ms reference evidence.
class ThreeFilmExtendedRecoveryODE:public ThreeFilmPersistentRecoveryODE {
public:
 SOFA_CLASS(ThreeFilmExtendedRecoveryODE,ThreeFilmPersistentRecoveryODE);
 double maximumResumeEndTime()const override{return .038;}
 void init()override{
  if(getContext()->getTime()<.0315||nominalStep.getValue()!=.0001||observationSteps.getValue()!=8)throw std::runtime_error("extended recovery requires qualified100us eight-step FREE plan after31.6ms");
  ThreeFilmPersistentRecoveryODE::init();
 }
};
}
#ifndef REGRIP_RECOVERY_EMBEDDED
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripThreeFilmRecovery";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL separated30..32ms recovery;100/50/25us nominal steps and actual clock intervals;rejects reimpact;NOT restored shape/grasp certificate").add<regrip_three_resume::ThreeFilmRecoveryODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL exact-end observation:public next-dt scheduler,all11 contexts;observation V4 resume NOT qualified;NOT grasp").add<regrip_three_resume::ThreeFilmAlignedRecoveryODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL persistent V5 observation plan:used/next dt,accumulated clock,counter and explicit completed-plan extension;NOT grasp").add<regrip_three_resume::ThreeFilmPersistentRecoveryODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL separately admitted31.6..38ms FREE recovery;100us,V5 exact plan;NOT full recovery/grasp").add<regrip_three_resume::ThreeFilmExtendedRecoveryODE>());}
}
#endif
