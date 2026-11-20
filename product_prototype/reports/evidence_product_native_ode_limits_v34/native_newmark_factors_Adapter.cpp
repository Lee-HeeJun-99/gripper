// Narrow integration-factor contract adapter ONLY. The stock Native solve()
// remains inherited/unmodified. No state/force/contact/ODE algorithm is added.
#include <sofa/component/odesolver/backward/NewmarkImplicitSolver.h>
#include <sofa/core/ObjectFactory.h>
#include <stdexcept>
namespace regrip {
using Native=sofa::component::odesolver::backward::NewmarkImplicitSolver;
class ReGripNewmarkFactors:public Native {
public:
 SOFA_CLASS(ReGripNewmarkFactors,Native);
 void init()override{
  Native::init();
  if(d_gamma.getValue()!=SReal(.5)||d_beta.getValue()!=SReal(.25))
   throw std::runtime_error("Factor contract is restricted to average-acceleration Newmark gamma=.5,beta=.25");
 }
 // q_new=q_old+h*v_old+(h/2)*(v_new-v_old).
 // A velocity correction from a constraint therefore changes q by h/2*dv.
 SReal getPositionIntegrationFactor()const override{return getContext()->getDt()/2;}
 SReal getSolutionIntegrationFactor(int derivative)const override{
  return derivative==0?getContext()->getDt()/2:Native::getSolutionIntegrationFactor(derivative);
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripNewmarkFactors";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Restricted Native Newmark factor-interface adapter;stock solve inherited,no state correction or new physical solver").add<regrip::ReGripNewmarkFactors>());}
}
