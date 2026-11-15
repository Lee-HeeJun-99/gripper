#pragma once
#include <cmath>
#include <stdexcept>
#include <vector>
#include <limits>
#include <algorithm>
namespace regrip_event_clock {
struct Schedule{
 double base=0,quantum=0;unsigned resolution=0;unsigned long long tick=0;unsigned steps=0;
 std::vector<unsigned long long>events;std::vector<unsigned>divisors;
 Schedule(double h,const std::vector<double>&times,const std::vector<unsigned>&levels):base(h){
  if(!std::isfinite(h)||h<=0||times.empty()||times.size()!=levels.size()||times.front()!=0)throw std::invalid_argument("bounded event schedule");
  for(unsigned d:levels){if(!d||d>16||(d&(d-1)))throw std::invalid_argument("dyadic event divisors only");if(d>resolution)resolution=d;}
  quantum=h/resolution;
  for(size_t i=0;i<times.size();++i){
   if(!std::isfinite(times[i])||times[i]<0||times[i]>24||(i&&times[i]<=times[i-1]))throw std::invalid_argument("ordered0..24s events");
   auto k=std::llround(times[i]/quantum);
   if(std::abs(static_cast<double>(static_cast<long double>(k)*quantum)-times[i])>16*std::numeric_limits<double>::epsilon()*std::max(1.,times[i]))throw std::invalid_argument("event is not on dyadic time lattice");
   events.push_back(k);divisors.push_back(levels[i]);
  }
 }
 double time()const{return static_cast<double>(static_cast<long double>(tick)*quantum);}
 unsigned ticks()const{
  size_t index=0;while(index+1<events.size()&&tick>=events[index+1])++index;
  auto count=resolution/divisors[index];
  if(index+1<events.size()&&tick+count>events[index+1])count=unsigned(events[index+1]-tick);
  if(!count)throw std::runtime_error("zero step");
  return count;
 }
 double dt()const{return ticks()*quantum;}
 void advance(){if(steps>=240000)throw std::runtime_error("event step budget exceeded");tick+=ticks();++steps;if(time()>24+base)throw std::runtime_error("event duration budget exceeded");}
};
}
