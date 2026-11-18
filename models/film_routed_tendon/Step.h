#pragma once
#include "Route.h"
#include "../film_transmission/Gauss.h"
namespace regrip_routed_tendon {
using namespace regrip_transmission;
inline Parts parts(const CoupledPlaneStep&m,const std::vector<Point>&q,double T,double amplitude){
 Parts out{Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::MatrixXd::Zero(m.freeSize,m.freeSize)};
 out.cable=elements(m.model,q,T,amplitude,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)out.skin+=e.energy.v;else out.rails+=e.energy.v;}else if(e.kind==1)out.bond+=e.energy.v;
  for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=m.index[ga];if(i<0)continue;double f=-m.weight[ga]*e.energy.g[a];out.force(i)+=f;if(e.kind==1)out.attachment(i)+=f;if(e.kind==2)out.tendon(i)+=f;for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=m.index[gb];if(j>=0)out.stiffness(i,j)+=m.weight[ga]*m.weight[gb]*e.energy.h[N*a+b];}}
 });return out;
}
inline Step step(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass,double amplitude){
 validate(m,amplitude);if(h<=0||h>.001||time<0||time+h>.05000000000001)throw std::invalid_argument("bounded separate routed coupon");auto map=mechanics(m,q,v,h,0,mass);auto out=gauss(filmMass(map),map.pack(q),map.pack(v),time,h,[&](const Eigen::VectorXd&x,double t){return parts(map,map.expand(x),holdControl().sample(t).tension,amplitude);},time==0);Step result{map.expand(out.q),map.expand(out.v),out.residual,out.evaluations};result.highOrder=true;for(unsigned i=0;i<2;++i){result.stageQ[i]=map.expand(out.stageQ[i]);result.stageV[i]=map.expand(out.stageV[i]);result.stageTime[i]=time+(.5+(i?1:-1)*std::sqrt(3.)/6)*h;result.stageT[i]=holdControl().sample(result.stageTime[i]).tension;}return result;
}
}
