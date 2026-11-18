#include "../models/film_stationary_release/FreeFooter.h"
#include <sstream>
#include <iomanip>
#include <iostream>
int main(){
 using namespace regrip_stationary_release;const double begin=.026799999999999949,end=begin+.0002,time=end+.0002;
 std::ostringstream text;text<<std::setprecision(17);writeFreeFooter(text,{begin,end,.022623148278007259},time);const std::string valid=text.str();
 std::istringstream in(valid);auto p=readFreeFooter(in,time);if(p.begin!=begin||p.end!=end||p.lastImpact!=.022623148278007259)throw std::runtime_error("exact provenance roundtrip differs");
 unsigned rejects=0;auto bad=[&](std::string from,std::string to){auto changed=valid;auto at=changed.find(from);if(at==std::string::npos)throw std::runtime_error("test anchor missing");changed.replace(at,from.size(),to);try{std::istringstream stream(changed);readFreeFooter(stream,time);}catch(const std::runtime_error&){++rejects;return;}throw std::runtime_error("invalid FREE provenance accepted");};
 bad("FREE_ACTIVE_COUNT 0","FREE_ACTIVE_COUNT 1");bad("RELEASED_FACE_GEOMETRY 3","RELEASED_FACE_GEOMETRY 2");bad("0 116 6","0 116 5");bad("STATIONARY_SEPARATED","INCOMING_BODY");bad("LAST_IMPACT_TIME 0.022623148278007259","LAST_IMPACT_TIME 0.03");bad("ACCUMULATED_TIME ","INVALID_CLOCK ");bad("RELEASE_INTERVAL ","INVALID_INTERVAL ");
 std::cout<<"PASS exact footer roundtrip;"<<rejects<<" malformed active/geometry/origin/history/time fixtures rejected\n";
}
