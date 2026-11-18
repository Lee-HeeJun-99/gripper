#pragma once
#include "../film_three_finger_event/BlockFree.h"
#include "../film_lateral_tendon/Step.h"
#include <functional>
namespace regrip_three_event {
using GaussStageObserver=std::function<void(unsigned,const regrip_transmission::GaussResult&,const std::array<Eigen::VectorXd,2>&)>;
// Independent zero-tension,strictly separated continuation candidate. Reuses
// the existing fourth-order Gauss kernel;NO new material/contact/impact law.
inline FreeState freeGauss(const SharedFilmSystem&s,const Eigen::VectorXd&q0,
 const Eigen::VectorXd&v0,double time,double h,const EventControl&control,const GaussStageObserver&observer={}){
 const unsigned nf=s.shared.nf,n=q0.size(),body=3*nf;
 if(n!=s.shared.M.rows()||v0.size()!=n||q0.tail<3>().norm()!=0||v0.tail<3>().norm()!=0||s.external.norm()!=0||time<.03||!(h>0&&h<=.001)||control.sample(time).tension!=0||control.sample(time+h).tension!=0)throw std::invalid_argument("separated zero-load/post-unload Gauss research fixture required");
 FreeState out{q0,v0,Eigen::VectorXd::Zero(n),Eigen::VectorXd::Zero(n)};Eigen::VectorXd impulse=Eigen::VectorXd::Zero(n);
 Eigen::MatrixXd off=s.shared.M;off.diagonal().setZero();if(off.cwiseAbs().maxCoeff()!=0)throw std::runtime_error("explicit diagonal projected film/body mass required");
 for(unsigned f=0;f<3;++f){const auto&base=s.shared.films[f];auto local=s.local(q0,f);auto velocity=base.film.expand(v0.segment(f*nf,nf));CoupledPlaneStep map(base.film.model,base.film.mass,h,2,0,local.q,velocity,std::vector<Point>(local.q.size()),0);auto M=regrip_transmission::filmMass(map);
  if(!(M.array()==s.shared.M.block(f*nf,f*nf,nf,nf).array()).all()||map.index!=base.film.index||map.weight!=base.film.weight)throw std::runtime_error("Gauss actual projected mass/root map differs");
  unsigned calls=0;std::array<Eigen::VectorXd,2>force,position;
  auto result=regrip_transmission::gauss(M,q0.segment(f*nf,nf),v0.segment(f*nf,nf),time,h,[&](const Eigen::VectorXd&x,double t){auto value=regrip_lateral_tendon::parts(map,map.expand(x),control.sample(t).tension,6);unsigned j=calls++%2;position[j]=x;force[j]=value.force;return value;});
  out.mechanicalEvaluations+=result.evaluations;out.q.segment(f*nf,nf)=result.q;out.v.segment(f*nf,nf)=result.v;
  if(calls!=result.evaluations||position[0]!=result.stageQ[0]||position[1]!=result.stageQ[1])throw std::runtime_error("Gauss passive final-stage capture differs;NO stale trial force");
  if(observer)observer(f,result,force);
  impulse.segment(f*nf,nf)=h/2*(force[0]+force[1]-2*M*(result.stageV[0]+result.stageV[1]));
 }
 // Keep the existing free-body midpoint rule,not a new rigid integrator.
 double denominator=1+h;Eigen::Vector3d middle=v0.segment<3>(body)/denominator;out.q.segment<3>(body)=q0.segment<3>(body)+h*middle;out.v.segment<3>(body)=2*middle-v0.segment<3>(body);impulse.segment<3>(body)=-2*h*s.shared.M.block<3,3>(body,body)*middle;
 out.momentumResidual=(s.shared.M*(out.v-v0)-impulse).norm();if(out.momentumResidual>1e-17||!out.q.allFinite()||!out.v.allFinite())throw std::runtime_error("Gauss coupled momentum/finite gate failed");return out;
}
}
