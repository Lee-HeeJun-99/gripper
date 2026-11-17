#include "../models/film_impact/AffineBirth.h"
#include "../models/film_impact/RestartHistory.h"
#include <iostream>
using namespace regrip_film_impact;
void check(bool b){if(!b)throw std::runtime_error("birth/restart reference mismatch");}
int main(){try{
 Eigen::Vector3d x(2,0,0),d(-4,0,0);
 auto e=affineSphereBirth(x,d,1);check(e&&e->fraction==.25&&e->normal(0)==1);
 // Endpoints BOTH outside, event must not disappear.
 check((x+d).norm()>1);
 auto derivative=birthEndpointDerivative(*e,d);
 for(int i=0;i<3;++i){auto a=d,b=d;a(i)+=1e-6;b(i)-=1e-6;
  double fd=(affineSphereBirth(x,a,1)->fraction-affineSphereBirth(x,b,1)->fraction)/2e-6;
  check(std::abs(fd-derivative(i))<1e-9);}
 check(!affineSphereBirth(x,Eigen::Vector3d(1,0,0),1));
 bool rejected=false;try{affineSphereBirth(Eigen::Vector3d(-2,1,0),Eigen::Vector3d(4,0,0),1);}catch(const std::domain_error&){rejected=true;}check(rejected);
 auto zero=affineSphereBirth(Eigen::Vector3d(1,0,0),Eigen::Vector3d(-1,0,0),1);check(zero&&zero->fraction==0);
 RestartHistory history;check(!history.useBDF2(.1));history.acceptSmoothStep(.1);check(history.useBDF2(.1));
 history.impact();check(!history.useBDF2(.1));history.acceptSmoothStep(.025);check(!history.useBDF2(.1));
 history.acceptSmoothStep(.1);check(history.useBDF2(.1));
 std::cout<<"PASS affine point-sphere event/IFT, grazing rejection and restart eligibility;NOT triangle CCD or SOFA integration\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
