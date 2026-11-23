#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/simulation/IntegrateEndEvent.h>
#include <sofa/simulation/events/BuildConstraintSystemEndEvent.h>
#include <sofa/simulation/events/SolveConstraintSystemEndEvent.h>
#include <fstream>
#include <iomanip>

class ReGripStepProbe:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ReGripStepProbe,sofa::core::objectmodel::BaseObject);
 using V=sofa::defaulttype::Vec3Types;using R=sofa::defaulttype::Rigid3Types;
 using State=sofa::core::behavior::MechanicalState<V>;using Rigid=sofa::core::behavior::MechanicalState<R>;
 using Field=sofa::core::behavior::ForceField<V>;using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 using Link=sofa::core::objectmodel::BaseLink;
 template<class T>using L=sofa::core::objectmodel::SingleLink<ReGripStepProbe,T,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>;
 L<State>body,freeBody;L<Rigid>guides;L<Field>elastic;L<Solver>solver;L<sofa::core::behavior::BaseMatrixLinearSystem>system;
 sofa::core::objectmodel::Data<std::string>filename;sofa::core::objectmodel::Data<double>sampleTime;
 bool active=false,done=false;std::ofstream phases;
 ReGripStepProbe():body(initLink("body","Full mapped FEM")),freeBody(initLink("freeBody","Independent free Vec3")),guides(initLink("guides","Actual rigid guides")),elastic(initLink("elastic","Native material field")),solver(initLink("solver","Actual Native constraint solver")),system(initLink("system","Actual Native linear system")),filename(initData(&filename,std::string(),"filename","Exclusive prefix")),sampleTime(initData(&sampleTime,.05,"sampleTime","Target end clock")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!freeBody||!guides||!elastic||!solver||!system||std::ifstream(filename.getValue()+".phases.csv"))throw std::runtime_error("explicit links and unique prefix required");phases.open(filename.getValue()+".phases.csv");phases<<std::setprecision(17)<<"time_s,phase,body_q,body_v,body_free_q,body_free_v,guide_q,guide_v,guide_free_q,guide_free_v,free_q,free_v,free_free_q,free_free_v,lambda\n";}
 template<class S>void state(S*s){phases<<",\""<<s->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<s->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<s->read(sofa::core::vec_id::read_access::freePosition)->getValue()<<"\",\""<<s->read(sofa::core::vec_id::read_access::freeVelocity)->getValue()<<"\"";}
 void phase(const char*name){phases<<getContext()->getTime()<<','<<name;state(body.get());state(guides.get());state(freeBody.get());phases<<",\""<<solver->d_constraintForces.getValue()<<"\"\n";phases.flush();
  std::ofstream j(filename.getValue()+"."+name+".J.csv");j<<std::setprecision(17)<<"state,row,column,values\n";
  auto dump=[&](auto*s,const char*tag){const auto&J=s->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row)for(auto col=row.begin();col!=row.end();++col)j<<tag<<','<<row.index()<<','<<col.index()<<",\""<<col.val()<<"\"\n";};dump(guides.get(),"guide");dump(freeBody.get(),"free");
 }
 void beginK(){
  const auto q=body->read(sofa::core::vec_id::read_access::position)->getValue();const auto v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();
  Field::DataVecCoord x;Field::DataVecDeriv vel,f;x.setValue(q);vel.setValue(v);f.setValue(V::VecDeriv(q.size()));elastic->addForce(sofa::core::MechanicalParams::defaultInstance(),f,x,vel);
  sofa::linearalgebra::FullMatrix<double>K(q.size()*3,q.size()*3);K.clear();unsigned offset=0;elastic->addKToMatrix(&K,-1.,offset);
  std::ofstream o(filename.getValue()+".previous_K.csv");o<<std::setprecision(17)<<"i,j,K_N_per_m\n";for(unsigned i=0;i<q.size()*3;++i)for(unsigned j=0;j<q.size()*3;++j)if(K.element(i,j)!=0)o<<i<<','<<j<<','<<K.element(i,j)<<'\n';
  std::ofstream force(filename.getValue()+".previous_elastic_force.csv");force<<std::setprecision(17)<<"node,force_N\n";for(unsigned i=0;i<q.size();++i)force<<i<<",\""<<f.getValue()[i]<<"\"\n";
  if(q!=body->read(sofa::core::vec_id::read_access::position)->getValue()||v!=body->read(sofa::core::vec_id::read_access::velocity)->getValue())throw std::runtime_error("private query changed state");
 }
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  if(done)return;
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(e)){
   active=std::abs(getContext()->getTime()+getContext()->getDt()-sampleTime.getValue())<1e-12;
   if(active){beginK();phase("begin");}return;
  }
  if(!active)return;
  if(dynamic_cast<sofa::simulation::IntegrateEndEvent*>(e))phase("integrate_end");
  if(dynamic_cast<sofa::simulation::BuildConstraintSystemEndEvent*>(e))phase("build_end");
  if(dynamic_cast<sofa::simulation::SolveConstraintSystemEndEvent*>(e))phase("solve_end");
  if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e)){
   phase("accepted_end");const auto*A=system->getSystemBaseMatrix();if(!A)throw std::runtime_error("Native matrix missing");
   std::ofstream o(filename.getValue()+".A.csv");o<<std::setprecision(17)<<"i,j,A\n";for(sofa::Index i=0;i<A->rowSize();++i)for(sofa::Index j=0;j<A->colSize();++j)if(A->element(i,j)!=0)o<<i<<','<<j<<','<<A->element(i,j)<<'\n';done=true;
  }
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripStepProbe";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only sampled previous-state/effective-matrix/phase diagnostic").add<ReGripStepProbe>());}
}
