#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <fstream>
#include <iomanip>
namespace regrip {
using sofa::core::objectmodel::BaseObject;
using sofa::core::objectmodel::BaseLink;
class NativePairRows:public BaseObject {
public:
 SOFA_CLASS(NativePairRows,BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 sofa::core::objectmodel::SingleLink<NativePairRows,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> body;
 sofa::core::objectmodel::SingleLink<NativePairRows,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK> solver;
 sofa::core::objectmodel::Data<std::string> filename;
 std::ofstream f;
 NativePairRows():body(initLink("body","Actual rigid state,read only")),solver(initLink("solver","Actual native multipliers,read only")),filename(initData(&filename,std::string(),"filename","Unique direct-J journal")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!solver||std::ifstream(filename.getValue()))throw std::runtime_error("unique linked direct-J output required");f.open(filename.getValue());f<<std::setprecision(17)<<"time_s,row_id,column_id,lambda_Ns,J,free_q,free_v\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  const auto& J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
  const auto& l=solver->d_constraintForces.getValue();
  const auto& q=body->read(sofa::core::vec_id::read_access::freePosition)->getValue();
  const auto& v=body->read(sofa::core::vec_id::read_access::freeVelocity)->getValue();
  for(auto r=J.begin();r!=J.end();++r){if(r.index()>=l.size())throw std::runtime_error("row/multiplier mismatch");for(auto c=r.begin();c!=r.end();++c){if(c.index()>=q.size()||c.index()>=v.size())throw std::runtime_error("invalid body column");f<<getContext()->getTime()<<','<<r.index()<<','<<c.index()<<','<<l[r.index()]<<",\""<<c.val()<<"\",\""<<q[c.index()]<<"\",\""<<v[c.index()]<<"\"\n";}}
  f.flush();
 }
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char* getModuleName(){return "ReGripPairRows";}
__attribute__((visibility("default"))) const char* getModuleVersion(){return "1.0";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only direct native row/free state observer;no physics mutations").add<regrip::NativePairRows>());}
}
