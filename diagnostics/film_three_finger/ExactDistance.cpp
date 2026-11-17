#include "../../models/film_three_finger/PreciseDistanceOrder.h"
#include <boost/multiprecision/cpp_int.hpp>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("recorded coordinate CSV required");std::ifstream in(argv[1]);std::string line;std::getline(in,line);std::array<TriangleCoordinates,2>tri;unsigned rows=0;
 while(std::getline(in,line)){std::replace(line.begin(),line.end(),',',' ');std::istringstream row(line);unsigned t,i;row>>t>>i;if(t>1||i>2)throw std::runtime_error("coordinate index");for(double&x:tri[t][i])row>>x;if(!row)throw std::runtime_error("coordinate input");++rows;}if(rows!=6)throw std::runtime_error("incomplete fixture");
 using Q=boost::multiprecision::cpp_bin_float_quad;using H=boost::multiprecision::cpp_bin_float_100;using R=boost::multiprecision::cpp_rational;
 if(R(.1)==R(1)/10||R(.5)!=R(1)/2)throw std::runtime_error("binary-double rational conversion assumption failed");
 auto sign=[](const auto&x){return x>0?1:x<0?-1:0;};
 Q low=preciseSquaredDistance<Q>(tri[0])-preciseSquaredDistance<Q>(tri[1]);H high=preciseSquaredDistance<H>(tri[0])-preciseSquaredDistance<H>(tri[1]);R exact=preciseSquaredDistance<R>(tri[0])-preciseSquaredDistance<R>(tri[1]);
 std::cout<<std::setprecision(110)<<"low_difference="<<low<<"\nhigh_difference="<<high<<"\nexact_difference="<<exact<<"\nexact_sign="<<sign(exact)<<"\nPASS exact rational geometry of recorded stored doubles;NOT continuous geometry or dynamics certificate\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
