#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/component/constraint/lagrangian/solver/GenericConstraintSolver.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <limits>
namespace regrip_film_native {
using sofa::core::objectmodel::BaseLink;
class FilmNativeObserver final:public sofa::core::objectmodel::BaseObject {
public:
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;using Solver=sofa::component::constraint::lagrangian::solver::GenericConstraintSolver;
 SOFA_CLASS(FilmNativeObserver,sofa::core::objectmodel::BaseObject);
 sofa::core::objectmodel::SingleLink<FilmNativeObserver,State,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>body,sphere;
 sofa::core::objectmodel::SingleLink<FilmNativeObserver,Solver,BaseLink::FLAG_STOREPATH|BaseLink::FLAG_STRONGLINK>solver;
 sofa::core::objectmodel::Data<std::string>filename;sofa::core::objectmodel::Data<double>radius;
 State::VecCoord begin;std::ofstream stream;double last=-1;
 FilmNativeObserver():body(initLink("body","Actual mapped world-coordinate state,not displacement")),sphere(initLink("sphere","Explicit fixed sphere center state")),solver(initLink("solver","Public constraint multiplier data")),filename(initData(&filename,std::string(),"filename","Exclusive force-stage native journal")),radius(initData(&radius,8.,"radius","Declared sphere radius")){f_listening.setValue(true);}
 void init()override{BaseObject::init();if(!body||!sphere||!solver||radius.getValue()<=0)throw std::invalid_argument("native observer links/radius");std::ifstream old(filename.getValue());if(filename.getValue().empty()||old)throw std::runtime_error("native observer file exists/empty");stream.open(filename.getValue());stream<<std::setprecision(17)<<"time,dt,lambda_impulse,unmatched_jacobian_rows,body_force,sphere_force,body_moment_begin,body_moment_free,body_moment_accepted,min_vertex_gap,positions,free_positions,begin_positions\n";}
 State::VecDeriv impulses(State*state,const sofa::type::vector<SReal>&lambda,unsigned&unmatched)const{State::VecDeriv result(state->getSize());const auto&J=state->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();for(auto row=J.begin();row!=J.end();++row){if(row.index()>=lambda.size()){++unmatched;continue;}for(auto col=row.begin();col!=row.end();++col){if(col.index()>=result.size())throw std::runtime_error("native constraint column");result[col.index()]+=col.val()*lambda[row.index()];}}return result;}
 template<class V>void writeVector(const V&v){stream<<'"';for(const auto&x:v)stream<<x<<' ';stream<<'"';}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){begin=body->read(sofa::core::vec_id::read_access::position)->getValue();return;}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!stream)return;double t=getContext()->getTime();if(t==last)return;last=t;double dt=getContext()->getDt();const auto&lambda=solver->d_constraintForces.getValue();unsigned unmatched=0;auto bi=impulses(body.get(),lambda,unmatched),si=impulses(sphere.get(),lambda,unmatched);const auto&x=body->read(sofa::core::vec_id::read_access::position)->getValue();const auto&free=body->read(sofa::core::vec_id::read_access::freePosition)->getValue();const auto&center=sphere->read(sofa::core::vec_id::read_access::position)->getValue().at(0);sofa::type::Vec3 F{},S{},Mb{},Mf{},Ma{};double gap=std::numeric_limits<double>::infinity();
  for(unsigned i=0;i<bi.size();++i){auto force=bi[i]/dt;F+=force;if(begin.size()==bi.size())Mb+=sofa::type::cross(begin[i],force);if(free.size()==bi.size())Mf+=sofa::type::cross(free[i],force);Ma+=sofa::type::cross(x[i],force);gap=std::min(gap,(x[i]-center).norm()-radius.getValue());}for(const auto&i:si)S+=i/dt;
  stream<<t<<','<<dt<<',';writeVector(lambda);stream<<','<<unmatched<<',';
  if(unmatched)stream<<"null,null,null,null,null,";else{for(const auto&v:{F,S,Mb,Mf,Ma}){stream<<'"'<<v[0]<<' '<<v[1]<<' '<<v[2]<<'"'<<',';}}
  stream<<gap<<',';auto positions=[&](const State::VecCoord&q){stream<<'"';for(const auto&p:q)for(unsigned j=0;j<3;++j)stream<<p[j]<<' ';stream<<'"';};positions(x);stream<<',';positions(free);stream<<',';positions(begin);stream<<'\n';stream.flush();
 }
};
}
extern "C"{__attribute__((visibility("default")))void initExternalModule(){}__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmNativeObserver";}__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Read-only native child J^Tlambda/dt with begin/free/accepted geometry;row count is NOT active contact count").add<regrip_film_native::FilmNativeObserver>());}}
