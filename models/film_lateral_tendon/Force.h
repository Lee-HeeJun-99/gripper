#pragma once
#include "Route.h"
#include "../film_native_contact/CoupledPlaneStep.h"
namespace regrip_lateral_contact {
// Same existing implicit-stage pullback algorithm as routed_contact/Force.h;
// ONLY the cable provider changes. Original adapter/model remains untouched.
inline regrip_film_native::CoupledPlaneStep::Evaluation evaluate(const regrip_film_native::CoupledPlaneStep&stage,const Eigen::VectorXd&y,double lateral){
 using namespace regrip_film_native;regrip_lateral_tendon::validate(stage.model,lateral);
 CoupledPlaneStep core(stage.model,stage.mass,stage.h,stage.damping,0,stage.previous,stage.previousVelocity,stage.J,stage.target);auto e=core.evaluate(y);auto q=stage.previous,v=stage.expand(y);for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d)q[i][d]+=stage.h*v[i][d];
 regrip_lateral_tendon::route(stage.model,q,stage.T,lateral,[&](const Element&el){e.phi+=el.energy.v;for(unsigned a=0;a<3*el.ids.size();++a){unsigned ga=3*el.ids[a/3]+a%3;int i=stage.index[ga];if(i<0)continue;e.gradient(i)+=stage.h*stage.weight[ga]*el.energy.g[a];for(unsigned b=0;b<3*el.ids.size();++b){unsigned gb=3*el.ids[b/3]+b%3;int j=stage.index[gb];if(j>=0)e.tangent(i,j)+=stage.h*stage.h*stage.weight[ga]*stage.weight[gb]*el.energy.h[N*a+b];}}});return e;
}
}
