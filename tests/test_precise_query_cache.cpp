#include "../models/film_routed_contact/PreciseQueryCache.h"
#include <iostream>
#include <random>
using namespace regrip_three_finger;
int original(const TriangleCoordinates&a,const TriangleCoordinates&b){try{return preciseOrder(a,b);}catch(const UnresolvedDistanceOrder&){return rationalOrder(a,b);}}
int main(){std::mt19937_64 rng(1327);std::uniform_real_distribution<double>u(-30,30);unsigned comparisons=0,unique=0,fallbacks=0;
 for(unsigned query=0;query<8;++query){std::vector<TriangleCoordinates>x(16);for(auto&t:x)for(auto&p:t)for(double&v:p)v=u(rng);x[1]=x[0];x[2]={x[0][2],x[0][1],x[0][0]};PreciseQueryCache cache(x);
  for(unsigned a=0;a<x.size();++a)for(unsigned b=0;b<x.size();++b){int before=original(x[a],x[b]),after=cache.compare(a,b,[&]{++fallbacks;return original(x[a],x[b]);});if(before!=after)throw std::runtime_error("exact ordering/fallback parity failed");++comparisons;}
  if(cache.evaluations!=x.size())throw std::runtime_error("not exactly one Q/H evaluation per queried triangle");unique+=cache.evaluations;
 }
 std::vector<TriangleCoordinates>bad(2);bad[0]={{{0,0,0},{1,0,0},{0,1,0}}};bad[1]={{{1,0,0},{1,0,0},{1,0,0}}};bool a=false,b=false;try{original(bad[1],bad[0]);}catch(const std::domain_error&){a=true;}try{PreciseQueryCache cache(bad);cache.compare(1,0,[&]{return original(bad[1],bad[0]);});}catch(const std::domain_error&){b=true;}if(!a||a!=b)throw std::runtime_error("degenerate rejection differs");
 std::cout<<"PASS exact Q/H comparison and original rational fallback;comparisons="<<comparisons<<",unique_distance_evaluations="<<unique<<",fallbacks="<<fallbacks<<";NOT actual runtime/force/state qualification\n";
}
