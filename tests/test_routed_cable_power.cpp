#include "../diagnostics/film_three_finger/RoutedCablePower.h"
#include <iostream>
#include <iomanip>
using namespace regrip_cable_observer;
int main(){try{
 Assembly m(21);m.guideIntervals=4;m.guideOffset=5;m.rootGuideSecondOrder=true;auto rest=m.rest();std::vector<Point>u(m.size()),v(m.size());
 for(unsigned i=0;i<u.size();++i){double x=rest[i][0],y=rest[i][1];u[i]={.002*std::sin(.05*x),.001*std::cos(.02*x+.2*y),.01*std::sin(.03*x)*std::cos(.04*y)};v[i]={.1*std::cos(.07*x),.1*std::sin(.12*y),.1*std::sin(.1*x+.1*y)};}
 auto observed=evaluate(m,u,v);double full=0;
 // Unit multiplier differentiates length,NOT an applied1N dynamic experiment.
 m.elements(u,1.,[&](const Element&e){if(e.kind==2)for(unsigned i=0;i<3*e.ids.size();++i)full-=e.energy.g[i]*v[e.ids[i/3]][i%3];});
 if(full!=observed.shorteningRate||m.cableLength(u)!=observed.length)throw std::runtime_error("existing full AD cable gradient/length differs");
 double h=.00025;auto plus=u,minus=u;for(unsigned i=0;i<u.size();++i)for(unsigned d=0;d<3;++d){plus[i][d]+=h*v[i][d];minus[i][d]-=h*v[i][d];}double fd=-(m.cableLength(plus)-m.cableLength(minus))/(2*h);
 if(!std::isfinite(fd)||std::abs(fd-observed.shorteningRate)>1e-7)throw std::runtime_error("independent directional cable-length FD failed");
 auto rotate=[](Point x){double c=std::cos(.37),s=std::sin(.37);return Point{c*x[0]-s*x[1],s*x[0]+c*x[1],x[2]};};auto ur=u,vr=v;std::vector<Point>rigid(v.size());for(unsigned i=0;i<u.size();++i){auto x=add(rest[i],u[i]);auto r=rotate(x);ur[i]=sub(add(r,Point{1,2,3}),rest[i]);vr[i]=rotate(v[i]);rigid[i]=add(Point{.1,.2,.3},Point{-.01*x[1],.01*x[0],0});}
 auto transformed=evaluate(m,ur,vr),rigidPower=evaluate(m,u,rigid);
 if(std::abs(transformed.length-observed.length)>1e-12||std::abs(transformed.shorteningRate-observed.shorteningRate)>1e-12||std::abs(rigidPower.shorteningRate)>1e-12)throw std::runtime_error("cable objectivity/rigid power identity");
 bool rejected=false;try{auto collapsed=u;for(unsigned i=0;i<u.size();++i)collapsed[i]=scale(rest[i],-1.);evaluate(m,collapsed,v);}catch(const std::domain_error&){rejected=true;}if(!rejected)throw std::runtime_error("degenerate guide accepted");
 std::cout<<std::setprecision(17)<<"PASS exact full AD-gradient/length agreement,objectivity,rigid power,degenerate rejection;NOT actual energy certification\nAD_rate="<<observed.shorteningRate<<" FD_rate="<<fd<<" FD_absolute_error="<<std::abs(fd-observed.shorteningRate)<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
