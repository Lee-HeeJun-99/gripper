#include "../models/contact_energy/SlipBandReference.h"
#include "../models/integrated/Kernels.h"
#include <iostream>
#include <iomanip>
int main(){try{
 constexpr double a=.3192,C=3e-6,k=.001;std::cout<<std::setprecision(17)<<"displacement,h,grid_shift,point_D,reference_D,relative_D,relative_force,active_band_mm\n";
 for(double d:{1e-4,1e-6}){
  auto ref=regrip_slip_band::reference(a,C,k,d),gauss=regrip_slip_band::splitGauss3(a,C,k,d);
  if(ref.plastic<=0||std::abs(gauss.plastic-ref.plastic)/ref.plastic>1e-10L||std::abs(2*ref.elastic+ref.plastic-d*ref.force)>1e-28L)throw std::runtime_error("independent split-integral/energy identity");
  for(double h:{.01,.005,.0025,.00125,.000625,.0003125,.00015625})for(double fraction:{0.,.25,.5}){
   unsigned n=std::lround(2/h);double D=0,F=0;
   for(unsigned i=0;i<n;++i){double s=-1+(i+.5)*h-h*fraction,cap=std::max(0.,C*(1-s*s/(a*a)));auto r=regrip_integrated::slider(d,0,k,cap);D+=h*r.dissipation;F+=h*r.traction;}
   std::cout<<d<<','<<h<<','<<fraction<<','<<D<<','<<double(ref.plastic)<<','<<double(std::abs(D-ref.plastic)/ref.plastic)<<','<<double(std::abs(F-ref.force)/ref.force)<<','<<double(ref.band)<<'\n';
  }
  long double eps=d*1e-4L;auto left=regrip_slip_band::reference(a,C,k,d-eps),right=regrip_slip_band::reference(a,C,k,d+eps);long double derivative=((right.elastic+right.plastic)-(left.elastic+left.plastic))/(2*eps);
  if(std::abs(derivative-ref.force)/ref.force>1e-8L)throw std::runtime_error("incremental U+D derivative versus actual traction integral");
 }
 std::cerr<<"PASS analytic versus split Gauss3,local energy and incremental work derivative. Midpoint alias FAILs are measurements,NOT hidden or production fixes.\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
