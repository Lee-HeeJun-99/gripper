#pragma once
#include <chrono>
#include <fstream>
#include <iomanip>
#include <map>
#include <stdexcept>
#include <string>
namespace regrip_film {
// Opt-in observational instrumentation. Inclusive timings are nested, not additive.
// Explicit cache insertion counts are NOT process-wide heap allocation counts.
struct PassiveProfile {
 struct Metric {unsigned long long count=0;double seconds=0;};
 mutable std::map<std::string,Metric> metrics;
 std::ofstream output;
 bool enabled=false;
 void open(const std::string&path){if(path.empty())return;std::ifstream old(path);if(old)throw std::runtime_error("cost profile already exists");output.open(path);if(!output)throw std::runtime_error("cannot create cost profile");enabled=true;}
 void count(const char*name,unsigned long long n=1)const{if(enabled)metrics[name].count+=n;}
 struct Scope {
  const PassiveProfile&owner;const char*name;std::chrono::steady_clock::time_point start;
  Scope(const PassiveProfile&p,const char*n):owner(p),name(n){if(owner.enabled){start=std::chrono::steady_clock::now();owner.count(name);}}
  ~Scope(){if(owner.enabled)owner.metrics[name].seconds+=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();}
 };
 ~PassiveProfile(){if(output){output<<"metric,count,inclusive_seconds\n"<<std::setprecision(17);for(const auto&entry:metrics)output<<entry.first<<','<<entry.second.count<<','<<entry.second.seconds<<'\n';output<<"process_heap_allocation_events,NOT_MEASURED,NOT_MEASURED\n";}}
};
}
