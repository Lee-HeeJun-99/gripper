#pragma once
#include "../film_three_finger/SharedFilmSystem.h"
namespace regrip_three_event {
using namespace regrip_three_finger;
struct FreeState {
 Eigen::VectorXd q,v,positionFamilyRate,velocityFamilyRate;
 double momentumResidual=0;
 unsigned mechanicalEvaluations=0;
};
// Before first contact the three films and the ONE rigid body are uncoupled.
// Reuse each existing validated System::smooth(...,false) FILM block;its dummy
// rigid block is discarded,not counted three times. Integrate the actual shared
// free body ONCE with the same implicit-midpoint law. No contact projection.
inline FreeState freeMidpoint(const SharedFilmSystem&s,const Eigen::VectorXd&q0,
 const Eigen::VectorXd&v0,double start,double h,const EventControl&control,
 double damping=2,bool familyDerivative=false){
 const unsigned nf=s.shared.nf,n=s.shared.M.rows(),body=3*nf;
 if(q0.size()!=n||v0.size()!=n||!q0.allFinite()||!v0.allFinite()||!(h>0&&h<=.001)||damping<0||!std::isfinite(start+h+damping)||q0.tail<3>().norm()!=0)throw std::invalid_argument("bounded free block step;rotational chart starts at zero");
 FreeState out{q0,v0,Eigen::VectorXd::Zero(n),Eigen::VectorXd::Zero(n)};
 Eigen::MatrixXd expected=Eigen::MatrixXd::Zero(n,n);
 auto applied=control.sample(start+h/2);
 for(unsigned f=0;f<3;++f){
  const auto&base=s.shared.films[f];auto local=s.local(q0,f);auto incoming=base.film.expand(v0.segment(f*nf,nf));
  CoupledPlaneStep film(base.film.model,base.film.mass,h,damping,applied.tension,local.q,incoming,std::vector<Point>(local.q.size()),0);
  Body dummy=base.before.body;dummy.center=local.body.center;dummy.linear.setZero();dummy.angular.setZero();dummy.force.setZero();
  System single(std::move(film),base.triangles,dummy,s.layout.bufferRadius,true,true,false,1e-18,1e-10);
  expected.block(f*nf,f*nf,nf,nf)=single.M.topLeftCorner(nf,nf);
  auto result=single.smooth(start,control,false);out.mechanicalEvaluations+=result.evaluations;out.q.segment(f*nf,nf)=single.film.pack(result.state.q);out.v.segment(f*nf,nf)=single.film.pack(result.state.v);
  if(familyDerivative){
   Eigen::VectorXd before=single.pack(single.before),middle=(before+single.pack(result.state))/2;auto e=single.evaluate(middle,applied.tension);Eigen::LDLT<Eigen::MatrixXd>factor(e.tangent);
   if(factor.info()!=Eigen::Success||factor.vectorD().minCoeff()<=0)throw std::runtime_error("free block derivative tangent not SPD");
   Eigen::VectorXd unit=Eigen::VectorXd::Zero(single.n);auto qmid=single.before.q;auto vm=single.film.expand(middle.head(nf));for(unsigned i=0;i<qmid.size();++i)for(unsigned d=0;d<3;++d)qmid[i][d]+=h/2*vm[i][d];
   single.film.model.elements(qmid,1.,[&](const Element&e){if(e.kind!=2)return;for(unsigned j=0;j<3*e.ids.size();++j){unsigned a=3*e.ids[j/3]+j%3;int k=single.film.index[a];if(k>=0)unit(k)+=single.film.weight[a]*e.energy.g[j];}});
   Eigen::VectorXd Gh=(e.gradient-single.M*(middle-before))/h+(e.tangent-single.M-h/2*damping*single.M)*middle/h+h/4*applied.rate*unit,rate=factor.solve(-Gh);
   out.positionFamilyRate.segment(f*nf,nf)=middle.head(nf)+h*rate.head(nf);out.velocityFamilyRate.segment(f*nf,nf)=2*rate.head(nf);
  }
 }
 double mass=s.shared.M(body,body),inertia=s.shared.M(body+3,body+3);if(!(mass>0&&inertia>0))throw std::runtime_error("positive free rigid mass/inertia required");expected.block<3,3>(body,body).diagonal().setConstant(mass);expected.block<3,3>(body+3,body+3).diagonal().setConstant(inertia);
 if(!(expected.array()==s.shared.M.array()).all())throw std::runtime_error("free block shared/projected nodal masses do not match;no omitted coupling");
 double denominator=1+h*damping/2;
 Eigen::Vector3d acceleration=s.external/mass,middle=(v0.segment<3>(body)+h/2*acceleration)/denominator,omega=v0.tail<3>()/denominator;
 out.q.segment<3>(body)=q0.segment<3>(body)+h*middle;out.v.segment<3>(body)=2*middle-v0.segment<3>(body);out.q.tail<3>()=h*omega;out.v.tail<3>()=2*omega-v0.tail<3>();
 if(familyDerivative){Eigen::Vector3d rate=(acceleration-damping*v0.segment<3>(body))/(2*denominator*denominator),rotationRate=-damping*v0.tail<3>()/(2*denominator*denominator);out.positionFamilyRate.segment<3>(body)=middle+h*rate;out.velocityFamilyRate.segment<3>(body)=2*rate;out.positionFamilyRate.tail<3>()=omega+h*rotationRate;out.velocityFamilyRate.tail<3>()=2*rotationRate;}
 Eigen::VectorXd vm=(v0+out.v)/2,qm=q0+h/2*vm;auto force=s.force(qm,applied.tension);out.momentumResidual=(s.shared.M*(out.v-v0)-h*(force.value-damping*s.shared.M*vm)).norm();
 if((out.q-q0-h*vm).norm()>1e-12||out.momentumResidual>1e-17||!out.q.allFinite()||!out.v.allFinite())throw std::runtime_error("shared free midpoint momentum/position/finite gate failed");
 return out;
}
}
