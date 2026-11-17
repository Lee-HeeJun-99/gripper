#pragma once
#include "../film_impact/WholeSurfaceMidpoint.h"
#include <Eigen/Geometry>
#include <cstring>
#include "AccurateDual.h"
namespace regrip_coupled {
using namespace regrip_film_impact;
using namespace regrip_film_native;
using regrip_film_sphere::ClosestPrimitive;
// Independent sphere-only frictionless coupled law. A sphere's normal
// impulse is radial: its rotational Jacobian is exactly zero,not a frozen
// orientation or a missing generic-rigid contact term. Isotropic inertia.
struct Body {
 Eigen::Vector3d center=Eigen::Vector3d::Zero(),linear=Eigen::Vector3d::Zero(),angular=Eigen::Vector3d::Zero();
 Eigen::Quaterniond orientation=Eigen::Quaterniond::Identity();
 double mass=1e-4,inertia=.00256;Eigen::Vector3d force=Eigen::Vector3d::Zero();
};
inline Point point(const Eigen::Vector3d&x){return {x(0),x(1),x(2)};}
inline Eigen::Vector3d vector(Point x){return {x[0],x[1],x[2]};}
struct State {std::vector<Point>q,v;Body body;};
struct Row {unsigned triangle,feature;double gap;Eigen::VectorXd gradient;Eigen::MatrixXd hessian;Eigen::Vector3d normal,contact;};
struct Result {
 State state,eventState,preImpact,postImpact;
 std::optional<SurfaceEvent>event;std::optional<ManyRowImpact>impact;
 Eigen::MatrixXd eventJ;std::vector<Row>contactRows,projectionRows;Eigen::VectorXd constraintImpulse;
 std::vector<double>contactTimes; // Optional actual stage clocks;empty preserves legacy endpoint journal.
 Eigen::RowVectorXd eventIncomingSensitivity;std::optional<double>absoluteEventStartSensitivity;
 std::optional<ManyRowImpact>projection;
 double minimumGap=0,residual=0,projectionLoss=0,projectionDefect=0;
 double forceTime=0,tension=0,rotationAngle=0;
 bool sustained=false;unsigned closureSweeps=0;
 unsigned evaluations=0,acceptedReuses=0;
};
struct System {
 CoupledPlaneStep film;std::vector<std::array<unsigned,3>>triangles;State before;double radius;
 unsigned nf,n;Eigen::MatrixXd M;bool strictNewton,reuseAccepted,midpointContact;double absoluteNewtonResidual,contactSolveGap;
 System(CoupledPlaneStep m,std::vector<std::array<unsigned,3>>t,Body b,double r,bool strict=false,bool reuse=true,bool midpoint=false,double forceResidual=0,double gapSolve=1e-10):film(std::move(m)),triangles(std::move(t)),before{film.previous,film.previousVelocity,b},radius(r),nf(film.freeSize),n(nf+6),strictNewton(strict),reuseAccepted(reuse),midpointContact(midpoint),absoluteNewtonResidual(forceResidual),contactSolveGap(gapSolve){
  if(!std::isfinite(forceResidual)||forceResidual<0||forceResidual>1e-15)throw std::invalid_argument("optional Newton force residual can only tighten original1e-15 default");
  if(!(gapSolve>0&&gapSolve<=1e-10)||!std::isfinite(gapSolve))throw std::invalid_argument("optional contact solve gap can only tighten original1e-10");
  if(!(b.mass>0&&b.inertia>0&&r>0)||!std::isfinite(b.mass+b.inertia+r)||!b.center.allFinite()||!b.linear.allFinite()||!b.angular.allFinite()||!b.force.allFinite()||!b.orientation.coeffs().allFinite()||std::abs(b.orientation.squaredNorm()-1)>1e-12||triangles.empty())throw std::invalid_argument("coupled sphere inputs");
  M=Eigen::MatrixXd::Zero(n,n);M.topLeftCorner(nf,nf)=filmMass(film);M.block<3,3>(nf,nf).diagonal().setConstant(b.mass);M.block<3,3>(nf+3,nf+3).diagonal().setConstant(b.inertia);
 }
 double residualThreshold(double initial)const{return std::max(absoluteNewtonResidual>0?absoluteNewtonResidual:strictNewton?1e-18:1e-15,initial*(strictNewton?1e-10:1e-7));}
 Eigen::VectorXd pack(const State&s)const{Eigen::VectorXd y(n);y.head(nf)=film.pack(s.v);y.segment<3>(nf)=s.body.linear;y.tail<3>()=s.body.angular;return y;}
 void velocity(State&s,const Eigen::VectorXd&y)const{s.v=film.expand(y.head(nf));s.body.linear=y.segment<3>(nf);s.body.angular=y.tail<3>();}
 State endpoint(const Eigen::VectorXd&middle)const{
  State s=before;auto v=film.expand(middle.head(nf));for(unsigned i=0;i<s.q.size();++i)for(unsigned d=0;d<3;++d)s.q[i][d]+=film.h*v[i][d];
  s.body.center+=film.h*middle.segment<3>(nf);velocity(s,2*middle-pack(before));
  Eigen::Vector3d a=film.h*middle.tail<3>();double angle=a.norm();if(angle>0)s.body.orientation=Eigen::Quaterniond(Eigen::AngleAxisd(angle,a/angle))*before.body.orientation;
  return s;
 }
 ClosestPrimitive::Evaluation primitive(const State&s,unsigned id)const{
  const auto&t=triangles.at(id);auto rest=film.model.rest();std::vector<Point>relative;for(unsigned i:t)relative.push_back(sub(add(rest.at(i),s.q.at(i)),point(s.body.center)));
  return ClosestPrimitive::evaluate(relative,{0,0,0},radius);
 }
 Row geometry(const State&s,unsigned id)const{
  const auto&t=triangles.at(id);auto e=primitive(s,id);Eigen::MatrixXd D=Eigen::MatrixXd::Zero(9,n);
  for(unsigned a=0;a<9;++a){unsigned ga=3*t[a/3]+a%3;if(film.index[ga]>=0)D(a,film.index[ga])=film.weight[ga];D(a,nf+a%3)=-1;}
  Eigen::VectorXd g(9);Eigen::MatrixXd H(9,9);for(unsigned a=0;a<9;++a){g(a)=e.gap.g[a];for(unsigned b=0;b<9;++b)H(a,b)=e.gap.h[regrip_film::N*a+b];}
  Eigen::Vector3d delta(e.point[0].v,e.point[1].v,e.point[2].v);if(!(delta.norm()>0))throw std::domain_error("coupled sphere normal undefined");
  return {id,e.feature,e.gap.v,D.transpose()*g,D.transpose()*H*D,delta/delta.norm(),s.body.center+delta};
 }
 double clearance(const State&s)const{double g=std::numeric_limits<double>::infinity();for(unsigned i=0;i<triangles.size();++i)g=std::min(g,primitive(s,i).gap.v);return g;}
 State forceGeometry(const State&end)const{
  if(!midpointContact)return end;
  State middle=end;for(unsigned i=0;i<end.q.size();++i)for(unsigned d=0;d<3;++d)middle.q[i][d]=.5*(before.q[i][d]+end.q[i][d]);
  middle.body.center=.5*(before.body.center+end.body.center);return middle;
 }
 CoupledPlaneStep::Evaluation evaluate(const Eigen::VectorXd&y,double tension)const{
  CoupledPlaneStep stage(film.model,film.mass,film.h/2,film.damping,tension,before.q,before.v,std::vector<Point>(before.q.size()),0);
  auto f=stage.evaluate(y.head(nf));CoupledPlaneStep::Evaluation out;out.phi=f.phi;out.gradient=Eigen::VectorXd::Zero(n);out.tangent=Eigen::MatrixXd::Zero(n,n);out.gradient.head(nf)=f.gradient;out.tangent.topLeftCorner(nf,nf)=f.tangent;
  Eigen::VectorXd v0=pack(before);for(unsigned i=nf;i<n;++i){double force=i<nf+3?before.body.force(i-nf):0,dm=M(i,i),delta=y(i)-v0(i),h=film.h/2;out.gradient(i)=dm*(delta+h*film.damping*y(i))-h*force;out.tangent(i,i)=dm*(1+h*film.damping);out.phi+=.5*dm*(delta*delta+h*film.damping*y(i)*y(i))-h*force*y(i);}
  return out;
 }
 Result smooth(double time,const EventControl&control,bool constrained)const{
  Result out;out.forceTime=time+film.h/2;out.tension=control.sample(out.forceTime).tension;Eigen::VectorXd y=pack(before),lambda(0);std::vector<unsigned>owned;double initial=-1;std::optional<CoupledPlaneStep::Evaluation>cached;Eigen::VectorXd cachedY;
  struct Geometry{Eigen::VectorXd gap;Eigen::MatrixXd C,endC,H;};
  auto geo=[&](const Eigen::VectorXd&trial,const Eigen::VectorXd&l){auto state=endpoint(trial),forceState=forceGeometry(state);Geometry g;g.gap.resize(owned.size());g.C=Eigen::MatrixXd::Zero(n,owned.size());g.endC=Eigen::MatrixXd::Zero(n,owned.size());g.H=Eigen::MatrixXd::Zero(n,n);for(unsigned k=0;k<owned.size();++k){auto endRow=geometry(state,owned[k]);auto row=midpointContact?geometry(forceState,owned[k]):endRow;g.gap(k)=endRow.gap;g.C.col(k)=row.gradient;g.endC.col(k)=endRow.gradient;g.H+=film.h*(midpointContact?.5:1.)*l(k)*row.hessian;}return g;};
  for(unsigned sweep=0;sweep<8;++sweep){bool converged=false;
   for(unsigned iteration=0;iteration<30;++iteration){CoupledPlaneStep::Evaluation e;if(reuseAccepted&&cached&&cachedY.size()==y.size()&&std::memcmp(cachedY.data(),y.data(),sizeof(double)*y.size())==0){e=std::move(*cached);cached.reset();++out.acceptedReuses;}else{e=evaluate(y,out.tension);++out.evaluations;}auto g=geo(y,lambda);double r=(e.gradient-g.C*lambda).norm();if(initial<0)initial=r;
    auto final=[&](double residual,const Geometry&gg,const Eigen::VectorXd&l){return residual<=residualThreshold(initial)&&CoupledContactStep::gapError(gg.gap,l)<=contactSolveGap;};
    if(final(r,g,lambda)){converged=true;out.residual=2*r;break;}
    Eigen::LDLT<Eigen::MatrixXd>factor(e.tangent-g.H);if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("coupled sphere TRUE tangent not SPD;no regularization");
    Eigen::VectorXd inverseG=factor.solve(e.gradient);Eigen::MatrixXd inverseC=factor.solve(g.C),W=film.h*g.endC.transpose()*inverseC;Eigen::VectorXd d=g.gap-film.h*g.endC.transpose()*inverseG,next=contactSolveGap==1e-10?CoupledContactStep::dual(W,d,lambda):accurateDual(W,d,lambda,contactSolveGap),dy=-inverseG+inverseC*next;
    auto merit=[&](const auto&gradient,const Geometry&gg,const Eigen::VectorXd&l){double square=(gradient-gg.C*l).squaredNorm();for(int i=0;i<l.size();++i){if(!(W(i,i)>0))throw std::runtime_error("coupled sphere zero compliance");double c=std::min(l(i),gg.gap(i)/W(i,i));square+=c*c;}return std::sqrt(square);};
    double old=merit(e.gradient,g,lambda),alpha=1;bool accepted=false;for(unsigned back=0;back<16;++back){Eigen::VectorXd trial=y+alpha*dy,l=lambda+alpha*(next-lambda);auto value=evaluate(trial,out.tension);++out.evaluations;auto gg=geo(trial,l);if(final((value.gradient-gg.C*l).norm(),gg,l)||merit(value.gradient,gg,l)<=(1-1e-4*alpha)*old){y=trial;lambda=l;if(reuseAccepted){cachedY=y;cached=std::move(value);}accepted=true;break;}alpha*=.5;}
    if(!accepted){std::ostringstream message;message<<std::setprecision(17)<<"coupled sphere contact line search rejected time="<<time<<" h="<<film.h<<" iteration="<<iteration<<" residual="<<r<<" threshold="<<residualThreshold(initial)<<" merit="<<old<<" gap_error="<<CoupledContactStep::gapError(g.gap,lambda)<<" owned="<<owned.size()<<" minimum_mass_diagonal="<<M.diagonal().minCoeff();throw std::runtime_error(message.str());}
   }
   if(!converged)throw std::runtime_error("coupled sphere Newton budget30");out.state=endpoint(y);out.minimumGap=clearance(out.state);out.closureSweeps=sweep+1;
   unsigned added=0;if(constrained)for(unsigned id=0;id<triangles.size();++id)if(primitive(out.state,id).gap.v< -contactSolveGap){if(std::find(owned.begin(),owned.end(),id)!=owned.end())throw std::runtime_error("owned coupled row violates solve gap");if(owned.size()>=256)throw std::runtime_error("coupled row budget256");owned.push_back(id);++added;}
   if(!added){for(unsigned id:owned)out.contactRows.push_back(geometry(forceGeometry(out.state),id));out.constraintImpulse=2*lambda;out.sustained=!owned.empty();return out;}
   unsigned old=lambda.size();lambda.conservativeResize(owned.size());lambda.tail(owned.size()-old).setZero();
  }throw std::runtime_error("coupled candidate closure budget8");
 }
 QuadraticSurfacePath relativePath(const State&end)const{
  auto rest=film.model.rest();QuadraticSurfacePath path{rest,std::vector<Point>(rest.size()),std::vector<Point>(rest.size())};auto v0=pack(before),v1=pack(end);Eigen::VectorXd middle=(v0+v1)/2;auto vm=film.expand(middle.head(nf));
  for(unsigned i=0;i<rest.size();++i)for(unsigned d=0;d<3;++d){path.a0[i][d]+=before.q[i][d]-before.body.center(d);path.a1[i][d]=film.h*(before.v[i][d]-before.body.linear(d));path.a2[i][d]=film.h*(vm[i][d]-before.v[i][d]-middle(nf+d)+before.body.linear(d));}return path;
 }
 Result advance(double time,const EventControl&control)const{
  double gap=clearance(before);if(gap< -1e-10)throw std::domain_error("initial coupled sphere penetration");
  auto project=[&](Result&out){std::vector<Row>rows;for(unsigned id=0;id<triangles.size();++id)if(primitive(out.state,id).gap.v<=1e-10)rows.push_back(geometry(out.state,id));if(!rows.empty()){Eigen::MatrixXd J(rows.size(),n);for(unsigned k=0;k<rows.size();++k)J.row(k)=rows[k].gradient;auto projected=manyRowImpact(M,J,pack(out.state),1e-10);velocity(out.state,projected.state.velocity);out.projectionLoss=projected.state.energyLoss;out.projectionDefect=projected.momentumEnergyDefect;out.projection=projected;out.projectionRows=std::move(rows);}};
  if(gap<=1e-10){for(unsigned id=0;id<triangles.size();++id)if(primitive(before,id).gap.v<=1e-10){auto row=geometry(before,id);if(row.gradient.dot(pack(before))< -1e-10)throw std::domain_error("initial inward coupled contact needs zero-time impact");}auto out=smooth(time,control,true);project(out);return out;}
  auto out=smooth(time,control,false);auto path=relativePath(out.state);out.event=earliestSurfaceEvent(path,triangles,{0,0,0},radius);if(!out.event){if(out.minimumGap< -1e-10)throw std::runtime_error("coupled path missed endpoint contact");return out;}
  double a=out.event->fraction;out.eventState=before;Eigen::VectorXd v0=pack(before),vm=(v0+pack(out.state))/2;auto middle=film.expand(vm.head(nf));
  for(unsigned i=0;i<before.q.size();++i)for(unsigned d=0;d<3;++d)out.eventState.q[i][d]+=film.h*(a*before.v[i][d]+a*a*(middle[i][d]-before.v[i][d]));
  out.eventState.body.center+=film.h*(a*before.body.linear+a*a*(vm.segment<3>(nf)-before.body.linear));Eigen::Vector3d rotation=film.h*(a*before.body.angular+a*a*(vm.tail<3>()-before.body.angular));double angle=rotation.norm();if(angle>0)out.eventState.body.orientation=Eigen::Quaterniond(Eigen::AngleAxisd(angle,rotation/angle))*before.body.orientation;
  velocity(out.eventState,v0+2*a*(vm-v0));out.preImpact=out.eventState;out.eventJ.resize(out.event->rows.size(),n);for(unsigned k=0;k<out.event->rows.size();++k)out.eventJ.row(k)=geometry(out.eventState,out.event->rows[k].triangle).gradient;
  bool unique=true;for(int k=1;k<out.eventJ.rows();++k)if((out.eventJ.row(k).array()!=out.eventJ.row(0).array()).any())unique=false;
  if(unique){auto e=evaluate(vm,control.sample(time+film.h/2).tension);Eigen::LDLT<Eigen::MatrixXd>factor(e.tangent);if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("coupled event sensitivity tangent not SPD");Eigen::MatrixXd V=factor.solve(M),Q=film.h*((a-a*a)*Eigen::MatrixXd::Identity(n,n)+a*a*V);double denominator=film.h*out.eventJ.row(0).dot(pack(out.preImpact));if(!(denominator<0))throw std::domain_error("coupled nontransversal event sensitivity");out.eventIncomingSensitivity=-(out.eventJ.row(0)*Q)/denominator;
   Eigen::VectorXd forceT=Eigen::VectorXd::Zero(n);auto qmid=before.q;auto midpointVelocity=film.expand(vm.head(nf));for(unsigned i=0;i<qmid.size();++i)for(unsigned d=0;d<3;++d)qmid[i][d]+=film.h/2*midpointVelocity[i][d];film.model.elements(qmid,1,[&](const Element&el){if(el.kind!=2)return;for(unsigned j=0;j<3*el.ids.size();++j){unsigned ga=3*el.ids[j/3]+j%3;int i=film.index[ga];if(i>=0)forceT(i)+=film.weight[ga]*el.energy.g[j];}});Eigen::VectorXd timeRate=factor.solve(-film.h/2*control.sample(time+film.h/2).rate*forceT);out.absoluteEventStartSensitivity=1-film.h*out.eventJ.row(0).dot(film.h*a*a*timeRate)/denominator;
  }
  out.impact=manyRowImpact(M,out.eventJ,pack(out.preImpact),1e-10);out.postImpact=out.preImpact;velocity(out.postImpact,out.impact->state.velocity);
  double remaining=film.h*(1-a);out.state=out.postImpact;
  if(remaining>0){CoupledPlaneStep next(film.model,film.mass,remaining,film.damping,control.sample(time+a*film.h).tension,out.postImpact.q,out.postImpact.v,std::vector<Point>(before.q.size()),0);System remainder(next,triangles,out.postImpact.body,radius,strictNewton,reuseAccepted,midpointContact,absoluteNewtonResidual,contactSolveGap);auto contact=remainder.smooth(time+a*film.h,control,true);out.state=contact.state;out.contactRows=contact.contactRows;out.constraintImpulse=contact.constraintImpulse;out.residual=contact.residual;out.sustained=contact.sustained;out.forceTime=contact.forceTime;out.tension=contact.tension;out.evaluations+=contact.evaluations;out.acceptedReuses+=contact.acceptedReuses;project(out);}
  out.minimumGap=clearance(out.state);if(out.minimumGap< -1e-10)throw std::runtime_error("coupled accepted whole-surface gap gate");return out;
 }
};
}
