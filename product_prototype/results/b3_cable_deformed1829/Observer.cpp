// Read-only stock solver phase probe. No state/constraint/force edits.
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/simulation/events/BuildConstraintSystemEndEvent.h>
#include <sofa/simulation/events/SolveConstraintSystemEndEvent.h>
#include <fstream>
#include <iomanip>
class NativeCablePhase:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeCablePhase,sofa::core::objectmodel::BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 using RigidState=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<NativeCablePhase,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeCablePhase,Solver,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::SingleLink<NativeCablePhase,BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>cable;
 sofa::core::objectmodel::SingleLink<NativeCablePhase,RigidState,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>rigidBody;
 sofa::core::objectmodel::Data<std::string>filename;
 std::ofstream file;unsigned step=0;
 NativeCablePhase():body(initLink("body","Read-only actual cable points")),solver(initLink("solver","Actual constraint problem")),cable(initLink("cable","Read-only cable metadata")),rigidBody(initLink("rigidBody","Optional actual rigid parent")),filename(initData(&filename,std::string(),"filename","Exclusive phase journal")){f_listening.setValue(true);}
 void init()override{
  BaseObject::init();if(!body||!solver||!cable||std::ifstream(filename.getValue()))throw std::runtime_error("exclusive journal and links required");
  file.open(filename.getValue());file<<std::setprecision(17)<<"step,time_s,phase,q,v,free_q,free_v,J,lambda_Ns,cable_force_raw,parent_q,parent_v,parent_free_q,parent_J\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  const char*phase=nullptr;
  if(dynamic_cast<sofa::simulation::BuildConstraintSystemEndEvent*>(e))phase="build_end";
  if(dynamic_cast<sofa::simulation::SolveConstraintSystemEndEvent*>(e))phase="solve_end";
  if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))phase="accepted_end";
  if(!phase)return;
  file<<step<<','<<getContext()->getTime()<<','<<phase<<",\""<<body->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::freePosition)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::freeVelocity)->getValue()<<"\",\"";
  const auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
  for(auto row=J.begin();row!=J.end();++row)for(auto col=row.begin();col!=row.end();++col)file<<row.index()<<':'<<col.index()<<':'<<col.val()<<';';
  file<<"\",\"";const auto*p=solver->getConstraintProblem();if(p)for(int i=0;i<p->getDimension();++i)file<<p->f[i]<<' ';
  file<<"\",\"";const auto*d=cable->findData("force");file<<(d?d->getValueString():"NULL")<<'"';
  if(rigidBody){
   file<<",\""<<rigidBody->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<rigidBody->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<rigidBody->read(sofa::core::vec_id::read_access::freePosition)->getValue()<<"\",\"";
   const auto&P=rigidBody->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
   if(J.begin()!=J.end()){const auto selected=J.begin().index();for(auto row=P.begin();row!=P.end();++row)if(row.index()==selected)for(auto col=row.begin();col!=row.end();++col)file<<row.index()<<':'<<col.index()<<':'<<col.val()<<';';}
   file<<'"';
  }else file<<",NULL,NULL,NULL,NULL";
  file<<'\n';file.flush();
  if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))++step;
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripCablePhase";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only cable matrix/free/accepted phases").add<NativeCablePhase>());}
}
