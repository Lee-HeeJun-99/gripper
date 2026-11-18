#include <algorithm>
#include <stdexcept>
#include <string>
#include <sstream>
#include <iostream>
#include "../models/film_lateral_release/FreeFooter.h"
struct Film {std::vector<std::array<unsigned,3>>triangles{{0,1,2}};};
struct System {struct Shared {std::array<Film,3>films;}shared;};
int main(){try{
 System s;const std::string prefix="FREE_ACTIVE_COUNT 0 RELEASED_EDGE_GEOMETRY 3 0 0 1 2 1 0 1 2 2 0 1 2 ";
 const std::string suffix="RELEASE_INTERVAL .027 .0272 EDGE_BIRTH_HISTORY_UNMEASURED ACCUMULATED_TIME .0276";
 std::istringstream good(prefix+suffix);double begin,end;auto edges=regrip_lateral_release::readFreeFooter(good,s,.0276,begin,end);
 if(edges.size()!=3||edges[2][0]!=2||begin!=.027||end!=.0272)throw std::runtime_error("valid footer changed");
 unsigned rejected=0;for(const auto&bad:std::vector<std::string>{
  "FREE_ACTIVE_COUNT 1 RELEASED_EDGE_GEOMETRY 3",prefix+"RELEASE_INTERVAL .0273 .0272 EDGE_BIRTH_HISTORY_UNMEASURED ACCUMULATED_TIME .0276",
  prefix+"RELEASE_INTERVAL .027 .0272 INVENTED_BIRTH .025 ACCUMULATED_TIME .0276",prefix+"RELEASE_INTERVAL .027 .0272 EDGE_BIRTH_HISTORY_UNMEASURED ACCUMULATED_TIME .0277",
  "FREE_ACTIVE_COUNT 0 RELEASED_EDGE_GEOMETRY 3 0 0 1 4 1 0 1 2 2 0 1 2 "+suffix,
  "FREE_ACTIVE_COUNT 0 RELEASED_EDGE_GEOMETRY 3 0 0 1 1 1 0 1 2 2 0 1 2 "+suffix}){
  bool failed=false;try{std::istringstream in(bad);regrip_lateral_release::readFreeFooter(in,s,.0276,begin,end);}catch(const std::runtime_error&){failed=true;}if(!failed)throw std::runtime_error("invalid footer accepted");++rejected;
 }
 std::cout<<"PASS exact footer; rejected "<<rejected<<" malformed active/topology/clock/history branches\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
