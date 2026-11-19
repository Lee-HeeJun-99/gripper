#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <fstream>
#include <iomanip>
#include <cmath>
namespace product {
using sofa::core::objectmodel::BaseObject;using sofa::core::objectmodel::BaseLink;
class NativeCableSequence:public BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(NativeCableSequence,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeCableSequence,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeCableSequence,BaseObject,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>cable0,cable1;
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::objectmodel::Data<double>stroke,closing,hold,release;
 std::ofstream journal;double applied=0;
 NativeCableSequence():body(initLink("body","Native actual position DOFs")),cable0(initLink("cable0","Native SoftRobots CableConstraint")),cable1(initLink("cable1","Second native cable")),filename(initData(&filename,std::string(),"filename","Exclusive CSV")),stroke(initData(&stroke,.005,"stroke","Commanded shortening m;not actuator spec")),closing(initData(&closing,.5,"closing","Closing ramp end s")),hold(initData(&hold,1.,"hold","Hold end s")),release(initData(&release,1.5,"release","Release end s")){f_listening.setValue(true);}
 static double smooth(double u){u=std::max(0.,std::min(1.,u));return u*u*u*(10+u*(-15+6*u));}
 void init()override{BaseObject::init();if(!body||!cable0||!cable1)throw std::runtime_error("explicit native state/cable links required");if(std::ifstream(filename.getValue()))throw std::runtime_error("immutable output exists");journal.open(filename.getValue());journal<<std::setprecision(17)<<"time_s,command_m,cable0_force_raw,cable1_force_raw,cable0_displacement_m,cable1_displacement_m,q_m,v_m_s,guide0_q_m,guide1_q_m\n";}
 std::string value(BaseObject*b,const char*key){auto*d=b->findData(key);if(auto*x=dynamic_cast<sofa::core::objectmodel::Data<double>*>(d)){std::ostringstream s;s<<std::setprecision(17)<<x->getValue();return s.str();}return d?d->getValueString():"NOT_MEASURED";}
 void handleEvent(sofa::core::objectmodel::Event*ev)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(ev)){double t=getContext()->getTime()+getContext()->getDt();applied=stroke.getValue()*(t<closing.getValue()?smooth(t/closing.getValue()):t<hold.getValue()?1:t<release.getValue()?1-smooth((t-hold.getValue())/(release.getValue()-hold.getValue())):0);std::ostringstream s;s<<std::setprecision(17)<<applied;for(auto*b:{cable0.get(),cable1.get()}){auto*d=b->findData("value");if(!d||!d->read(s.str()))throw std::runtime_error("native CableConstraint.value input rejected");}}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(ev))return;
  journal<<getContext()->getTime()<<','<<applied;for(auto*b:{cable0.get(),cable1.get()})journal<<",\""<<value(b,"force")<<'"';for(auto*b:{cable0.get(),cable1.get()})journal<<",\""<<value(b,"displacement")<<'"';
  auto&q=body->read(sofa::core::vec_id::read_access::position)->getValue();auto&v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();for(auto*list:{&q,&v}){journal<<",\"";for(auto&p:*list)for(double d:p){if(!std::isfinite(d))throw std::runtime_error("nonfinite native state");journal<<d<<' ';}journal<<'"';}for(auto*b:{cable0.get(),cable1.get()}){auto*s=dynamic_cast<State*>(b->getContext()->getMechanicalState());if(!s)throw std::runtime_error("mapped guide state missing");journal<<",\"";for(auto&p:s->read(sofa::core::vec_id::read_access::position)->getValue())for(double d:p)journal<<d<<' ';journal<<'"';}journal<<'\n';journal.flush();
 }
};
class NativeRigidJournal:public BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 using CenterState=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(NativeRigidJournal,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeRigidJournal,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeRigidJournal,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::SingleLink<NativeRigidJournal,CenterState,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>center;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream stream;
 NativeRigidJournal():body(initLink("body","Actual free Rigid3")),solver(initLink("solver","Public native impulse data")),center(initLink("center","Actual mapped sphere centre")),filename(initData(&filename,std::string(),"filename","Exclusive rigid journal")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!solver||std::ifstream(filename.getValue()))throw std::runtime_error("rigid journal requires explicit state/solver/unique output");stream.open(filename.getValue());stream<<std::setprecision(17)<<"time_s,rigid_q,rigid_v,object_impulse_Ns_Nms,object_J_rows,solver_error,solver_iterations\n";}
 void handleEvent(sofa::core::objectmodel::Event*ev)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(ev))return;if(center){std::ofstream c(filename.getValue()+".center.csv",std::ios::app);c<<std::setprecision(17)<<getContext()->getTime()<<','<<center->read(sofa::core::vec_id::read_access::position)->getValue()<<'\n';}State::Deriv impulse{};unsigned rows=0;auto&lambda=solver->d_constraintForces.getValue();auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row){if(row.index()>=lambda.size())throw std::runtime_error("native object Jacobian/multiplier mismatch");++rows;for(auto col=row.begin();col!=row.end();++col)impulse+=col.val()*lambda[row.index()];}stream<<getContext()->getTime()<<",\""<<body->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<impulse<<"\","<<rows<<','<<solver->d_currentError.getValue()<<','<<solver->d_currentIterations.getValue()<<'\n';stream.flush();}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripProductSequence";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Input and logging ONLY;native SOFA FEM/cable/solver").add<product::NativeCableSequence>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native Rigid3 journal").add<product::NativeRigidJournal>());}
}
