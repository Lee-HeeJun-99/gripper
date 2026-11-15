#include "../models/conservative_beam/EnergyKernel.h"
#include "BeamReferenceV1.inc"
#include <random>
#include <iostream>
#include <chrono>
int main(){try{using namespace regrip3d;std::mt19937 gen(1811);std::uniform_real_distribution<double>d(-.5,.5);Pose a0,b0;b0.p={10,0,0};regrip_beam::Properties p{183,60,60,8,10.6666667,10.6666667};beam_reference_v1::Properties pp{183,60,60,8,10.6666667,10.6666667};double maxF=0,maxJ=0,maxE=0;for(int state=0;state<100;++state){Pose a=a0,b=b0;for(int j=0;j<3;++j){a.p[j]+=d(gen);b.p[j]+=d(gen);}a.q=exp(V{d(gen),d(gen),d(gen)});b.q=exp(V{d(gen),d(gen),d(gen)});auto r=regrip_beam::evaluate(a,b,a0,b0,p),old=beam_reference_v1::evaluate(a,b,a0,b0,pp);maxE=std::max(maxE,std::abs(r.energy-old.energy));for(int i=0;i<12;++i)maxF=std::max(maxF,std::abs(r.force[i]-old.force[i]));for(int i=0;i<144;++i)maxJ=std::max(maxJ,std::abs(r.jacobian[i]-old.jacobian[i]));}if(maxE>1e-11||maxF>1e-10||maxJ>1e-9)throw std::runtime_error("constant propagation differs from dense reference");std::cout<<"PASS100 dense-reference equivalence E="<<maxE<<" F="<<maxF<<" J="<<maxJ<<'\n';}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
