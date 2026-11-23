#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/collision/NarrowPhaseDetection.h>
#include <sofa/core/collision/ContactManager.h>
#include <sofa/component/constraint/lagrangian/model/UnilateralLagrangianConstraint.h>
#include <set>
#include <sofa/core/CollisionModel.h>
#include <sofa/linearalgebra/FullMatrix.h>
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
class NativeDetectionPairs:public BaseObject {
public:
 SOFA_CLASS(NativeDetectionPairs,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeDetectionPairs,sofa::core::collision::NarrowPhaseDetection,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>narrow;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativeDetectionPairs():narrow(initLink("narrow","Public native detection output")),filename(initData(&filename,std::string(),"filename","Exclusive detector provenance")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!narrow||std::ifstream(filename.getValue()))throw std::runtime_error("unique detector journal required");file.open(filename.getValue());file<<std::setprecision(17)<<"accepted_time_s,model0,model1,pair_index,detected_point0,detected_point1\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;for(auto&pair:narrow->getDetectionOutputs()){auto*out=pair.second;if(!out)continue;for(unsigned k=0;k<out->size();++k)file<<getContext()->getTime()<<",\""<<pair.first.first->getPathName()<<"\",\""<<pair.first.second->getPathName()<<"\","<<k<<",\""<<out->getFirstPosition(k)<<"\",\""<<out->getSecondPosition(k)<<"\"\n";}file.flush();}
};
class NativeResponseRows:public BaseObject {
public:
 using Constraint=sofa::component::constraint::lagrangian::model::UnilateralLagrangianConstraint<sofa::defaulttype::Vec3Types>;
 using Point=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Body=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 SOFA_CLASS(NativeResponseRows,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeResponseRows,sofa::core::collision::ContactManager,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>manager;
 sofa::core::objectmodel::SingleLink<NativeResponseRows,Body,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeResponseRows,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativeResponseRows():manager(initLink("manager","Native contact responses")),body(initLink("body","Actual free rigid object")),solver(initLink("solver","Actual native multipliers")),filename(initData(&filename,std::string(),"filename","Exclusive direct response row journal")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!manager||!body||!solver||std::ifstream(filename.getValue()))throw std::runtime_error("unique linked response journal required");file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,model0,model1,response_name,constraint_path,first_row,row_id,lambda_Ns,object_impulse_Ns_Nms\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  auto constraints=getContext()->getObjects<Constraint>(sofa::core::objectmodel::BaseContext::SearchDown);
  auto&lambda=solver->d_constraintForces.getValue();auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();std::set<unsigned>claimed;
  for(auto&contact:manager->getContacts()){
   auto models=contact->getCollisionModels();Constraint*owner=nullptr;unsigned matches=0;
   for(auto*c:constraints)if(c->getName()==contact->getName()&&c->getContext()==contact->getContext()){
    auto*one=c->getMechModel1();auto*two=c->getMechModel2();auto prefix0=models.first->getContext()->getPathName()+"/";auto prefix1=models.second->getContext()->getPathName()+"/";
    if(one&&two&&one->getPathName().find(prefix0)==0&&two->getPathName().find(prefix1)==0){owner=c;++matches;}
   }
   if(matches!=1){std::ostringstream error;error<<"response name="<<contact->getName()<<" context="<<contact->getContext()->getName()<<" matches="<<matches<<" candidates=";for(auto*c:constraints)error<<c->getName()<<"@"<<c->getContext()->getName()<<';';throw std::runtime_error(error.str());}
   // Public API changes yetIntegrated metadata; never claim internal-history query purity.
   Constraint::VecConstraintBlockInfo blocks;Constraint::VecPersistentID ids;owner->getConstraintInfo(nullptr,blocks,ids);
   for(auto&block:blocks)for(int offset=0;offset<block.nbGroups*block.nbLines;++offset){
    unsigned id=block.const0+offset;if(block.parent!=owner||id>=lambda.size()||!claimed.insert(id).second)throw std::runtime_error("invalid or duplicate native response row");
    Body::Deriv impulse{};for(auto r=J.begin();r!=J.end();++r)if(r.index()==id)for(auto col=r.begin();col!=r.end();++col)impulse+=col.val()*lambda[id];
    file<<getContext()->getTime()<<",\""<<models.first->getPathName()<<"\",\""<<models.second->getPathName()<<"\",\""<<contact->getName()<<"\",\""<<owner->getPathName()<<"\","<<block.const0<<','<<id<<','<<lambda[id]<<",\""<<impulse<<"\"\n";
   }
  }file.flush();
 }
};
class NativeCableSequence:public BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(NativeCableSequence,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeCableSequence,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeCableSequence,BaseObject,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>cable0,cable1;
 sofa::core::objectmodel::Data<std::string> filename;
 sofa::core::objectmodel::Data<double>stroke,closing,hold,release;
 std::ofstream journal;double applied=0;
 sofa::core::objectmodel::Data<double> liftHeight;
 sofa::core::objectmodel::Data<double> maximumForceN;
 std::array<sofa::type::Vec3d,2> pullOrigin;
 NativeCableSequence():body(initLink("body","Native actual position DOFs")),cable0(initLink("cable0","Native SoftRobots CableConstraint")),cable1(initLink("cable1","Second native cable")),filename(initData(&filename,std::string(),"filename","Exclusive CSV")),stroke(initData(&stroke,.005,"stroke","Commanded shortening m;not actuator spec")),closing(initData(&closing,.5,"closing","Closing ramp end s")),hold(initData(&hold,1.,"hold","Hold end s")),release(initData(&release,1.5,"release","Release end s")),liftHeight(initData(&liftHeight,0.,"liftHeight","Driven palm/root upward movement m;NOT imposed finger/object pose")),maximumForceN(initData(&maximumForceN,-1.,"maximumForceN","Negative:legacy displacement input;nonnegative:force N converted to native impulse by actual dt;NOT a new force law")){f_listening.setValue(true);}
 static double smooth(double u){u=std::max(0.,std::min(1.,u));return u*u*u*(10+u*(-15+6*u));}
 void init()override{BaseObject::init();if(!body||!cable0||!cable1)throw std::runtime_error("explicit native state/cable links required");if(std::ifstream(filename.getValue()))throw std::runtime_error("immutable output exists");unsigned k=0;for(auto*b:{cable0.get(),cable1.get()}){auto*d=dynamic_cast<sofa::core::objectmodel::Data<sofa::type::Vec3d>*>(b->findData("pullPoint"));if(!d)throw std::runtime_error("typed cable pull point required");pullOrigin[k++]=d->getValue();if(maximumForceN.getValue()>=0&&!b->findData("valueType")->read("force"))throw std::runtime_error("native Cable force input not supported");}journal.open(filename.getValue());journal<<std::setprecision(17)<<"time_s,command_m,cable0_force_raw,cable1_force_raw,cable0_displacement_m,cable1_displacement_m,q_m,v_m_s,guide0_q_m,guide1_q_m,command_N,command_Ns\n";}
 std::string value(BaseObject*b,const char*key){auto*d=b->findData(key);if(auto*x=dynamic_cast<sofa::core::objectmodel::Data<double>*>(d)){std::ostringstream s;s<<std::setprecision(17)<<x->getValue();return s.str();}return d?d->getValueString():"NOT_MEASURED";}
 void handleEvent(sofa::core::objectmodel::Event*ev)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(ev)){double t=getContext()->getTime()+getContext()->getDt();double profile=t<closing.getValue()?smooth(t/closing.getValue()):t<hold.getValue()?1:t<release.getValue()?1-smooth((t-hold.getValue())/(release.getValue()-hold.getValue())):0;applied=maximumForceN.getValue()>=0?maximumForceN.getValue()*profile*getContext()->getDt():stroke.getValue()*profile;unsigned k=0;for(auto*b:{cable0.get(),cable1.get()}){auto point=pullOrigin[k++];point[2]+=liftHeight.getValue()*std::max(0.,std::min(1.,(t-1.)/.5));std::ostringstream p;p<<std::setprecision(17)<<point;b->findData("pullPoint")->read(p.str());}std::ostringstream s;s<<std::setprecision(17)<<applied;for(auto*b:{cable0.get(),cable1.get()}){auto*d=b->findData("value");if(!d||!d->read(s.str()))throw std::runtime_error("native CableConstraint.value input rejected");}}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(ev))return;
  journal<<getContext()->getTime()<<',';if(maximumForceN.getValue()>=0)journal<<"NULL";else journal<<applied;for(auto*b:{cable0.get(),cable1.get()})journal<<",\""<<value(b,"force")<<'"';for(auto*b:{cable0.get(),cable1.get()})journal<<",\""<<value(b,"displacement")<<'"';
  auto&q=body->read(sofa::core::vec_id::read_access::position)->getValue();auto&v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();for(auto*list:{&q,&v}){journal<<",\"";for(auto&p:*list)for(double d:p){if(!std::isfinite(d))throw std::runtime_error("nonfinite native state");journal<<d<<' ';}journal<<'"';}for(auto*b:{cable0.get(),cable1.get()}){auto*s=dynamic_cast<State*>(b->getContext()->getMechanicalState());if(!s)throw std::runtime_error("mapped guide state missing");journal<<",\"";for(auto&p:s->read(sofa::core::vec_id::read_access::position)->getValue())for(double d:p)journal<<d<<' ';journal<<'"';}journal<<',';if(maximumForceN.getValue()>=0)journal<<applied/getContext()->getDt()<<','<<applied;else journal<<"NULL,NULL";journal<<'\n';journal.flush();
 }
};
class NativePointJournal:public BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(NativePointJournal,BaseObject);
 sofa::core::objectmodel::SingleLink<NativePointJournal,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativePointJournal():body(initLink("body","Native driven support state")),filename(initData(&filename,std::string(),"filename","Exclusive public fixture log")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||std::ifstream(filename.getValue()))throw std::runtime_error("unique linked fixture journal required");file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,q,v\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;file<<getContext()->getTime()<<",\""<<body->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\"\n";file.flush();}
};
class NativeContactRows:public BaseObject {
public:
 using Film=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;using Rigid=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 SOFA_CLASS(NativeContactRows,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeContactRows,Film,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>film0,film1,film2;
 sofa::core::objectmodel::SingleLink<NativeContactRows,Rigid,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeContactRows,Rigid,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>guide0,guide1,guide2;
 sofa::core::objectmodel::SingleLink<NativeContactRows,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativeContactRows():film0(initLink("film0","Native parent0")),film1(initLink("film1","Optional parent1")),film2(initLink("film2","Optional parent2")),body(initLink("body","Native rigid body")),guide0(initLink("guide0","Optional rigid hardware0")),guide1(initLink("guide1","Optional rigid hardware1")),guide2(initLink("guide2","Optional rigid hardware2")),solver(initLink("solver","Native multipliers")),filename(initData(&filename,std::string(),"filename","Actual object row ownership")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!solver||!film0||std::ifstream(filename.getValue()))throw std::runtime_error("unique contact row observer links required");file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,row_id,film_mask,lambda_Ns,object_impulse_Ns_Nms,surface_mask,hardware_only_mask\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;
  auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();auto&lambda=solver->d_constraintForces.getValue();
  for(auto row=J.begin();row!=J.end();++row){
   if(row.index()>=lambda.size())throw std::runtime_error("actual row/multiplier mismatch");
   unsigned mask=0,k=0;
   for(auto*f:{film0.get(),film1.get(),film2.get()}){if(f){auto&F=f->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto r=F.begin();r!=F.end();++r)if(r.index()==row.index())for(auto c=r.begin();c!=r.end();++c)if(c.val().norm2()>0)mask|=1u<<k;}++k;}
   const unsigned surface=mask;k=0;
   for(auto*g:{guide0.get(),guide1.get(),guide2.get()}){if(g){auto&G=g->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto r=G.begin();r!=G.end();++r)if(r.index()==row.index())for(auto c=r.begin();c!=r.end();++c)for(unsigned d=0;d<6;++d)if(c.val()[d]!=0)mask|=1u<<k;}++k;}
   Rigid::Deriv impulse{};for(auto c=row.begin();c!=row.end();++c)impulse+=c.val()*lambda[row.index()];
   file<<getContext()->getTime()<<','<<row.index()<<','<<mask<<','<<lambda[row.index()]<<",\""<<impulse<<"\","<<surface<<','<<(mask&~surface)<<'\n';
  }file.flush();
 }
};
class NativeCableAudit:public BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(NativeCableAudit,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeCableAudit,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeCableAudit,BaseObject,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>cable;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativeCableAudit():body(initLink("body","Parent state")),cable(initLink("cable","Read-only cable metadata")),filename(initData(&filename,std::string(),"filename","Exclusive cable diagnostic")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!cable||std::ifstream(filename.getValue()))throw std::runtime_error("unique cable audit links required");file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,L0_m,L_internal_m,command,child_v,parent_J,child_J\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;file<<getContext()->getTime();for(auto key:{"cableInitialLength","cableLength","value"}){file<<",\"";auto*d=cable->findData(key);if(auto*x=dynamic_cast<sofa::core::objectmodel::Data<double>*>(d))file<<x->getValue();else file<<(d?d->getValueString():"NOT_MEASURED");file<<'"';}auto*child=dynamic_cast<State*>(cable->getContext()->getMechanicalState());if(!child)throw std::runtime_error("child state missing");file<<",\""<<child->read(sofa::core::vec_id::read_access::velocity)->getValue()<<'"';for(auto*s:{body.get(),child}){file<<",\"";auto&J=s->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row)for(auto col=row.begin();col!=row.end();++col)file<<row.index()<<':'<<col.index()<<':'<<col.val()<<';';file<<'"';}file<<'\n';file.flush();}
};
class NativeConstraintJournal:public BaseObject {
public:
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 SOFA_CLASS(NativeConstraintJournal,BaseObject);
 sofa::core::objectmodel::SingleLink<NativeConstraintJournal,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::Data<std::string>filename;std::ofstream file;
 NativeConstraintJournal():solver(initLink("solver","Read-only native solver")),filename(initData(&filename,std::string(),"filename","Exclusive constraint log")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!solver||std::ifstream(filename.getValue()))throw std::runtime_error("unique solver journal required");file.open(filename.getValue());file<<std::setprecision(17)<<"time_s,error,iterations,impulses_Ns\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))return;file<<getContext()->getTime()<<','<<solver->d_currentError.getValue()<<','<<solver->d_currentIterations.getValue()<<",\""<<solver->d_constraintForces.getValue()<<"\"\n";file.flush();}
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
 sofa::core::objectmodel::Data<bool>auditMass;
 NativeRigidJournal():body(initLink("body","Actual free Rigid3")),solver(initLink("solver","Public native impulse data")),center(initLink("center","Actual mapped sphere centre")),filename(initData(&filename,std::string(),"filename","Exclusive rigid journal")),auditMass(initData(&auditMass,false,"auditMass","Read-only public initial element mass matrices")){f_listening.setValue(true);}
 void bwdInit()override{BaseObject::bwdInit();if(!auditMass.getValue())return;auto*m=body->getContext()->getMass();auto name=filename.getValue()+".mass.json";if(!m||std::ifstream(name))throw std::runtime_error("unique public mass audit required");std::ofstream f(name);f<<std::setprecision(17)<<"{\"scope\":\"public initial element mass matrices,not global assembly certification\",\"elements\":[";for(sofa::Index i=0;i<body->getSize();++i){if(i)f<<',';sofa::linearalgebra::FullMatrix<SReal>A;m->getElementMass(i,&A);f<<"{\"mass_kg\":"<<m->getElementMass(i)<<",\"matrix\":[";for(sofa::Index r=0;r<A.rowSize();++r){if(r)f<<',';f<<'[';for(sofa::Index c=0;c<A.colSize();++c){if(c)f<<',';f<<A.element(r,c);}f<<']';}f<<"]}";}f<<"]}";}
 void init()override{BaseObject::init();if(!body||!solver||std::ifstream(filename.getValue()))throw std::runtime_error("rigid journal requires explicit state/solver/unique output");stream.open(filename.getValue());stream<<std::setprecision(17)<<"time_s,rigid_q,rigid_v,object_impulse_Ns_Nms,object_J_rows,solver_error,solver_iterations\n";}
 void handleEvent(sofa::core::objectmodel::Event*ev)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(ev))return;if(center){std::ofstream c(filename.getValue()+".center.csv",std::ios::app);c<<std::setprecision(17)<<getContext()->getTime()<<','<<center->read(sofa::core::vec_id::read_access::position)->getValue()<<'\n';}State::Deriv impulse{};unsigned rows=0;auto&lambda=solver->d_constraintForces.getValue();auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row){if(row.index()>=lambda.size())throw std::runtime_error("native object Jacobian/multiplier mismatch");++rows;for(auto col=row.begin();col!=row.end();++col)impulse+=col.val()*lambda[row.index()];}stream<<getContext()->getTime()<<",\""<<body->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<impulse<<"\","<<rows<<','<<solver->d_currentError.getValue()<<','<<solver->d_currentIterations.getValue()<<'\n';stream.flush();}
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripProductSequence";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Input and logging ONLY;native SOFA FEM/cable/solver").add<product::NativeCableSequence>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native Rigid3 journal").add<product::NativeRigidJournal>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native fixture journal").add<product::NativePointJournal>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native constraint convergence").add<product::NativeConstraintJournal>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only cable/parent Jacobian audit").add<product::NativeCableAudit>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only actual native contact row ownership").add<product::NativeContactRows>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only detector provenance").add<product::NativeDetectionPairs>());f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native response row provenance").add<product::NativeResponseRows>());}
}
