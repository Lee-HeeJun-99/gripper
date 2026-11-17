#include "../film_sphere_contact/ClosestPrimitive.h"
#include <Eigen/Geometry>
#include <sofa/core/objectmodel/BaseObject.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseProjectiveConstraintSet.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip_rigid_reference {
// PASSIVE observer for a SEPARATE Native free-body control. It does not turn
// the fixed-object event owner into a moving-body solver or change its guards.
class NativeFreeBodyProbe final:public sofa::core::objectmodel::BaseObject {
public:
 SOFA_CLASS(NativeFreeBodyProbe,sofa::core::objectmodel::BaseObject);
 using Rigid=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;
 using Vec=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<NativeFreeBodyProbe,Rigid,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<NativeFreeBodyProbe,Vec,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>surface,sphere;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<double>radius;
 sofa::core::objectmodel::Data<unsigned>maxSteps;
 Eigen::MatrixXd M;Eigen::Vector3d previousPosition,previousLinear,previousOmega;Vec::VecCoord previousSurface;double damping=0;unsigned steps=0;std::ofstream out;
 NativeFreeBodyProbe():body(initLink("body","Actual free Rigid3 state")),surface(initLink("surface","Actual mapped film world state")),sphere(initLink("sphere","Actual mapped sphere center")),filename(initData(&filename,std::string(),"filename","Exclusive passive Native control journal")),radius(initData(&radius,8.01,"radius","Declared midsurface buffered radius")),maxSteps(initData(&maxSteps,64u,"maxSteps","Passive observer step budget;explicit profiled campaign may choose <=1024")){f_listening.setValue(true);}
 static Eigen::Vector3d eigen(const sofa::type::Vec3&v){return {v[0],v[1],v[2]};}
 void init()override{
  BaseObject::init();if(!body||body->getSize()!=1||!surface||!sphere||sphere->getSize()!=1||getContext()->getGravity().norm()!=0)throw std::runtime_error("Native free-body probe links/zero gravity required");
  for(auto*constraint:getContext()->getObjects<sofa::core::behavior::BaseProjectiveConstraintSet>(sofa::core::objectmodel::BaseContext::SearchDown))if(constraint->getContext()->getMechanicalState()==body.get())throw std::runtime_error("body must remain free6DOF;body constraints rejected");
  auto*ode=getContext()->get<sofa::core::objectmodel::BaseObject>(std::string("ode"));auto*data=ode?dynamic_cast<sofa::core::objectmodel::Data<double>*>(ode->findData("rayleighMass")):nullptr;if(!data)throw std::runtime_error("actual Native BE damping data required");damping=data->getValue();
  auto*mass=body->getContext()->getMass();if(!mass)throw std::runtime_error("actual free body mass required");sofa::linearalgebra::FullMatrix<double>matrix(6,6);matrix.clear();mass->getElementMass(0,&matrix);M.resize(6,6);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)M(i,j)=matrix.element(i,j);
  if(!M.allFinite()||M(0,0)<=0||M(3,3)<=0)throw std::runtime_error("invalid actual body mass");
  for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)if(M(i,j)!=(i==j?(i<3?M(0,0):M(3,3)):0))throw std::runtime_error("probe inference requires isotropic actual mass");
  if(maxSteps.getValue()==0||maxSteps.getValue()>1024)throw std::runtime_error("passive Native observer budget must be1..1024");
  if(filename.getValue().empty()||std::ifstream(filename.getValue())||std::ifstream(filename.getValue()+".mass.csv"))throw std::runtime_error("Native free-body journal exists/empty");out.open(filename.getValue());out<<std::setprecision(17)<<"time,dt,x,y,z,qx,qy,qz,qw,vx,vy,vz,wx,wy,wz,inferred_ix,inferred_iy,inferred_iz,inferred_tx,inferred_ty,inferred_tz,BE_position_residual,mapped_center_error,minimum_buffer_gap,body_kinetic,native_ix,native_iy,native_iz,native_tx,native_ty,native_tz,impulse_balance_residual,unmatched_rows,contact_action_reaction_residual,contact_moment_begin_residual,contact_moment_end_residual\n";
  std::ofstream file(filename.getValue()+".mass.csv");file<<std::setprecision(17);for(int i=0;i<6;++i){for(int j=0;j<6;++j){if(j)file<<',';file<<M(i,j);}file<<'\n';}
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  const auto&x=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&v=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){previousPosition=eigen(x.getCenter());previousLinear=eigen(v.getVCenter());previousOmega=eigen(v.getVOrientation());previousSurface=surface->read(sofa::core::vec_id::read_access::position)->getValue();return;}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;if(++steps>maxSteps.getValue())throw std::runtime_error("Native mixed-state observer step budget");
  double h=getContext()->getDt();Eigen::Vector3d c=eigen(x.getCenter()),linear=eigen(v.getVCenter()),omega=eigen(v.getVOrientation());Eigen::VectorXd velocity(6),delta(6);velocity<<linear,omega;delta<<linear-previousLinear,omega-previousOmega;Eigen::VectorXd impulse=M*(delta+h*damping*velocity);
  const auto&center=sphere->read(sofa::core::vec_id::read_access::position)->getValue()[0];double mapped=(eigen(center)-c).norm();double minimum=std::numeric_limits<double>::infinity();auto*topology=surface->getContext()->getMeshTopology();if(!topology)throw std::runtime_error("actual surface topology missing");const auto&p=surface->read(sofa::core::vec_id::read_access::position)->getValue();
  for(auto t:topology->getTriangles()){std::vector<regrip_film_rail::Point>triangle;for(unsigned i:t)triangle.push_back({p[i][0],p[i][1],p[i][2]});auto gap=regrip_film_sphere::ClosestPrimitive::evaluate(triangle,{c(0),c(1),c(2)},radius.getValue());minimum=std::min(minimum,gap.gap.v);}
  auto*solver=getContext()->get<sofa::core::objectmodel::BaseObject>(std::string("constraints"));auto*lambda=solver?dynamic_cast<sofa::core::objectmodel::Data<sofa::type::vector<SReal>>*>(solver->findData("constraintForces")):nullptr;
  Eigen::VectorXd native=Eigen::VectorXd::Zero(6);unsigned unmatched=0;if(!lambda)throw std::runtime_error("public Native constraintForces Data unavailable");const auto&values=lambda->getValue();const auto&J=body->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
  for(auto row=J.begin();row!=J.end();++row){if(row.index()>=values.size()){++unmatched;continue;}for(auto column=row.begin();column!=row.end();++column){if(column.index()!=0)throw std::runtime_error("unexpected Native rigid Jacobian column");for(unsigned d=0;d<3;++d){native(d)+=column.val().getVCenter()[d]*values[row.index()];native(d+3)+=column.val().getVOrientation()[d]*values[row.index()];}}}
  Eigen::Vector3d fieldImpulse=Eigen::Vector3d::Zero(),beginMoment=fieldImpulse,endMoment=fieldImpulse;const auto&Js=surface->read(sofa::core::vec_id::read_access::constraintJacobian)->getValue();
  for(auto row=Js.begin();row!=Js.end();++row){if(row.index()>=values.size()){++unmatched;continue;}for(auto column=row.begin();column!=row.end();++column){if(column.index()>=p.size()||column.index()>=previousSurface.size())throw std::runtime_error("Native surface Jacobian column mismatch");Eigen::Vector3d dp=eigen(column.val())*values[row.index()];fieldImpulse+=dp;beginMoment+=eigen(previousSurface[column.index()]).cross(dp);endMoment+=eigen(p[column.index()]).cross(dp);}}
  beginMoment+=previousPosition.cross(native.head<3>())+native.tail<3>();endMoment+=c.cross(native.head<3>())+native.tail<3>();
  out<<getContext()->getTime()<<','<<h;for(unsigned d=0;d<3;++d)out<<','<<c(d);for(unsigned d=0;d<4;++d)out<<','<<x.getOrientation()[d];for(int d=0;d<6;++d)out<<','<<velocity(d);for(int d=0;d<6;++d)out<<','<<impulse(d);out<<','<<(c-previousPosition-h*linear).norm()<<','<<mapped<<','<<minimum<<','<<.5*velocity.dot(M*velocity);
  if(unmatched)out<<",null,null,null,null,null,null,null,"<<unmatched<<",null,null,null";else{for(int d=0;d<6;++d)out<<','<<native(d);out<<','<<(native-impulse).norm()<<",0,"<<(fieldImpulse+native.head<3>()).norm()<<','<<beginMoment.norm()<<','<<endMoment.norm();}out<<'\n';out.flush();
 }
};
void registerNativeFreeBodyProbe(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Passive actual mixed Film/Rigid Native-control recorder;inferred BE impulse,NOT custom event owner or grasp certification").add<NativeFreeBodyProbe>());}
}
