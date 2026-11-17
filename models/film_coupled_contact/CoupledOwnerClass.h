#pragma once
#include "CoupledSphere.h"
#include <sofa/core/behavior/OdeSolver.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseForceField.h>
#include <sofa/core/behavior/BaseProjectiveConstraintSet.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/topology/BaseMeshTopology.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/simulation/MechanicalOperations.h>
#include <fstream>
#include <iomanip>
namespace regrip_coupled {
class CoupledSphereODE:public sofa::core::behavior::OdeSolver {
public:
 SOFA_CLASS(CoupledSphereODE,sofa::core::behavior::OdeSolver);
 using Film=sofa::core::behavior::MechanicalState<sofa::defaulttype::Vec3Types>;
 using Rigid=sofa::core::behavior::MechanicalState<sofa::defaulttype::Rigid3Types>;using Link=sofa::core::objectmodel::BaseLink;
 sofa::core::objectmodel::SingleLink<CoupledSphereODE,Film,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>root;
 sofa::core::objectmodel::SingleLink<CoupledSphereODE,Rigid,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>body;
 sofa::core::objectmodel::SingleLink<CoupledSphereODE,sofa::core::objectmodel::BaseObject,Link::FLAG_STOREPATH|Link::FLAG_STRONGLINK>field;
 sofa::core::objectmodel::Data<double>radius,rayleighMass;
 sofa::core::objectmodel::Data<unsigned>maxSteps;
 sofa::core::objectmodel::Data<sofa::type::Vec3>externalForce;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<bool>strictNewton{initData(&strictNewton,false,"strictNewton","Independent tighter residual contrast;old1e-15/1e-7 preserved by default")};
 sofa::core::objectmodel::Data<bool>reuseAcceptedEvaluation{initData(&reuseAcceptedEvaluation,true,"reuseAcceptedEvaluation","Exact-bit accepted trial cache;false is same-binary control")};
 sofa::core::objectmodel::Data<bool>midpointContact{initData(&midpointContact,false,"midpointContact","EXPERIMENTAL midpoint force Jacobian with endpoint gap;not an energy certificate")};
 std::ofstream states,events,rows,eventStates,cost,work;unsigned count=0;double last=-1;
 bool workReady=false;double previousLength=0,previousTension=0,cumulativeWork=0;
 CoupledSphereODE():root(initLink("root","Actual independent displacement state")),body(initLink("body","Actual FREE sphere Rigid3")),field(initLink("field","Actual FilmRailTendon")),radius(initData(&radius,8.01,"radius","Spherical midsurface buffer radius")),rayleighMass(initData(&rayleighMass,2.,"rayleighMass","Common actual mass damping")),maxSteps(initData(&maxSteps,64u,"maxSteps","Profile-bounded experiment steps <=1600")),externalForce(initData(&externalForce,sofa::type::Vec3(0,0,0),"externalForce","Constant world force on sphere;research condition")),filename(initData(&filename,std::string(),"filename","Exclusive accepted coupled journals")){}
 template<class T>T parameter(const char*name)const{auto*d=dynamic_cast<sofa::core::objectmodel::Data<T>*>(field->findData(name));if(!d)throw std::runtime_error("actual coupled parameter missing");return d->getValue();}
 void init()override{
  OdeSolver::init();if(!root||!body||!field||field->getClassName()!="FilmRailTendon"||body->getSize()!=1||getContext()->getGravity().norm()!=0||!(radius.getValue()>0)||rayleighMass.getValue()<0||maxSteps.getValue()==0||maxSteps.getValue()>1600)throw std::runtime_error("explicit coupled sphere links/zero gravity/step budget required");
  if(!body->getContext()->getObjects<sofa::core::behavior::BaseProjectiveConstraintSet>(sofa::core::objectmodel::BaseContext::Local).empty())throw std::runtime_error("coupled body must be free");
  auto masses=getContext()->getObjects<sofa::core::behavior::BaseMass>(sofa::core::objectmodel::BaseContext::SearchDown);if(masses.size()!=2)throw std::runtime_error("coupled owner requires exactly actual film and body masses");
  for(auto*f:getContext()->getObjects<sofa::core::behavior::BaseForceField>(sofa::core::objectmodel::BaseContext::SearchDown))if(f!=field.get()&&!dynamic_cast<sofa::core::behavior::BaseMass*>(f))throw std::runtime_error("unsupported additional force field;not silently omitted");
  if(getContext()->getObjects<sofa::core::behavior::OdeSolver>(sofa::core::objectmodel::BaseContext::SearchDown).size()!=1)throw std::runtime_error("coupled owner must be sole ODE");
  for(const auto*suffix:{".states.csv",".events.csv",".rows.csv",".event_states.csv",".cost.csv",".work.csv"})if(filename.getValue().empty()||std::ifstream(filename.getValue()+suffix))throw std::runtime_error("coupled journal exists/empty");
  states.open(filename.getValue()+".states.csv");events.open(filename.getValue()+".events.csv");rows.open(filename.getValue()+".rows.csv");eventStates.open(filename.getValue()+".event_states.csv");for(auto*f:{&states,&events,&rows,&eventStates})*f<<std::setprecision(17);
  eventStates<<"time,stage,body_center,body_quaternion,body_velocity,body_omega,local_displacement,local_velocity,event_fraction_incoming_sensitivity,absolute_start_time_sensitivity\n";
  cost.open(filename.getValue()+".cost.csv");cost<<std::setprecision(17)<<"time,mechanical_evaluations,accepted_reuses\n";
  work.open(filename.getValue()+".work.csv");work<<std::setprecision(17)<<"time,tension,cable_length,step_tendon_work,cumulative_tendon_work\n";
  states<<"time,minimum_gap,position_residual,event,sustained,tension,force_time,end_tension,U_shell,U_attachment,K_film,K_linear,K_rotation,projection_loss,projection_momentum_defect,body_center,body_quaternion,body_velocity,body_omega,local_displacement,local_velocity\n";
  events<<"time,row,triangle,feature,gap,normal_before,normal_after,impulse,momentum_residual,impact_loss,momentum_energy_defect,subtraction_residual,linear_balance,angular_balance,root_impulse,root_moment,body_pre_velocity,body_post_velocity\n";
  rows<<"time,step,stage,row,triangle,feature,gap,impulse,nx,ny,nz,px,py,pz,jacobian\n";
 }
 template<class T>static void quote(std::ostream&out,const T&values){out<<",\"";for(auto value:values)out<<value<<' ';out<<'"';}
 void solve(const sofa::core::ExecParams*,SReal dt,sofa::core::MultiVecCoordId,sofa::core::MultiVecDerivId)override{
  if(++count>maxSteps.getValue()||dt!=getContext()->getDt()||getContext()->getTime()<=last)throw std::runtime_error("coupled once-per-step/explicit budget guard");last=getContext()->getTime();
  sofa::simulation::common::MechanicalOperations mop(sofa::core::ExecParams::defaultInstance(),getContext());mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  auto*local=dynamic_cast<Film*>(field->getContext()->getMechanicalState());auto*world=field->getContext()->get<Film>(std::string("actual/world"));auto*topology=world?world->getContext()->getMeshTopology():nullptr;auto*fm=field->getContext()->getMass();auto*bm=body->getContext()->getMass();if(!local||!topology||!fm||!bm)throw std::runtime_error("actual coupled states/masses/topology unavailable");
  Assembly model(parameter<unsigned>("nx"));model.guideIntervals=parameter<unsigned>("guideIntervals");model.guideOffset=parameter<double>("guideOffset");model.bondK=parameter<double>("bondStiffness");model.rootGuideSecondOrder=parameter<bool>("rootGuideSecondOrder");
  const auto&q=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&v=local->read(sofa::core::vec_id::read_access::velocity)->getValue();if(q.size()!=model.size())throw std::runtime_error("actual coupled model mismatch");
  std::vector<Point>q0(q.size()),v0(v.size()),zero(q.size());std::vector<double>mass(q.size());for(unsigned i=0;i<q.size();++i){mass[i]=fm->getElementMass(i);for(unsigned d=0;d<3;++d){q0[i][d]=q[i][d];v0[i][d]=v[i][d];}}
  auto bx=body->read(sofa::core::vec_id::read_access::position)->getValue();auto bv=body->read(sofa::core::vec_id::read_access::velocity)->getValue();Body b;for(unsigned d=0;d<3;++d){b.center(d)=bx[0].getCenter()[d];b.linear(d)=bv[0].getVCenter()[d];b.angular(d)=bv[0].getVOrientation()[d];b.force(d)=externalForce.getValue()[d];}b.orientation=Eigen::Quaterniond(bx[0].getOrientation()[3],bx[0].getOrientation()[0],bx[0].getOrientation()[1],bx[0].getOrientation()[2]);
  sofa::linearalgebra::FullMatrix<double>Mb(6,6);Mb.clear();bm->getElementMass(0,&Mb);b.mass=Mb.element(0,0);b.inertia=Mb.element(3,3);for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)if(Mb.element(i,j)!=(i==j?(i<3?b.mass:b.inertia):0))throw std::runtime_error("coupled sphere requires isotropic actual inertia;not general rigid support");
  std::vector<std::array<unsigned,3>>triangles;for(auto t:topology->getTriangles())triangles.push_back({t[0],t[1],t[2]});EventControl control{parameter<double>("maximumTension"),parameter<double>("rampTime"),parameter<double>("releaseBegin"),parameter<double>("releaseEnd"),parameter<bool>("c2Control")};
  if(!workReady){previousLength=model.cableLength(q0);previousTension=control.sample(last).tension;workReady=true;}
  CoupledPlaneStep mechanics(model,mass,dt,rayleighMass.getValue(),control.sample(last).tension,q0,v0,zero,0);System system(mechanics,triangles,b,radius.getValue(),strictNewton.getValue(),reuseAcceptedEvaluation.getValue(),midpointContact.getValue());auto result=system.advance(last,control);cost<<last+dt<<','<<result.evaluations<<','<<result.acceptedReuses<<'\n';cost.flush();
  if(!system.pack(result.state).allFinite()||!result.state.body.center.allFinite()||!result.state.body.orientation.coeffs().allFinite()||!std::isfinite(result.minimumGap)||result.minimumGap< -1e-10)throw std::runtime_error("invalid coupled accepted state BEFORE commit");
  auto recordRow=[&](const Row&r,double p,unsigned stage,unsigned id,double time){rows<<time<<','<<count<<','<<stage<<','<<id<<','<<r.triangle<<','<<r.feature<<','<<r.gap<<','<<p;for(double value:r.normal)rows<<','<<value;for(double value:r.contact)rows<<','<<value;quote(rows,r.gradient);rows<<'\n';};
  if(result.event){Eigen::Vector3d rootImpulse=Eigen::Vector3d::Zero(),rootMoment=rootImpulse,total=rootImpulse,angular=rootImpulse;auto rest=model.rest();std::vector<Eigen::Vector3d>nodal(q.size(),Eigen::Vector3d::Zero());
   for(const auto&pair:{std::make_pair("pre",&result.preImpact),std::make_pair("post",&result.postImpact)}){eventStates<<last+dt*result.event->fraction<<','<<pair.first;quote(eventStates,pair.second->body.center);quote(eventStates,pair.second->body.orientation.coeffs());quote(eventStates,pair.second->body.linear);quote(eventStates,pair.second->body.angular);eventStates<<",\"";for(auto p:pair.second->q)for(double value:p)eventStates<<value<<' ';eventStates<<"\",\"";for(auto p:pair.second->v)for(double value:p)eventStates<<value<<' ';eventStates<<'"';quote(eventStates,result.eventIncomingSensitivity);eventStates<<',';if(result.absoluteEventStartSensitivity)eventStates<<*result.absoluteEventStartSensitivity;else eventStates<<"null";eventStates<<'\n';}
   for(unsigned k=0;k<result.event->rows.size();++k){auto row=system.geometry(result.eventState,result.event->rows[k].triangle);double p=result.impact->state.impulse(k);auto support=triangles[row.triangle];std::vector<Point>relative;for(unsigned i:support)relative.push_back(sub(add(rest[i],result.eventState.q[i]),point(result.eventState.body.center)));auto e=ClosestPrimitive::evaluate(relative,{0,0,0},radius.getValue());for(unsigned a=0;a<9;++a)nodal[support[a/3]](a%3)+=p*e.gap.g[a];recordRow(row,p,0,k,last+dt*result.event->fraction);}
   for(unsigned i=0;i<q.size();++i){Eigen::Vector3d delta=mass[i]*(vector(result.postImpact.v[i])-vector(result.preImpact.v[i])),reaction=delta-nodal[i],x=vector(add(rest[i],result.eventState.q[i]));rootImpulse+=reaction;rootMoment+=x.cross(reaction);total+=delta;angular+=x.cross(delta);}
   Eigen::Vector3d dp=b.mass*(result.postImpact.body.linear-result.preImpact.body.linear);total+=dp;angular+=result.eventState.body.center.cross(dp)+b.inertia*(result.postImpact.body.angular-result.preImpact.body.angular);double linear=(total-rootImpulse).norm(),moment=(angular-rootMoment).norm();if(linear>1e-12||moment>1e-12||result.impact->state.momentumResidual>1e-12)throw std::runtime_error("coupled impact global momentum gate BEFORE commit");
   for(unsigned k=0;k<result.event->rows.size();++k){auto row=system.geometry(result.eventState,result.event->rows[k].triangle);events<<last+dt*result.event->fraction<<','<<k<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<result.eventJ.row(k).dot(system.pack(result.preImpact))<<','<<result.impact->state.normalVelocity(k)<<','<<result.impact->state.impulse(k)<<','<<result.impact->state.momentumResidual<<','<<result.impact->state.energyLoss<<','<<result.impact->momentumEnergyDefect<<','<<result.impact->subtractionResidual<<','<<linear<<','<<moment<<','<<rootImpulse.norm()<<','<<rootMoment.norm();quote(events,result.preImpact.body.linear);quote(events,result.postImpact.body.linear);events<<'\n';}
  }
  for(unsigned k=0;k<result.contactRows.size();++k)recordRow(result.contactRows[k],result.constraintImpulse(k),1,k,last+dt);
  if(result.projection)for(unsigned k=0;k<result.projectionRows.size();++k)recordRow(result.projectionRows[k],result.projection->state.impulse(k),2,k,last+dt);
  // One commit only,after shared mass/whole-surface/finite/momentum gates.
  auto x=root->read(sofa::core::vec_id::read_access::position)->getValue();auto rv=root->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned a=0;a<mechanics.index.size();++a)if(mechanics.index[a]>=0&&mechanics.weight[a]==1){x[a/3][a%3]=result.state.q[a/3][a%3];rv[a/3][a%3]=result.state.v[a/3][a%3];}root->write(sofa::core::vec_id::write_access::position)->setValue(x);root->write(sofa::core::vec_id::write_access::velocity)->setValue(rv);
  const auto&accepted=result.state.body;for(unsigned d=0;d<3;++d){bx[0].getCenter()[d]=accepted.center(d);bv[0].getVCenter()[d]=accepted.linear(d);bv[0].getVOrientation()[d]=accepted.angular(d);}for(unsigned d=0;d<4;++d)bx[0].getOrientation()[d]=accepted.orientation.coeffs()(d);body->write(sofa::core::vec_id::write_access::position)->setValue(bx);body->write(sofa::core::vec_id::write_access::velocity)->setValue(bv);mop.propagateXAndV(sofa::core::vec_id::write_access::position,sofa::core::vec_id::write_access::velocity);
  const auto&actual=local->read(sofa::core::vec_id::read_access::position)->getValue();const auto&av=local->read(sofa::core::vec_id::read_access::velocity)->getValue();for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)if(actual[i][d]!=result.state.q[i][d]||av[i][d]!=result.state.v[i][d])throw std::runtime_error("actual accepted film mapping differs from coupled kernel");
  const auto&actualBody=body->read(sofa::core::vec_id::read_access::position)->getValue()[0];const auto&actualVelocity=body->read(sofa::core::vec_id::read_access::velocity)->getValue()[0];for(unsigned d=0;d<3;++d)if(actualBody.getCenter()[d]!=accepted.center(d)||actualVelocity.getVCenter()[d]!=accepted.linear(d)||actualVelocity.getVOrientation()[d]!=accepted.angular(d))throw std::runtime_error("actual committed body state differs from coupled kernel");for(unsigned d=0;d<4;++d)if(actualBody.getOrientation()[d]!=accepted.orientation.coeffs()(d))throw std::runtime_error("actual body orientation differs from coupled kernel");
  double length=model.cableLength(result.state.q),endTension=control.sample(last+dt).tension,stepWork=-.5*(previousTension+endTension)*(length-previousLength);cumulativeWork+=stepWork;previousLength=length;previousTension=endTension;work<<last+dt<<','<<endTension<<','<<length<<','<<stepWork<<','<<cumulativeWork<<'\n';work.flush();
  double shell=0,attachment=0,K=0;model.elements(result.state.q,0,[&](const Element&e){if(e.kind==0)shell+=e.energy.v;if(e.kind==1)attachment+=e.energy.v;});for(unsigned i=0;i<mass.size();++i)K+=.5*mass[i]*dot(result.state.v[i],result.state.v[i]);states<<last+dt<<','<<result.minimumGap<<','<<result.residual<<','<<bool(result.event)<<','<<result.sustained<<','<<result.tension<<','<<result.forceTime<<','<<control.sample(last+dt).tension<<','<<shell<<','<<attachment<<','<<K<<','<<.5*b.mass*accepted.linear.squaredNorm()<<','<<.5*b.inertia*accepted.angular.squaredNorm()<<','<<result.projectionLoss<<','<<result.projectionDefect;quote(states,accepted.center);quote(states,accepted.orientation.coeffs());quote(states,accepted.linear);quote(states,accepted.angular);states<<",\"";for(auto p:result.state.q)for(double value:p)states<<value<<' ';states<<"\",\"";for(auto p:result.state.v)for(double value:p)states<<value<<' ';states<<"\"\n";for(auto*f:{&states,&events,&rows,&eventStates})f->flush();
 }
};
}
