#pragma once
#include "../film_coupled_contact/CoupledSphere.h"
#include <fstream>
namespace regrip_transmission {
using namespace regrip_coupled;
inline Assembly model(double bond=.001,double offset=5){Assembly m(21);m.guideIntervals=4;m.guideOffset=offset;m.bondK=bond;m.rootGuideSecondOrder=true;if((bond!=.001&&bond!=.01&&bond!=.0001)||(offset!=5&&offset!=-5))throw std::invalid_argument("separate declared single-factor coupon design required");return m;}
inline EventControl control(){EventControl c;c.maximum=.0001;c.ramp=.01;c.release=.02;c.end=.03;return c;}
inline std::vector<double>publicMass(const std::string&path){std::ifstream in(path);unsigned n;in>>n;if(!in||n!=231)throw std::runtime_error("actual231-node public mass required");std::vector<double>mass(n);for(double&x:mass){in>>x;if(!in||!std::isfinite(x)||x<=0)throw std::runtime_error("finite positive exact public nodal mass required");}return mass;}
inline CoupledPlaneStep mechanics(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double h,double T,const std::vector<double>&mass){return CoupledPlaneStep(m,mass,h,2,T,q,v,std::vector<Point>(m.size()),0);}
struct Parts {
 Eigen::VectorXd force,tendon,attachment;Eigen::MatrixXd stiffness;
 double skin=0,rails=0,bond=0,cable=0;
};
inline Parts parts(const CoupledPlaneStep&m,const std::vector<Point>&q,double T){
 Parts out{Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::MatrixXd::Zero(m.freeSize,m.freeSize)};
 m.model.elements(q,T,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)out.skin+=e.energy.v;else out.rails+=e.energy.v;}else if(e.kind==1)out.bond+=e.energy.v;
  for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=m.index[ga];if(i<0)continue;double f=-m.weight[ga]*e.energy.g[a];out.force(i)+=f;if(e.kind==1)out.attachment(i)+=f;if(e.kind==2)out.tendon(i)+=f;for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=m.index[gb];if(j>=0)out.stiffness(i,j)+=m.weight[ga]*m.weight[gb]*e.energy.h[N*a+b];}}
 });out.cable=m.model.cableLength(q);return out;
}
struct Step{std::vector<Point>q,v;double residual=0;unsigned evaluations=0;bool highOrder=false;std::array<std::vector<Point>,2>stageQ,stageV;std::array<double,2>stageTime{},stageT{};};
// The validated free block's System::smooth(false) is reused unchanged.
// A decoupled six-DOF dummy block is discarded;NO physical object/contact is present.
inline Step step(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass){
 if(!(h>0&&h<=.001)||time<0||time+h>.05000000000001)throw std::invalid_argument("bounded transmission coupon interval");
 Body dummy;dummy.center={0,0,1e6};System s(mechanics(m,q,v,h,control().sample(time+h/2).tension,mass),{{0,5,1}},dummy,1,true,true,false,1e-18,1e-10);auto r=s.smooth(time,control(),false);
 if(r.residual>1e-17)throw std::runtime_error("unchanged free-block momentum gate failed");return {std::move(r.state.q),std::move(r.state.v),r.residual,r.evaluations};
}
inline void quote(std::ostream&out,const std::vector<Point>&x){out<<",\"";for(const auto&p:x)for(double y:p)out<<y<<' ';out<<'"';}
}
