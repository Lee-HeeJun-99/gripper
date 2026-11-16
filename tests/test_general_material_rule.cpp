#include "../models/general_vector_history/AdaptiveMaterialRule.h"
#include <iostream>
int main(){try{
 double maximum=0;
 for(double amplitude:{1.,1e-20}){
  auto density=[amplitude](double s){std::array<double,11> y{};y[0]=1;y[2]=amplitude*std::max(0.,s-.3141592653589793);return y;};
  auto rule=regrip_general_history::adaptiveMaterialRule(8,1.,density);
  double D=0;for(auto [s,w]:rule)D+=w*density(s)[2];
  double exact=.5*amplitude*std::pow(1-.3141592653589793,2);
  double error=std::abs(D-exact)/exact;maximum=std::max(maximum,error);
  if(error>1e-5)throw std::runtime_error("positive-part front integral");
 }
 std::cout<<"PASS material front quadrature relative="<<maximum<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
