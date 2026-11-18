#pragma once
#include "Elements.h"
#include "../film_transmission/Gauss.h"
namespace regrip_precise_attachment {
inline regrip_transmission::Parts parts(const regrip_transmission::CoupledPlaneStep&m,const std::vector<Point>&q,double T,double lateral){
 using namespace regrip_transmission;
 Parts out{Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::VectorXd::Zero(m.freeSize),Eigen::MatrixXd::Zero(m.freeSize,m.freeSize)};
 out.cable=elements(m.model,q,T,lateral,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)out.skin+=e.energy.v;else out.rails+=e.energy.v;}else if(e.kind==1)out.bond+=e.energy.v;
 for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=m.index[ga];if(i<0)continue;double f=-m.weight[ga]*e.energy.g[a];out.force(i)+=f;if(e.kind==1)out.attachment(i)+=f;if(e.kind==2)out.tendon(i)+=f;for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=m.index[gb];if(j>=0)out.stiffness(i,j)+=m.weight[ga]*m.weight[gb]*e.energy.h[N*a+b];}}
 });return out;
}
}
