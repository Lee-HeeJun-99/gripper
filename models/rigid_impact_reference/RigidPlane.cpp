#include "../film_impact/ProjectedImpact.h"
#include <Eigen/Geometry>
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseForceField.h>
#include <sofa/core/behavior/BaseProjectiveConstraintSet.h>
#include <sofa/core/BaseMapping.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <fstream>
#include <iomanip>
namespace regrip_rigid_reference {
void registerFilmRigidImpulse(sofa::core::ObjectFactory*);
class RigidSuppliedPlaneFlight final:public sofa::core::behavior::OdeSolver {
public:
 using Base=sofa::core::behavior::OdeSolver;
 using State=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 SOFA_CLASS(RigidSuppliedPlaneFlight,Base);
 sofa::core::objectmodel::SingleLink<RigidSuppliedPlaneFlight,State,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::Data<sofa::type::Vec3>contactArm,planeNormal;
 sofa::core::objectmodel::Data<double>planeOffset,restitution;
 sofa::core::objectmodel::Data<std::string>filename;
 Eigen::MatrixXd M;double mass=0,inertia=0;bool advanced=false;std::ofstream out;
 RigidSuppliedPlaneFlight():body(initLink("body","One FREE Rigid3 actual SOFA state")),contactArm(initData(&contactArm,sofa::type::Vec3(-1,1,0),"contactArm","Explicit body-fixed material contact point;NOT a whole collider")),planeNormal(initData(&planeNormal,sofa::type::Vec3(1,0,0),"planeNormal","Supplied unit plane normal")),planeOffset(initData(&planeOffset,0.,"planeOffset","Plane n.dot(x)=offset")),restitution(initData(&restitution,0.,"restitution","Explicit isolated Newton restitution assumption")),filename(initData(&filename,std::string(),"filename","Exclusive actual state/mass journal")){}
 static Eigen::Vector3d eigen(const sofa::type::Vec3&x){return {x[0],x[1],x[2]};}
 void init()override{
  Base::init();if(!body||body->getSize()!=1||getContext()->getGravity().norm()!=0)throw std::runtime_error("rigid reference requires one Rigid3/zero gravity");
  if(getContext()->getObjects<Base>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=1||!getContext()->getObjects<sofa::core::BaseMapping>(sofa::core::objectmodel::BaseContext::SearchDown).empty()||!getContext()->getObjects<sofa::core::behavior::BaseProjectiveConstraintSet>(sofa::core::objectmodel::BaseContext::SearchDown).empty())throw std::runtime_error("rigid reference excludes other ODEs,mappings and constraints");
  auto masses=getContext()->getObjects<sofa::core::behavior::BaseMass>(sofa::core::objectmodel::BaseContext::SearchDown);
  if(masses.size()!=1||masses[0]!=body->getContext()->getMass())throw std::runtime_error("rigid reference requires actual sole body mass");
  for(auto*f:getContext()->getObjects<sofa::core::behavior::BaseForceField>(sofa::core::objectmodel::BaseContext::SearchDown))if(dynamic_cast<sofa::core::behavior::BaseMass*>(f)!=masses[0])throw std::runtime_error("rigid reference is force/torque-free except explicit plane impact");
  sofa::linearalgebra::FullMatrix<double> actual(6,6);actual.clear();masses[0]->getElementMass(0,&actual);M.resize(6,6);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)M(i,j)=actual.element(i,j);
  mass=M(0,0);inertia=M(3,3);if(!(mass>0&&inertia>0)||!M.allFinite())throw std::runtime_error("rigid actual mass/inertia invalid");
  for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j){double expected=i==j?(i<3?mass:inertia):0;if(std::abs(M(i,j)-expected)>64*std::numeric_limits<double>::epsilon()*std::abs(expected))throw std::runtime_error("exact free flight currently requires isotropic actual inertia;anisotropy rejected");}
  if(filename.getValue().empty()||std::ifstream(filename.getValue())||std::ifstream(filename.getValue()+".mass.csv"))throw std::runtime_error("rigid journal exists/empty");
  out.open(filename.getValue());out<<std::setprecision(17)<<"time,pre_normal,post_normal,impulse,momentum_residual,angular_impulse_residual,impact_loss,flight_gap_lower,end_gap,K_before,K_after,initial_center,initial_quaternion,initial_velocity,final_center,final_quaternion,final_velocity\n";
  std::ofstream matrix(filename.getValue()+".mass.csv");matrix<<std::setprecision(17);for(unsigned i=0;i<6;++i){for(unsigned j=0;j<6;++j){if(j)matrix<<',';matrix<<M(i,j);}matrix<<'\n';}
 }
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(advanced||getContext()->getTime()!=0||!(dt>0&&dt<=.01))throw std::runtime_error("one supplied impact plus bounded isolated flight only;NOT general free-body contact");
  auto x=body->read(sofa::core::vec_id::read_access::position)->getValue();auto v=body->read(sofa::core::vec_id::read_access::velocity)->getValue();auto initial=x[0];auto before=v[0];
  double norm=0;for(unsigned d=0;d<4;++d)norm+=initial.getOrientation()[d]*initial.getOrientation()[d];Eigen::Vector3d n=eigen(planeNormal.getValue()),c=eigen(initial.getCenter()),r=eigen(initial.getOrientation().rotate(contactArm.getValue()));
  if(std::abs(norm-1)>128*std::numeric_limits<double>::epsilon()||std::abs(n.squaredNorm()-1)>128*std::numeric_limits<double>::epsilon())throw std::runtime_error("supplied quaternion and normal must be unit;no hidden normalization");
  double gap=n.dot(c+r)-planeOffset.getValue();if(std::abs(gap)>1e-10)throw std::runtime_error("supplied material point must start on plane;NOT automatic birth detection");
  Eigen::VectorXd incoming(6);incoming<<eigen(before.getVCenter()),eigen(before.getVOrientation());Eigen::MatrixXd J(1,6);J<<n.transpose(),r.cross(n).transpose();
  auto impact=regrip_film_impact::solve(M,J,incoming,restitution.getValue(),1e-12,1e-12);Eigen::Vector3d linear=impact.velocity.head(3),omega=impact.velocity.tail(3);
  double speed=omega.norm(),post=(J*impact.velocity)(0),second=n.dot(omega.cross(omega.cross(r)));
  double lower=gap+std::min(0.,post)*dt;
  if(second-dt*std::pow(speed,3)*r.norm()<0&&post-dt*speed*speed*r.norm()<0)throw std::runtime_error("isolated free-flight separation not certified;requires sustained solver");
  if(lower< -1e-10)throw std::runtime_error("free-flight certified gap bound failed");
  auto rotation=initial.getOrientation();for(unsigned d=0;d<4;++d)rotation[d]=d==3?1:0;
  if(speed>0){double s=std::sin(dt*speed/2)/speed;for(unsigned d=0;d<3;++d)rotation[d]=s*omega(d);rotation[3]=std::cos(dt*speed/2);}
  x[0].getOrientation()=rotation*initial.getOrientation();for(unsigned d=0;d<3;++d){x[0].getCenter()[d]+=dt*linear(d);v[0].getVCenter()[d]=linear(d);v[0].getVOrientation()[d]=omega(d);}
  Eigen::Vector3d finalPoint=eigen(x[0].getCenter())+eigen(x[0].getOrientation().rotate(contactArm.getValue()));double endGap=n.dot(finalPoint)-planeOffset.getValue();if(endGap< -1e-10)throw std::runtime_error("free-flight end gap failed");
  Eigen::Vector3d oldLinear=incoming.head<3>(),oldOmega=incoming.tail<3>();Eigen::Vector3d oldAngular=c.cross(mass*oldLinear)+inertia*oldOmega,newAngular=c.cross(mass*linear)+inertia*omega;
  double angular=(newAngular-oldAngular-(c+r).cross(n*impact.impulse(0))).norm();
  body->write(sofa::core::vec_id::write_access::position)->setValue(x);body->write(sofa::core::vec_id::write_access::velocity)->setValue(v);
  out<<dt<<','<<(J*incoming)(0)<<','<<post<<','<<impact.impulse(0)<<','<<impact.momentumResidual<<','<<angular<<','<<impact.energyLoss<<','<<lower<<','<<endGap<<','<<.5*incoming.dot(M*incoming)<<','<<.5*impact.velocity.dot(M*impact.velocity);
  auto vec=[&](auto values,unsigned count){out<<",\"";for(unsigned d=0;d<count;++d)out<<values[d]<<' ';out<<'"';};
  vec(initial.getCenter(),3);vec(initial.getOrientation(),4);vec(incoming,6);vec(x[0].getCenter(),3);vec(x[0].getOrientation(),4);vec(impact.velocity,6);out<<'\n';out.flush();advanced=true;
 }
};
}
extern "C"{
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripRigidImpactReference";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Actual free isotropic Rigid3 supplied material-point impact plus isolated exact flight;NOT film coupling/whole-body CCD/grasp").add<regrip_rigid_reference::RigidSuppliedPlaneFlight>());regrip_rigid_reference::registerFilmRigidImpulse(f);}
}
