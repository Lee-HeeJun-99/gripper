#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitive.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_film_rail;
struct Route{double base,amplitude;double offset(unsigned i,unsigned nx)const{if(amplitude==0)return base;double s=double(i)/(nx-1);return base-4*amplitude*s*(1-s);}};
struct Evaluation{double energy=0,length=0,gap=1e9;std::vector<double>force,H;std::array<std::vector<Point>,2>guides;};
Evaluation evaluate(const Assembly&m,const std::vector<Point>&q,Route route){
 Evaluation out;unsigned n=3*m.size();out.force.resize(n);out.H.resize(n*n);auto rest=m.rest(),actual=rest;for(unsigned i=0;i<q.size();++i)actual[i]=add(actual[i],q[i]);
 for(unsigned part:{1u,2u}){
  for(unsigned k=0;k<=m.guideIntervals;++k){unsigned i=(m.nx-1)*k/m.guideIntervals;Assembly::Local loc(m.guideIds(part,i),actual);auto p=m.guide(loc,part,i,-route.offset(i,m.nx));out.guides[part-1].push_back({p[0].v,p[1].v,p[2].v});}
  for(unsigned k=0;k<m.guideIntervals;++k){unsigned a=(m.nx-1)*k/m.guideIntervals,b=(m.nx-1)*(k+1)/m.guideIntervals;auto ids=m.guideIds(part,a),next=m.guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Assembly::Local loc(ids,actual),ref(ids,rest);auto d=sub(m.guide(loc,part,b,-route.offset(b,m.nx)),m.guide(loc,part,a,-route.offset(a,m.nx))),d0=sub(m.guide(ref,part,b,-route.offset(b,m.nx)),m.guide(ref,part,a,-route.offset(a,m.nx)));auto length=root(dot(d,d));AD E=length-AD(root(dot(d0,d0)).v);out.energy+=E.v;out.length+=length.v;
   for(unsigned i=0;i<3*loc.ids.size();++i){unsigned gi=3*loc.ids[i/3]+i%3;out.force[gi]-=E.g[i];for(unsigned j=0;j<3*loc.ids.size();++j){unsigned gj=3*loc.ids[j/3]+j%3;out.H[n*gi+gj]+=E.h[N*i+j];}}
  }
 }
 regrip_three_finger::Layout layout;auto center=layout.mount[0].R.transpose()*(layout.bodyCenter-layout.mount[0].origin);Point c{center[0],center[1],center[2]};for(const auto&rail:out.guides)for(unsigned k=0;k+1<rail.size();++k)out.gap=std::min(out.gap,regrip_film_sphere::ClosestPrimitive::evaluate({rail[k],rail[k+1]},c,layout.bodyRadius).gap.v);return out;
}
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("exclusive output prefix required");Assembly m(21);m.guideIntervals=4;m.guideOffset=5;m.rootGuideSecondOrder=true;auto rest=m.rest();std::vector<Point>zero(m.size()),q(m.size());for(unsigned i=0;i<q.size();++i){auto x=rest[i];q[i]={.002*std::sin(.05*x[0]),.001*std::cos(.02*x[0]+.2*x[1]),.01*std::sin(.03*x[0])*std::cos(.04*x[1])};}
 std::string prefix=argv[1];std::ofstream rows(prefix+".routes.csv"),guides(prefix+".guides.csv"),station(prefix+".station_force.csv");rows<<std::setprecision(17)<<"variant,base_mm,amplitude_mm,initial_cable_length_mm,initial_centreline_sphere_gap_mm,force_FD_N,Hessian_FD_N_mm,objectivity_Nmm,net_force_N,net_moment_Nmm,baseline_force_H_max_abs\n";guides<<std::setprecision(17)<<"variant,rail,guide,x,y,z\n";station<<std::setprecision(17)<<"variant,x,unit_tendon_station_Fz\n";unsigned variant=0;
 for(Route route:{Route{5,0},Route{2,0},Route{5,4.5}}){auto initial=evaluate(m,zero,route),e=evaluate(m,q,route);double forceFD=0,hessianFD=0,parity=0;unsigned n=3*m.size();
  if(variant==0){std::vector<double>f(n),H(n*n);m.elements(q,1.,[&](const Element&a){if(a.kind!=2)return;for(unsigned i=0;i<3*a.ids.size();++i){unsigned gi=3*a.ids[i/3]+i%3;f[gi]-=a.energy.g[i];for(unsigned j=0;j<3*a.ids.size();++j)H[n*gi+3*a.ids[j/3]+j%3]+=a.energy.h[N*i+j];}});for(unsigned i=0;i<n;++i)parity=std::max(parity,std::abs(f[i]-e.force[i]));for(unsigned i=0;i<n*n;++i)parity=std::max(parity,std::abs(H[i]-e.H[i]));}
  for(unsigned j:{3*m.id(1,5,0)+2,3*m.id(1,20,0)+2,3*m.id(2,10,2)}){double h=1e-5;auto plus=q,minus=q;plus[j/3][j%3]+=h;minus[j/3][j%3]-=h;auto p=evaluate(m,plus,route),a=evaluate(m,minus,route);forceFD=std::max(forceFD,std::abs(-(p.energy-a.energy)/(2*h)-e.force[j]));for(unsigned i=0;i<n;++i)hessianFD=std::max(hessianFD,std::abs((p.force[i]-a.force[i])/(2*h)+e.H[n*i+j]));}
  Point F{},moment{};for(unsigned i=0;i<q.size();++i){Point f{e.force[3*i],e.force[3*i+1],e.force[3*i+2]};F=add(F,f);moment=add(moment,cross(add(rest[i],q[i]),f));}
  auto rotate=[](Point x){double c=std::cos(.37),s=std::sin(.37),a=std::cos(.29),b=std::sin(.29);Point y{a*x[0]+b*x[2],x[1],-b*x[0]+a*x[2]};return Point{c*y[0]-s*y[1],s*y[0]+c*y[1],y[2]};};auto rotated=q;for(unsigned i=0;i<q.size();++i)rotated[i]=sub(add(rotate(add(rest[i],q[i])),Point{1,2,3}),rest[i]);auto r=evaluate(m,rotated,route);double objective=std::abs(r.energy-e.energy);
  double netF=std::sqrt(dot(F,F)),netM=std::sqrt(dot(moment,moment));rows<<variant<<','<<route.base<<','<<route.amplitude<<','<<initial.length<<','<<initial.gap<<','<<forceFD<<','<<hessianFD<<','<<objective<<','<<netF<<','<<netM<<','<<parity<<'\n';rows.flush();
  for(unsigned part=0;part<2;++part)for(unsigned k=0;k<initial.guides[part].size();++k){const auto&p=initial.guides[part][k];guides<<variant<<','<<part<<','<<k<<','<<p[0]<<','<<p[1]<<','<<p[2]<<'\n';}
  for(unsigned i=0;i<m.nx;++i){double fz=0;for(unsigned part:{1u,2u})for(unsigned j=0;j<m.parts[part].ny;++j)fz+=initial.force[3*m.id(part,i,j)+2];station<<variant<<','<<100.*i/(m.nx-1)<<','<<fz<<'\n';}
  // SAME independent kernel gates as tests/test_film_rail_tendon.cpp.
  if(forceFD>1e-8||hessianFD>1e-5||objective>1e-10||netF>1e-10||netM>1e-9||parity>1e-12)throw std::runtime_error("routed preflight force/Hessian/objectivity/wrench/baseline identity gate failed");++variant;
 }
 std::cout<<"PASS independent route geometry/force preflight;unit multiplier differentiates length,NOT1N SOFA actuation;NOT candidate dynamics/grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
