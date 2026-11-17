#include "../film_impact/FilmProjection.h"
#include <Eigen/Geometry>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/MechanicalOperations.h>
#include <fstream>
#include <iomanip>
namespace regrip_rigid_reference {
class FilmRigidSharedImpulse final:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(FilmRigidSharedImpulse,sofa::core::objectmodel::BaseObject);
 using Film=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Rigid=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<FilmRigidSharedImpulse,Film,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>root;
 sofa::core::objectmodel::SingleLink<FilmRigidSharedImpulse,Rigid,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<FilmRigidSharedImpulse,sofa::core::objectmodel::BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>field;
 sofa::core::objectmodel::Data<unsigned>node;
 sofa::core::objectmodel::Data<sofa::type::Vec3>normal,bodyArm;
 sofa::core::objectmodel::Data<std::string>filename;
 bool done=false;
 FilmRigidSharedImpulse():root(initLink("root","Actual independent film displacement state")),body(initLink("body","Actual free Rigid3 state")),field(initLink("field","Actual FilmRailTendon")),node(initData(&node,102u,"node","One supplied film material node,NOT surface CCD")),normal(initData(&normal,sofa::type::Vec3(0,0,1),"normal","Explicit unit contact normal on film")),bodyArm(initData(&bodyArm,sofa::type::Vec3(1,1,-1),"bodyArm","Supplied coincident body material contact point")),filename(initData(&filename,std::string(),"filename","Exclusive zero-time shared impulse journal")){f_listening.setValue(true);}
 template<class T>T parameter(const char*name){auto*d=dynamic_cast<sofa::core::objectmodel::Data<T>*>(field->findData(name));if(!d)throw std::runtime_error("actual film parameter unavailable");return d->getValue();}
 static Eigen::Vector3d eigen(const sofa::type::Vec3&v){return {v[0],v[1],v[2]};}
 void init()override{
  BaseObject::init();if(!root||!body||!field||field->getClassName()!="FilmRailTendon"||body->getSize()!=1||getContext()->getGravity().norm()!=0)throw std::runtime_error("explicit actual film/free rigid/zero gravity links required");
  if(!getContext()->getObjects<sofa::core::behavior::OdeSolver>(sofa::core::objectmodel::BaseContext::SearchDown).empty())throw std::runtime_error("shared impulse reference is ZERO TIME only;external integration rejected");
  auto masses=getContext()->getObjects<sofa::core::behavior::BaseMass>(sofa::core::objectmodel::BaseContext::SearchDown);
  if(masses.size()!=2||!field->getContext()->getMass()||!body->getContext()->getMass())throw std::runtime_error("exactly actual film and body mass required");
  if(filename.getValue().empty())throw std::runtime_error("shared impulse journal empty");for(auto suffix:{"",".matrix.csv",".jacobian.csv",".states.csv"})if(std::ifstream(filename.getValue()+suffix))throw std::runtime_error("shared impulse journal exists");
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(done||!dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event))return;if(getContext()->getTime()!=0)throw std::runtime_error("supplied shared impulse time0 required");
  using namespace regrip_film_native;using namespace regrip_film_impact;
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<Film*>(field->getContext()->getMechanicalState());if(!local)throw std::runtime_error("actual film local state missing");
  Assembly model(parameter<unsigned>("nx"));model.guideIntervals=parameter<unsigned>("guideIntervals");model.guideOffset=parameter<double>("guideOffset");model.bondK=parameter<double>("bondStiffness");model.rootGuideSecondOrder=parameter<bool>("rootGuideSecondOrder");
  std::vector<Point>q(model.size()),v(model.size()),zero(model.size());std::vector<double>mass(model.size());auto positions=local->read(sofa::core::vec_id::read_access::position)->getValue();auto velocities=local->read(sofa::core::vec_id::read_access::velocity)->getValue();
  if(positions.size()!=model.size()||node.getValue()>=model.size())throw std::runtime_error("shared impulse geometry dimension");
  for(unsigned i=0;i<q.size();++i){mass[i]=field->getContext()->getMass()->getElementMass(i);for(unsigned d=0;d<3;++d){q[i][d]=positions[i][d];v[i][d]=velocities[i][d];}}
  // h is used only to construct the EXISTING root map;no force/time update
  // is evaluated in this explicitly zero-time impulse API.
  CoupledPlaneStep map(model,mass,getContext()->getDt(),0,0,q,v,zero,0);
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue();auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue();auto initial=bv[0];Eigen::Vector3d c=eigen(bx[0].getCenter()),r=eigen(bx[0].getOrientation().rotate(bodyArm.getValue())),n=eigen(normal.getValue());
  double quaternionNorm=0;for(unsigned d=0;d<4;++d)quaternionNorm+=bx[0].getOrientation()[d]*bx[0].getOrientation()[d];if(std::abs(quaternionNorm-1)>128*std::numeric_limits<double>::epsilon())throw std::runtime_error("shared actual quaternion must be unit;no normalization");
  auto rest=model.rest();Eigen::Vector3d point(rest[node.getValue()][0]+q[node.getValue()][0],rest[node.getValue()][1]+q[node.getValue()][1],rest[node.getValue()][2]+q[node.getValue()][2]);
  if((point-c-r).norm()>1e-10||std::abs(n.squaredNorm()-1)>1e-12)throw std::runtime_error("supplied material points must coincide with unit normal;no position correction");
  sofa::linearalgebra::FullMatrix<double>actual(6,6);actual.clear();body->getContext()->getMass()->getElementMass(0,&actual);Eigen::MatrixXd Mb(6,6);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)Mb(i,j)=actual.element(i,j);
  double objectMass=Mb(0,0),inertia=Mb(3,3);if(!(objectMass>0&&inertia>0))throw std::runtime_error("positive body mass/inertia required");for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)if(Mb(i,j)!=(i==j?(i<3?objectMass:inertia):0))throw std::runtime_error("shared API currently requires isotropic body inertia;guard not bypassed");
  Eigen::MatrixXd Mf=filmMass(map),M=Eigen::MatrixXd::Zero(map.freeSize+6,map.freeSize+6);M.topLeftCorner(map.freeSize,map.freeSize)=Mf;M.bottomRightCorner(6,6)=Mb;
  std::vector<Point>g(model.size());for(unsigned d=0;d<3;++d)g[node.getValue()][d]=n(d);Eigen::MatrixXd J(1,map.freeSize+6);J.leftCols(map.freeSize)=filmRow(map,g);J.rightCols(6)<<-n.transpose(),-r.cross(n).transpose();
  Eigen::VectorXd incoming(map.freeSize+6);incoming.head(map.freeSize)=map.pack(v);incoming.tail(6)<<eigen(initial.getVCenter()),eigen(initial.getVOrientation());auto impact=solve(M,J,incoming,0,1e-12,1e-12);auto repeat=solve(M,J,incoming,0,1e-12,1e-12);
  if(impact.velocity!=repeat.velocity||impact.impulse!=repeat.impulse)throw std::runtime_error("impure shared impulse query");
  if(!impact.velocity.allFinite()||!impact.impulse.allFinite()||!std::isfinite(impact.energyLoss))throw std::runtime_error("nonfinite shared impulse rejected before commit");
  auto after=map.expand(impact.velocity.head(map.freeSize));Eigen::Vector3d vb=impact.velocity.segment<3>(map.freeSize),wb=impact.velocity.tail<3>();double p=impact.impulse(0);
  Eigen::Vector3d rootReaction=Eigen::Vector3d::Zero(),rootMoment=rootReaction,linearBefore=rootReaction,linearAfter=rootReaction,angularBefore=rootReaction,angularAfter=rootReaction;
  for(unsigned i=0;i<v.size();++i){Eigen::Vector3d old(v[i][0],v[i][1],v[i][2]),next(after[i][0],after[i][1],after[i][2]),x(rest[i][0]+q[i][0],rest[i][1]+q[i][1],rest[i][2]+q[i][2]);Eigen::Vector3d reaction=mass[i]*(next-old);if(i==node.getValue())reaction-=p*n;rootReaction+=reaction;rootMoment+=x.cross(reaction);linearBefore+=mass[i]*old;linearAfter+=mass[i]*next;angularBefore+=x.cross(mass[i]*old);angularAfter+=x.cross(mass[i]*next);}
  linearBefore+=objectMass*eigen(initial.getVCenter());linearAfter+=objectMass*vb;angularBefore+=c.cross(objectMass*eigen(initial.getVCenter()))+inertia*eigen(initial.getVOrientation());angularAfter+=c.cross(objectMass*vb)+inertia*wb;
  double linearError=(linearAfter-linearBefore-rootReaction).norm(),angularError=(angularAfter-angularBefore-rootMoment).norm();
  if(impact.momentumResidual>1e-12||linearError>1e-12||angularError>1e-12)throw std::runtime_error("shared impulse momentum gate rejected before commit");
  auto rootV=root->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned a=0;a<map.index.size();++a)if(map.index[a]>=0&&map.weight[a]==1)rootV[a/3][a%3]=after[a/3][a%3];root->write(sofa::core::vec_id::write_access::velocity)->setValue(rootV);for(unsigned d=0;d<3;++d){bv[0].getVCenter()[d]=vb(d);bv[0].getVOrientation()[d]=wb(d);}body->write(sofa::core::vec_id::write_access::velocity)->setValue(bv);mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto actualFilm=local->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<v.size();++i)for(unsigned d=0;d<3;++d)if(actualFilm[i][d]!=after[i][d])throw std::runtime_error("actual shared mapped velocity mismatch");
  const auto&actualBody=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d)if(actualBody.getVCenter()[d]!=vb(d)||actualBody.getVOrientation()[d]!=wb(d))throw std::runtime_error("actual shared body velocity mismatch");
  auto matrix=[&](const char*suffix,const Eigen::MatrixXd&values){std::ofstream file(filename.getValue()+suffix);file<<std::setprecision(17);for(int i=0;i<values.rows();++i){for(int j=0;j<values.cols();++j){if(j)file<<',';file<<values(i,j);}file<<'\n';}};matrix(".matrix.csv",M);matrix(".jacobian.csv",J);
  std::ofstream states(filename.getValue()+".states.csv");states<<std::setprecision(17)<<"stage,reduced_velocity\n";for(auto pair:{std::make_pair("before",incoming),std::make_pair("after",impact.velocity)}){states<<pair.first<<",\"";for(int i=0;i<pair.second.size();++i)states<<pair.second(i)<<' ';states<<"\"\n";}
  std::ofstream out(filename.getValue());out<<std::setprecision(17)<<"time,node,pre_normal,post_normal,impulse,momentum_residual,linear_balance_with_root,angular_balance_with_root,root_impulse_norm,root_moment_norm,impact_loss,object_mass,inertia,body_vx,body_vy,body_vz,body_wx,body_wy,body_wz\n";
  out<<0<<','<<node.getValue()<<','<<(J*incoming)(0)<<','<<impact.normalVelocity(0)<<','<<p<<','<<impact.momentumResidual<<','<<linearError<<','<<angularError<<','<<rootReaction.norm()<<','<<rootMoment.norm()<<','<<impact.energyLoss<<','<<objectMass<<','<<inertia;for(unsigned d=0;d<3;++d)out<<','<<vb(d);for(unsigned d=0;d<3;++d)out<<','<<wb(d);out<<'\n';done=true;
 }
};
void registerFilmRigidImpulse(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Actual film/root-mapped and free-Rigid3 shared instantaneous material-point impulse API;NOT joint dynamics/CCD/grasp").add<FilmRigidSharedImpulse>());}
}
