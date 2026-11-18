#pragma once
#include <istream>
#include <array>
#include <vector>
namespace regrip_lateral_release {
using AuditEdges=std::vector<std::array<unsigned,4>>;
template<class System> inline AuditEdges readFreeFooter(std::istream&in,const System&s,double time,double&begin,double&end){
 std::string label;unsigned count,active;in>>label>>active;
 if(label!="FREE_ACTIVE_COUNT"||active!=0)throw std::runtime_error("lateral FREE requires empty active set");
 in>>label>>count;if(label!="RELEASED_EDGE_GEOMETRY"||count!=3)throw std::runtime_error("lateral released geometry audit missing");
 AuditEdges edges;
 for(unsigned f=0;f<3;++f){std::array<unsigned,4>e;for(auto&x:e)in>>x;
  if(!in||e[0]!=f||e[1]>=s.shared.films[f].triangles.size()||e[2]==e[3])throw std::runtime_error("released edge identity invalid");
  const auto&tri=s.shared.films[f].triangles[e[1]];for(unsigned node:{e[2],e[3]})if(std::find(tri.begin(),tri.end(),node)==tri.end())throw std::runtime_error("released edge topology invalid");edges.push_back(e);
 }
 in>>label>>begin>>end;if(label!="RELEASE_INTERVAL"||!(begin>0&&begin<end&&end<=time))throw std::runtime_error("release interval invalid");
 in>>label;if(label!="EDGE_BIRTH_HISTORY_UNMEASURED")throw std::runtime_error("unknown history must stay explicit");
 double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time)throw std::runtime_error("exact accumulated clock required");
 return edges;
}
}
