#include "AdaptiveStep.h"
#include "../film_coupled_contact/CoupledOwnerClass.h"
#include <sofa/core/objectmodel/Context.h>
namespace regrip_coupled_adaptive {
// Reuses the EXACT existing accepted-state owner for each accepted segment.
// Error estimation is query-only;no actual DOF is changed until all segments
// satisfy the controller. Public Context clock is restored before returning
// to the outer DefaultAnimationLoop. No SDK/Native constraint modifications.
class AdaptiveCoupledSphereODE final:public CoupledSphereODE {
public:
 SOFA_CLASS(AdaptiveCoupledSphereODE,CoupledSphereODE);
 sofa::core::objectmodel::Data<double>adaptiveTolerance{initData(&adaptiveTolerance,1e-4,"adaptiveTolerance","Fixed macro-horizon controller budget;NOT global time gate")};
 sofa::core::objectmodel::Data<unsigned>maxMacroSteps{initData(&maxMacroSteps,4u,"maxMacroSteps","Bounded experimental macro count1..20")};
 unsigned macroCount=0;std::ofstream macro,adaptation;
 void init()override{
  CoupledSphereODE::init();if(maxMacroSteps.getValue()==0||maxMacroSteps.getValue()>20)throw std::runtime_error("adaptive macro budget1..20");
  for(const auto*suffix:{".macro_states.csv",".adaptation.csv"})if(std::ifstream(filename.getValue()+suffix))throw std::runtime_error("adaptive journals exist");
  states.flush();std::ifstream input(filename.getValue()+".states.csv");std::string header;std::getline(input,header);if(header.empty())throw std::runtime_error("base owner state header unavailable");macro.open(filename.getValue()+".macro_states.csv");macro<<header<<'\n';adaptation.open(filename.getValue()+".adaptation.csv");adaptation<<std::setprecision(17)<<"begin,end,trials,rejected,accepted_segments,max_controller_error,max_instantaneous_relative_error\n";
 }
 void solve(const sofa::core::ExecParams*params,SReal dt,sofa::core::MultiVecCoordId xId,sofa::core::MultiVecDerivId vId)override{
  if(++macroCount>maxMacroSteps.getValue()||dt>.001||dt!=getContext()->getDt())throw std::runtime_error("adaptive pilot bounded to1ms macros");auto*context=dynamic_cast<sofa::core::objectmodel::Context*>(getContext());if(!context)throw std::runtime_error("public clock Context required");double begin=context->getTime();
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<Film*>(field->getContext()->getMechanicalState());auto*world=field->getContext()->get<Film>(std::string("actual/world"));auto*topology=world?world->getContext()->getMeshTopology():nullptr;if(!local||!topology)throw std::runtime_error("adaptive actual film geometry unavailable");
  Assembly model(parameter<unsigned>("nx"));model.guideIntervals=parameter<unsigned>("guideIntervals");model.guideOffset=parameter<double>("guideOffset");model.bondK=parameter<double>("bondStiffness");model.rootGuideSecondOrder=parameter<bool>("rootGuideSecondOrder");auto q=local->read(sofa::core::vec_id::read_access::position)->getValue();auto v=local->read(sofa::core::vec_id::read_access::velocity)->getValue();std::vector<Point>q0(q.size()),v0(q.size()),zero(q.size());std::vector<double>mass(q.size());for(unsigned i=0;i<q.size();++i){mass[i]=field->getContext()->getMass()->getElementMass(i);for(unsigned d=0;d<3;++d){q0[i][d]=q[i][d];v0[i][d]=v[i][d];}}
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];Body b;for(unsigned d=0;d<3;++d){b.center(d)=bx.getCenter()[d];b.linear(d)=bv.getVCenter()[d];b.angular(d)=bv.getVOrientation()[d];b.force(d)=externalForce.getValue()[d];}b.orientation=Eigen::Quaterniond(bx.getOrientation()[3],bx.getOrientation()[0],bx.getOrientation()[1],bx.getOrientation()[2]);sofa::linearalgebra::FullMatrix<double>M(6,6);M.clear();body->getContext()->getMass()->getElementMass(0,&M);b.mass=M.element(0,0);b.inertia=M.element(3,3);
  std::vector<std::array<unsigned,3>>triangles;for(auto t:topology->getTriangles())triangles.push_back({t[0],t[1],t[2]});EventControl control{parameter<double>("maximumTension"),parameter<double>("rampTime"),parameter<double>("releaseBegin"),parameter<double>("releaseEnd"),parameter<bool>("c2Control")};CoupledPlaneStep m(model,mass,dt,rayleighMass.getValue(),control.sample(begin).tension,q0,v0,zero,0);System system(m,triangles,b,radius.getValue(),strictNewton.getValue(),reuseAcceptedEvaluation.getValue());
  auto accepted=adaptiveStep(system,begin,control,adaptiveTolerance.getValue(),384,12,nullptr,true);
  adaptation<<begin<<','<<begin+dt<<','<<accepted.trials<<','<<accepted.rejected<<','<<accepted.segments.size()<<','<<accepted.maximumAcceptedError<<','<<accepted.maximumInstantaneousRelativeError<<'\n';adaptation.flush();
  struct Restore {sofa::core::objectmodel::Context*c;double time,dt;~Restore(){c->setTime(time);c->setDt(dt);}}restore{context,begin,dt};std::streampos finalOffset;
  for(const auto&segment:accepted.segments){context->setTime(segment.time);context->setDt(segment.h);finalOffset=states.tellp();CoupledSphereODE::solve(params,segment.h,xId,vId);
   const auto&actualQ=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&actualV=local->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)if(actualQ[i][d]!=segment.result.state.q[i][d]||actualV[i][d]!=segment.result.state.v[i][d])throw std::runtime_error("adaptive accepted actual film differs from query-only forecast");const auto&actualBody=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&actualVelocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d)if(actualBody.getCenter()[d]!=segment.result.state.body.center(d)||actualVelocity.getVCenter()[d]!=segment.result.state.body.linear(d)||actualVelocity.getVOrientation()[d]!=segment.result.state.body.angular(d))throw std::runtime_error("adaptive actual body differs from query-only forecast");
  }
  // Copy only the final accepted record,not a fabricated interpolated frame.
  states.flush();std::ifstream input(filename.getValue()+".states.csv");input.seekg(finalOffset);std::string line;if(!std::getline(input,line)||line.empty())throw std::runtime_error("adaptive final state row unavailable");macro<<line<<'\n';macro.flush();
 }
};
}
extern "C"{
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCoupledAdaptive";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Experimental query-only fixed-horizon adaptive controller reusing coupled accepted owner;NOT global time/grasp qualification").add<regrip_coupled_adaptive::AdaptiveCoupledSphereODE>());}
}
