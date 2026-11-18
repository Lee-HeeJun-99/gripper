#include "../../models/film_transmission/Kernel.h"
#include "../../extended/film_rail_tendon/Kernel.h"
#include <iomanip>
#include <iostream>
#include <limits>
template<class Model,class State,class Scalar>auto forceParts(const Model&m,const State&q,Scalar T){std::array<std::vector<long double>,3>force;for(auto&f:force)f.resize(3*m.size());m.elements(q,T,[&](const auto&e){if(e.kind>2)throw std::runtime_error("precision probe has no contact");for(unsigned a=0;a<3*e.ids.size();++a)force[e.kind][3*e.ids[a/3]+a%3]-=static_cast<long double>(e.energy.g[a]);});return force;}
int main(int argc,char**argv){try{
 if(argc!=4||std::numeric_limits<long double>::digits<=std::numeric_limits<double>::digits)throw std::runtime_error("samples,mass,output and genuinely extended precision required");using namespace regrip_transmission;auto m=model();regrip_film_rail_ext::Assembly high(21);high.railW=m.railW;high.bondK=m.bondK;high.guideOffset=m.guideOffset;high.rootGuideSecondOrder=m.rootGuideSecondOrder;
 for(unsigned i=0;i<m.parts.size();++i){auto&p=high.parts[i];const auto&d=m.parts[i];p.width=d.width;p.thickness=d.thickness;p.y=d.y;p.z=d.z;}
 auto rest=m.rest();for(const auto&p:rest)high.frozenRest.push_back({p[0],p[1],p[2]});auto mass=publicMass(argv[2]);std::vector<Point>zero(m.size());auto map=mechanics(m,zero,zero,.0001,0,mass);std::ifstream in(argv[1]);unsigned count;in>>count;if(count<1||count>8)throw std::runtime_error("minimal bounded precision probe");std::ofstream out(argv[3]);out<<std::setprecision(21)<<"sample,kind,double_projected_force_N,extended_projected_force_N,absolute_L2_difference_N,relative_percent,max_abs_difference_N\n";
 for(unsigned k=0;k<count;++k){double T;in>>T;std::vector<Point>q(m.size());std::vector<regrip_film_ext::Point>extended(m.size());for(unsigned i=0;i<q.size();++i)for(unsigned d=0;d<3;++d){in>>q[i][d];extended[i][d]=q[i][d];}if(!in)throw std::runtime_error("actual precision input invalid");auto low=forceParts(m,q,T),ref=forceParts(high,extended,static_cast<long double>(T));
  for(unsigned kind=0;kind<3;++kind){std::vector<long double>f(map.freeSize),g(map.freeSize);for(unsigned a=0;a<map.index.size();++a)if(map.index[a]>=0){f[map.index[a]]+=map.weight[a]*low[kind][a];g[map.index[a]]+=map.weight[a]*ref[kind][a];}long double a=0,b=0,error=0,maximum=0;for(unsigned i=0;i<f.size();++i){a+=f[i]*f[i];b+=g[i]*g[i];error+=(f[i]-g[i])*(f[i]-g[i]);maximum=std::max(maximum,std::abs(f[i]-g[i]));}a=std::sqrt(a);b=std::sqrt(b);error=std::sqrt(error);out<<k<<','<<kind<<','<<a<<','<<b<<','<<error<<',';if(b>0)out<<100*error/b;out<<','<<maximum<<'\n';}
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
