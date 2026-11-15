#include "../models/fixed_step_clock/Clock.h"
#include <iostream>
int main(){try{
 unsigned oldLate=0,newLate=0;
 for(double h:{.0005,.00025,.000125})for(double event:{.5,3.,6.,14.,15.,16.}){
  unsigned expected=std::lround(event/h),old=0,fixed=0;double time=0;
  while(time<event-1e-12){time+=h;++old;}
  while(regrip_clock::timeAt(0,h,fixed)<event-1e-12)++fixed;
  oldLate+=old!=expected;newLate+=fixed!=expected;
  std::cout<<h<<','<<event<<','<<expected<<','<<old<<','<<fixed<<'\n';
 }
 if(oldLate!=4||newLate)throw std::runtime_error("fixed clock schedule event regression");
 std::cout<<"PASS old_misaligned="<<oldLate<<" fixed_misaligned="<<newLate<<'\n';return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
