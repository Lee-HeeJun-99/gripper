#include "../models/film_sphere_contact/ClosestPrimitive.h"
#include "../models/film_sphere_contact/ClosestPrimitiveValue.h"
#include <chrono>
#include <cstring>
#include <iostream>
#include <random>
using regrip_film::Point;
bool exact(double a,double b){return std::memcmp(&a,&b,sizeof(a))==0;}
int main(){
 std::mt19937_64 rng(20261118);std::uniform_real_distribution<double>u(-30,30);std::vector<std::vector<Point>>cases;
 for(unsigned n=1;n<=3;++n)for(unsigned j=0;j<4000;++j){std::vector<Point>x(n);for(auto&p:x)for(auto&v:p)v=u(rng);cases.push_back(x);}
 unsigned count=0;for(const auto&x:cases){auto a=regrip_film_sphere::ClosestPrimitive::evaluate(x,{.3,-.2,1.},8);auto b=regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(x,{.3,-.2,1.},8);if(a.feature!=b.feature||!exact(a.gap.v,b.gap.v))throw std::runtime_error("feature/gap primal mismatch");for(unsigned d=0;d<3;++d)if(!exact(a.point[d].v,b.point[d].v))throw std::runtime_error("closest point primal mismatch");++count;}
 unsigned rejected=0;for(const auto&x:std::vector<std::vector<Point>>{{{0,0,0}},{{1,1,1},{1,1,1}},{{1,0,0},{2,0,0},{3,0,0}}}){bool a=false,b=false;try{regrip_film_sphere::ClosestPrimitive::evaluate(x,{0,0,0},8);}catch(const std::exception&){a=true;}try{regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(x,{0,0,0},8);}catch(const std::exception&){b=true;}if(!a||a!=b)throw std::runtime_error("degenerate rejection mismatch");++rejected;}
 volatile double checksum=0;auto begin=std::chrono::steady_clock::now();for(const auto&x:cases)checksum+=regrip_film_sphere::ClosestPrimitive::evaluate(x,{.3,-.2,1.},8).gap.v;auto middle=std::chrono::steady_clock::now();for(const auto&x:cases)checksum+=regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(x,{.3,-.2,1.},8).gap.v;auto finish=std::chrono::steady_clock::now();
 std::cout<<"{\"status\":\"PASS\",\"random_bit_exact_cases\":"<<count<<",\"degenerate_rejections\":"<<rejected<<",\"AD_seconds\":"<<std::chrono::duration<double>(middle-begin).count()<<",\"value_seconds\":"<<std::chrono::duration<double>(finish-middle).count()<<",\"checksum\":"<<checksum<<"}\n";
}
