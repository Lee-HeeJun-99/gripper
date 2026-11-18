#include "../models/film_routed_tendon/Route.h"
#include <iostream>
#include <iomanip>
using namespace regrip_routed_tendon;
struct Result{double E=0;std::vector<double>f,H;};
Result evaluate(const Assembly&m,const std::vector<Point>&q,double amplitude,bool original=false){unsigned n=3*m.size();Result out{0,std::vector<double>(n),std::vector<double>(n*n)};auto visit=[&](const Element&e){out.E+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){unsigned i=3*e.ids[a/3]+a%3;out.f[i]-=e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b){unsigned j=3*e.ids[b/3]+b%3;out.H[n*i+j]+=e.energy.h[N*a+b];}}};if(original)m.elements(q,.001,visit);else elements(m,q,.001,amplitude,visit);return out;}
int main(){try{
 Assembly m(21);m.guideOffset=5;m.guideIntervals=4;m.rootGuideSecondOrder=true;auto rest=m.rest();std::vector<Point>q(m.size());for(unsigned i=0;i<q.size();++i){auto x=rest[i];q[i]={.002*std::sin(.05*x[0]),.001*std::cos(.02*x[0]+.2*x[1]),.01*std::sin(.03*x[0])*std::cos(.04*x[1])};}double maxF=0,maxH=0,baseline=0;
 for(double amp:{0.,4.5}){auto e=evaluate(m,q,amp);unsigned n=e.f.size();if(amp==0){auto old=evaluate(m,q,0,true);baseline=std::abs(old.E-e.E);for(unsigned i=0;i<n;++i)baseline=std::max(baseline,std::abs(old.f[i]-e.f[i]));for(unsigned i=0;i<n*n;++i)baseline=std::max(baseline,std::abs(old.H[i]-e.H[i]));if(length(m,q,0)!=m.cableLength(q))throw std::runtime_error("baseline actual cable length differs");}
  for(unsigned j:{3*m.id(0,5,0)+2,3*m.id(1,5,0)+2,3*m.id(2,10,2)}){double h=1e-6;auto plus=q,minus=q;plus[j/3][j%3]+=h;minus[j/3][j%3]-=h;auto p=evaluate(m,plus,amp),a=evaluate(m,minus,amp);maxF=std::max(maxF,std::abs(-(p.E-a.E)/(2*h)-e.f[j]));for(unsigned i=0;i<n;++i)maxH=std::max(maxH,std::abs((p.f[i]-a.f[i])/(2*h)+e.H[n*i+j]));}
  Point force{},moment{};for(unsigned i=0;i<q.size();++i){Point f{e.f[3*i],e.f[3*i+1],e.f[3*i+2]};force=add(force,f);moment=add(moment,cross(add(rest[i],q[i]),f));}if(std::sqrt(dot(force,force))>1e-10||std::sqrt(dot(moment,moment))>1e-9)throw std::runtime_error("routed full-system wrench balance");
 }
 // Existing film/rail independent FD gates,not relaxed for the candidate.
 if(maxF>1e-8||maxH>1e-5||baseline>1e-12)throw std::runtime_error("routed full mechanics FD/baseline identity failed");
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"force_FD_N\":"<<maxF<<",\"Hessian_FD_N_mm\":"<<maxH<<",\"baseline_force_energy_H_max_abs\":"<<baseline<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
