#include "../models/film_shell/ReGripBDFSolver.h"
#include <sofa/component/odesolver/backward/EulerImplicitSolver.h>
#include <sofa/simulation/Node.h>
#include <iostream>
int main(){try{
 using namespace sofa::component::odesolver::backward;
 auto node=sofa::core::objectmodel::New<sofa::simulation::Node>();auto native=sofa::core::objectmodel::New<ReGripBDFSolver>();auto sdk=sofa::core::objectmodel::New<EulerImplicitSolver>();node->addObject(native);node->addObject(sdk);
 bool guarded=false;try{native->getPositionIntegrationFactor();}catch(const std::logic_error&){guarded=true;}if(!guarded)throw std::runtime_error("unsupported mode not rejected");
 native->d_nativeConstraintBE.setValue(true);native->d_order.setValue(1);native->d_theta.setValue(1);
 for(double dt:{.1,.01,.0005}){node->setDt(dt);for(int i=0;i<3;++i){if(native->getSolutionIntegrationFactor(i)!=sdk->getSolutionIntegrationFactor(i))throw std::runtime_error("solution compliance factor");for(int j=0;j<3;++j)if(native->getIntegrationFactor(i,j)!=sdk->getIntegrationFactor(i,j))throw std::runtime_error("input compliance factor");}}
 native->d_order.setValue(2);guarded=false;try{native->getVelocityIntegrationFactor();}catch(const std::logic_error&){guarded=true;}if(!guarded)throw std::runtime_error("multistep constraint use not rejected");
 std::cout<<"PASS native BE integration factors exactly match actual SDK Euler;unsupported BDF2 rejected;not contact dynamics qualification\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
