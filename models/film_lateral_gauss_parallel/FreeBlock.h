#pragma once
#include "../film_lateral_gauss/FreeBlock.h"
#include <future>
namespace regrip_gauss_parallel {
using namespace regrip_three_event;
struct FilmResult {regrip_transmission::GaussResult step;Eigen::MatrixXd mass;std::array<Eigen::VectorXd,2>force;};
// Only the already-uncoupled,separated film blocks are scheduled concurrently.
// Workers access immutable numerical snapshots,NEVER SOFA objects/clock/journals.
inline FreeState freeGaussParallel(const SharedFilmSystem&s,const Eigen::VectorXd&q0,
 const Eigen::VectorXd&v0,double time,double h,const EventControl&control,
 unsigned threads,const GaussStageObserver&observer={}){
 const unsigned nf=s.shared.nf,n=q0.size(),body=3*nf;
 if((threads!=1&&threads!=3)||n!=s.shared.M.rows()||v0.size()!=n||q0.tail<3>().norm()!=0||v0.tail<3>().norm()!=0||s.external.norm()!=0||time<.03||!(h>0&&h<=.001)||control.sample(time).tension!=0||control.sample(time+h).tension!=0)throw std::invalid_argument("bounded separated zero-load Gauss1/3-worker fixture required");
 FreeState out{q0,v0,Eigen::VectorXd::Zero(n),Eigen::VectorXd::Zero(n)};Eigen::VectorXd impulse=Eigen::VectorXd::Zero(n);Eigen::MatrixXd off=s.shared.M;off.diagonal().setZero();if(off.cwiseAbs().maxCoeff()!=0)throw std::runtime_error("explicit diagonal projected film/body mass required");
 auto solveFilm=[&](unsigned f){FilmResult block;const auto&base=s.shared.films[f];auto local=s.local(q0,f);auto velocity=base.film.expand(v0.segment(f*nf,nf));CoupledPlaneStep map(base.film.model,base.film.mass,h,2,0,local.q,velocity,std::vector<Point>(local.q.size()),0);block.mass=regrip_transmission::filmMass(map);
  if(!(block.mass.array()==s.shared.M.block(f*nf,f*nf,nf,nf).array()).all()||map.index!=base.film.index||map.weight!=base.film.weight)throw std::runtime_error("parallel Gauss actual mass/root map differs");unsigned calls=0;std::array<Eigen::VectorXd,2>position;
  block.step=regrip_transmission::gauss(block.mass,q0.segment(f*nf,nf),v0.segment(f*nf,nf),time,h,[&](const Eigen::VectorXd&x,double t){auto value=regrip_lateral_tendon::parts(map,map.expand(x),control.sample(t).tension,6);unsigned j=calls++%2;position[j]=x;block.force[j]=value.force;return value;});
  if(calls!=block.step.evaluations||position[0]!=block.step.stageQ[0]||position[1]!=block.step.stageQ[1])throw std::runtime_error("parallel Gauss final-stage capture differs");return block;
 };
 std::array<FilmResult,3>blocks;
 if(threads==3){std::array<std::future<FilmResult>,3>jobs;for(unsigned f=0;f<3;++f)jobs[f]=std::async(std::launch::async,solveFilm,f);for(unsigned f=0;f<3;++f)blocks[f]=jobs[f].get();}
 else for(unsigned f=0;f<3;++f)blocks[f]=solveFilm(f);
 // Serial f0/f1/f2 reduction preserves physical and journal ordering exactly.
 for(unsigned f=0;f<3;++f){const auto&b=blocks[f];const auto&r=b.step;out.mechanicalEvaluations+=r.evaluations;out.q.segment(f*nf,nf)=r.q;out.v.segment(f*nf,nf)=r.v;if(observer)observer(f,r,b.force);impulse.segment(f*nf,nf)=h/2*(b.force[0]+b.force[1]-2*b.mass*(r.stageV[0]+r.stageV[1]));}
 double denominator=1+h;Eigen::Vector3d middle=v0.segment<3>(body)/denominator;out.q.segment<3>(body)=q0.segment<3>(body)+h*middle;out.v.segment<3>(body)=2*middle-v0.segment<3>(body);impulse.segment<3>(body)=-2*h*s.shared.M.block<3,3>(body,body)*middle;
 out.momentumResidual=(s.shared.M*(out.v-v0)-impulse).norm();if(out.momentumResidual>1e-17||!out.q.allFinite()||!out.v.allFinite())throw std::runtime_error("parallel Gauss momentum/finite gate failed");return out;
}
}
