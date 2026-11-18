#include "../models/film_three_finger_resume/FaceBranch.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_resume;
int main(){try{
 double valueError=0,gradientError=0,HessianError=0;for(double x:{.1,.25,.5}){std::vector<Point>tri={{-x,-.25,-1},{1-x,-.25,-1},{-x,.75,-1}};auto branch=faceBranch(tri,1);auto physical=ClosestPrimitive::evaluate(tri,{0,0,0},1);if(physical.feature!=6)throw std::runtime_error("interior fixture differs");valueError=std::max(valueError,std::abs(branch.geometry.gap.v-physical.gap.v));for(unsigned a=0;a<9;++a){gradientError=std::max(gradientError,std::abs(branch.geometry.gap.g[a]-physical.gap.g[a]));for(unsigned b=0;b<9;++b)HessianError=std::max(HessianError,std::abs(branch.geometry.gap.h[regrip_film::N*a+b]-physical.gap.h[regrip_film::N*a+b]));}if(branch.barycentric[0]<=0||branch.barycentric[1]<=0||branch.barycentric[2]<=0)throw std::runtime_error("inside-face parameter sign differs");}
 auto outside=faceBranch({{.1,-.25,-1},{1.1,-.25,-1},{.1,.75,-1}},1);if(outside.barycentric[1]>=0)throw std::runtime_error("outside extension boundary sign differs");if(valueError!=0||gradientError!=0||HessianError!=0)throw std::runtime_error("extension differs from existing physical feature6 expression");std::cout<<std::setprecision(17)<<"PASS face extension value/gradient/Hessian EXACT in3 physical interior fixtures;outside parameter sign only,NOT physical outside force/SOFA\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
