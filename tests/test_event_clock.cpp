#include "../models/event_step_clock/Schedule.h"
#include <iostream>
int main(){try{
 for(unsigned divisor:{1u,2u,4u}){
  regrip_event_clock::Schedule c(.00025,{0,16},{1,divisor});unsigned expected=64000+8000*divisor;
  for(unsigned i=0;i<expected;++i){double t=c.time();if(i<=64000&&t!=double(static_cast<long double>(i)*.00025))throw std::runtime_error("uniform prefix changed");if((i<64000? .00025:.00025/divisor)!=c.dt())throw std::runtime_error("wrong explicit time step");c.advance();}
  if(c.time()!=18||c.steps!=expected)throw std::runtime_error("exact final event time");
 }
 for(auto test:{0,1,2}){bool rejected=false;try{regrip_event_clock::Schedule c(.00025,test==0?std::vector<double>{0,16.00001}:std::vector<double>{0,16},test==1?std::vector<unsigned>{1,3}:test==2?std::vector<unsigned>{1}:std::vector<unsigned>{1,4});}catch(const std::invalid_argument&){rejected=true;}if(!rejected)throw std::runtime_error("invalid grid accepted");}
 std::cout<<"PASS dyadic event grid,exact prefix/time,invalid-event rejection\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
