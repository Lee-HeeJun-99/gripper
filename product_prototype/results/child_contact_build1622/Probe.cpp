#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/component/constraint/lagrangian/model/UnilateralLagrangianConstraint.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/simulation/events/BuildConstraintSystemEndEvent.h>
#include <sofa/simulation/events/SolveConstraintSystemEndEvent.h>
#include <fstream>
#include <iomanip>
class ReGripContactGapProbe:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(ReGripContactGapProbe,sofa::core::objectmodel::BaseObject);
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<ReGripContactGapProbe,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<ReGripContactGapProbe,Solver,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<double>startTime,endTime;
 sofa::core::objectmodel::Data<bool>contactChildren;
 std::ofstream states,rows,matrix,jacobian,children;
 ReGripContactGapProbe():body(initLink("body","Observed actual rigid layer")),solver(initLink("solver","Existing Native constraint problem")),filename(initData(&filename,std::string(),"filename","Exclusive read-only diagnostic prefix")),startTime(initData(&startTime,0.0,"startTime","Read-only sampling window start")),endTime(initData(&endTime,.00121,"endTime","Read-only sampling window end;legacy default preserved")),contactChildren(initData(&contactChildren,false,"contactChildren","Optional read-only actual mapped contact point current/free positions and child Jacobian")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!solver||std::ifstream(filename.getValue()+".states.csv"))throw std::runtime_error("unique linked contact gap observer required");states.open(filename.getValue()+".states.csv");rows.open(filename.getValue()+".rows.csv");matrix.open(filename.getValue()+".W.csv");jacobian.open(filename.getValue()+".J.csv");for(auto*f:{&states,&rows,&matrix,&jacobian})*f<<std::setprecision(17);states<<"time_s,phase,q,v,free_q,free_v\n";rows<<"time_s,phase,row,dFree,f\n";matrix<<"time_s,phase,i,j,W\n";jacobian<<"time_s,phase,row,column,values\n";}
 void handleEvent(sofa::core::objectmodel::Event*e)override{
  const char*phase=nullptr;if(dynamic_cast<sofa::simulation::BuildConstraintSystemEndEvent*>(e))phase="build_end";if(dynamic_cast<sofa::simulation::SolveConstraintSystemEndEvent*>(e))phase="solve_end";if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e))phase="accepted_end";if(!phase||getContext()->getTime()<startTime.getValue()||getContext()->getTime()>endTime.getValue())return;
  double t=getContext()->getTime();states<<t<<','<<phase<<",\""<<body->read(sofa::core::vec_id::read_access::position)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::velocity)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::freePosition)->getValue()<<"\",\""<<body->read(sofa::core::vec_id::read_access::freeVelocity)->getValue()<<"\"\n";
  const auto*problem=solver->getConstraintProblem();if(!problem)throw std::runtime_error("Native constraint problem missing");const int n=problem->getDimension();if(problem->dFree.size()<n||problem->f.size()<n)throw std::runtime_error("invalid native problem dimensions");
  for(int i=0;i<n;++i){rows<<t<<','<<phase<<','<<i<<','<<problem->dFree[i]<<','<<problem->f[i]<<'\n';for(int j=0;j<n;++j)if(problem->W.element(i,j)!=0)matrix<<t<<','<<phase<<','<<i<<','<<j<<','<<problem->W.element(i,j)<<'\n';}
  const auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row)for(auto col=row.begin();col!=row.end();++col)jacobian<<t<<','<<phase<<','<<row.index()<<','<<col.index()<<",\""<<col.val()<<"\"\n";
  if(contactChildren.getValue()){
   using C=sofa::component::constraint::lagrangian::model::UnilateralLagrangianConstraint<sofa::defaulttype::Vec3Types>;
   using S=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
   if(!children.is_open()){if(std::ifstream(filename.getValue()+".children.csv"))throw std::runtime_error("unique child journal required");children.open(filename.getValue()+".children.csv");children<<std::setprecision(17)<<"time_s,phase,constraint,side,row,column,q,free_q,J\n";}
   for(auto*c:getContext()->getObjects<C>(sofa::core::objectmodel::BaseContext::SearchDown)){
    int side=0;for(auto*base:{c->getMechModel1(),c->getMechModel2()}){
     auto*s=dynamic_cast<S*>(base);if(!s)throw std::runtime_error("typed actual contact state missing");
     const auto&q=s->read(sofa::core::vec_id::read_access::position)->getValue();const auto&fq=s->read(sofa::core::vec_id::read_access::freePosition)->getValue();const auto&cj=s->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
     for(auto r=cj.begin();r!=cj.end();++r)for(auto col=r.begin();col!=r.end();++col){if(col.index()>=q.size()||col.index()>=fq.size())throw std::runtime_error("contact current/free point index missing");children<<t<<','<<phase<<",\""<<c->getPathName()<<"\","<<side<<','<<r.index()<<','<<col.index()<<",\""<<q[col.index()]<<"\",\""<<fq[col.index()]<<"\",\""<<col.val()<<"\"\n";}
     ++side;
    }
   }children.flush();
  }
  states.flush();rows.flush();matrix.flush();jacobian.flush();
 }
};
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripContactGapProbe";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only Native constraint problem and rigid phase diagnostic").add<ReGripContactGapProbe>());}
}
