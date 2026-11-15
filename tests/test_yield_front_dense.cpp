#include "../models/yield_front_history/ScalarField.h"
#include "../models/integrated/Kernels.h"
#include <iostream>
#include <iomanip>
using namespace regrip_yield_front;
int main(){try{
 constexpr Real a=.3192L,C=3e-6L,k=.001L;Field field(a,k);Real exactD=0,exactF=0;
 for(int step=0;step<120;++step){Poly du{2e-5L*std::sin(.17L*step),1e-5L*std::cos(.13L*step),3e-6L*std::sin(.11L*step)};auto t=field.evaluate(du,step>=70&&step<80?.4L*C:C);exactD+=t.measures.dissipation;exactF=t.measures.traction;field.commit(t);}
 std::cout<<std::setprecision(17)<<"nodes,loss,reference_loss,relative_loss,relative_force\n";double first=0,last=0;
 for(unsigned n:{256u,1024u,4096u,16384u,65536u}){std::vector<double>u(n),z(n);double D=0,F=0;
  for(int step=0;step<120;++step){double d0=double(2e-5L*std::sin(.17L*step)),d1=double(1e-5L*std::cos(.13L*step)),d2=double(3e-6L*std::sin(.11L*step)),cap=double(step>=70&&step<80?.4L*C:C);F=0;
   for(unsigned i=0;i<n;++i){double x=-1+2.*(i+.5)/n;u[i]+=d0+x*(d1+x*d2);auto r=regrip_integrated::slider(u[i],z[i],double(k),cap*(1-x*x));z[i]=r.plastic;D+=double(2*a/n)*r.dissipation;F+=double(2*a/n)*r.traction;}
  }
  double error=double(std::abs(D-exactD)/exactD);if(n==256)first=error;last=error;
  std::cout<<n<<','<<D<<','<<double(exactD)<<','<<error<<','<<double(std::abs(F-exactF)/std::abs(exactF))<<'\n';
 }
 if(!(last<first&&last<1e-5))throw std::runtime_error("independent dense slider history fails to approach exact field");return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
