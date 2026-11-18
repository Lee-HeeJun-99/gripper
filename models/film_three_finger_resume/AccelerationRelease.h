#pragma once
#include "FaceEdgeTransfer.h"
namespace regrip_three_resume {
struct AccelerationReaction {Eigen::VectorXd force,normal;unsigned mask=0;double residual=0;};
// BOUNDED three-row acceleration complementarity reference,not an impact law.
// No component clipping,compliance or tensile reaction. Dependent W is rejected.
inline AccelerationReaction accelerationReaction(const Eigen::MatrixXd&W,const Eigen::VectorXd&free){
 if(W.rows()!=3||W.cols()!=3||free.size()!=3||!W.allFinite()||!free.allFinite())throw std::invalid_argument("three acceleration rows required");
 if((W-W.transpose()).norm()>64*std::numeric_limits<double>::epsilon()*W.norm())throw std::domain_error("acceleration compliance not symmetric within operation roundoff");
 Eigen::LDLT<Eigen::MatrixXd>check(W);if(check.info()!=Eigen::Success||check.vectorD().minCoeff()<=0)throw std::domain_error("acceleration compliance not SPD");
 for(unsigned mask=0;mask<8;++mask){std::vector<unsigned>active;for(unsigned i=0;i<3;++i)if(mask&(1u<<i))active.push_back(i);Eigen::VectorXd lambda=Eigen::VectorXd::Zero(3);
  if(!active.empty()){Eigen::MatrixXd block(active.size(),active.size());Eigen::VectorXd b(active.size());for(unsigned i=0;i<active.size();++i){b(i)=-free(active[i]);for(unsigned j=0;j<active.size();++j)block(i,j)=W(active[i],active[j]);}Eigen::VectorXd solution=block.ldlt().solve(b);for(unsigned i=0;i<active.size();++i)lambda(active[i])=solution(i);}
  if(!lambda.allFinite()||lambda.minCoeff()<0)continue;Eigen::VectorXd normal=free+W*lambda;bool admissible=true;double residual=0;
  // Floating linear algebra backward error,not a force clipping tolerance.
  double bound=64*std::numeric_limits<double>::epsilon()*(free.norm()+W.norm()*lambda.norm());
  for(unsigned i=0;i<3;++i)if(mask&(1u<<i)){residual=std::max(residual,std::abs(normal(i)));if(std::abs(normal(i))>bound)admissible=false;}else if(normal(i)<0)admissible=false;
  if(admissible)return {lambda,normal,mask,residual};
 }
 throw std::runtime_error("no admissible acceleration subset;no regularization");
}
struct AccelerationStage {double time,weight;Eigen::VectorXd q,v,force,applied;unsigned mask;double residual;};
struct AccelerationRelease {Eigen::VectorXd q,v;std::vector<AccelerationStage>stages;double minimumGap=0,momentumResidual=0,minimumForce=0,endTime=0;unsigned finalMask=7;};
inline AccelerationRelease accelerationRelease(const SharedFilmSystem&s,const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time,double h,const std::vector<EdgeOwner>&edges,unsigned grid){
 if(grid<8||grid>128||edges.size()!=3||!(h>0&&h<=.0001))throw std::invalid_argument("bounded edge release reference");
 unsigned n=q.size();Eigen::VectorXd diagonal=s.shared.M.diagonal();Eigen::MatrixXd off=s.shared.M-diagonal.asDiagonal().toDenseMatrix();if(off.cwiseAbs().maxCoeff()!=0||diagonal.minCoeff()<=0)throw std::domain_error("exact diagonal projected mass required");
 AccelerationRelease out;out.minimumGap=s.clearance(q);out.minimumForce=std::numeric_limits<double>::infinity();Eigen::VectorXd y(2*n),impulse=Eigen::VectorXd::Zero(n);y.head(n)=q;y.tail(n)=v;
 auto rhs=[&](const Eigen::VectorXd&state,double t,double weight){Eigen::VectorXd x=state.head(n),vel=state.tail(n);auto g=edgeGeometry(s,x,edges);Eigen::VectorXd applied=s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension).value-2*s.shared.M*vel;Eigen::VectorXd a=applied.cwiseQuotient(diagonal),free=g.J*a;for(unsigned i=0;i<3;++i)free(i)+=vel.dot(g.H[i]*vel);Eigen::MatrixXd miJ=g.J.transpose();for(unsigned i=0;i<n;++i)miJ.row(i)/=diagonal(i);Eigen::MatrixXd W=g.J*miJ;auto contact=accelerationReaction(W,free);
  for(unsigned i=0;i<3;++i)if(contact.force(i)>0&&(std::abs(g.gap(i))>1e-10||std::abs(g.J.row(i).dot(vel))>1e-10)){std::ostringstream error;error<<std::setprecision(17)<<"positive acceleration reaction outside touching tangent state;reimpact requires separate law:time="<<t<<" row="<<i<<" gap="<<g.gap(i)<<" vn="<<g.J.row(i).dot(vel)<<" force="<<contact.force(i);throw std::runtime_error(error.str());}
  out.minimumGap=std::min(out.minimumGap,s.clearance(x));if(out.minimumGap< -1e-10)throw std::runtime_error("acceleration release whole RK-stage gap fails;no projection");
  Eigen::VectorXd total=applied+g.J.transpose()*contact.force,derivative(2*n);derivative.head(n)=vel;derivative.tail(n)=total.cwiseQuotient(diagonal);impulse+=weight*total;out.minimumForce=std::min(out.minimumForce,contact.force.minCoeff());out.stages.push_back({t,weight,x,vel,contact.force,applied,contact.mask,contact.residual});return derivative;};
 double dt=h/grid,clock=time;for(unsigned i=0;i<grid;++i){Eigen::VectorXd k1=rhs(y,clock,dt/6),k2=rhs(y+dt/2*k1,clock+dt/2,dt/3),k3=rhs(y+dt/2*k2,clock+dt/2,dt/3),k4=rhs(y+dt*k3,clock+dt,dt/6);y+=dt/6*(k1+2*k2+2*k3+k4);clock+=dt;out.minimumGap=std::min(out.minimumGap,s.clearance(y.head(n)));if(out.minimumGap< -1e-10)throw std::runtime_error("acceleration release whole accepted-substep gap fails;no projection");}
 out.q=y.head(n);out.v=y.tail(n);out.endTime=clock;out.finalMask=out.stages.back().mask;out.momentumResidual=(s.shared.M*(out.v-v)-impulse).norm();if(!y.allFinite()||out.momentumResidual>1e-17||out.minimumForce<0||out.stages.back().time!=clock)throw std::runtime_error("acceleration release finite/momentum/nonnegative/accumulated clock gate");return out;
}
}
