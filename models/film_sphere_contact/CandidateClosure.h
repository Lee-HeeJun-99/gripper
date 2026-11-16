#pragma once
#include "SphereStep.h"
#include <array>
#include <set>
namespace regrip_film_sphere {
// Endpoint closure only, not swept CCD. Native rows are copied and reindexed
// into a separate owner. No native J, W, dFree or multiplier is modified.
struct CandidateClosure {
 using Triangle=std::array<unsigned,3>;
 struct Result {
  CoupledContactStep::Result mechanical;
  std::vector<CoupledContactStep::Plane> rows;
  std::vector<int> triangle; // -1: copied predictor support, otherwise topology ID
  unsigned sweeps=0,added=0;
  double minimumGap=std::numeric_limits<double>::infinity();
 };
 static std::vector<unsigned> key(std::vector<unsigned> nodes){std::sort(nodes.begin(),nodes.end());return nodes;}
 static Result solve(const CoupledContactStep& original,Point center,double radius,
                     const std::vector<Triangle>& triangles,const std::vector<Point>& initial,
                     bool sqp,std::ostream* trace=nullptr,unsigned maxSweeps=8){
  if(triangles.empty()||maxSweeps==0)throw std::invalid_argument("nonempty surface and finite positive closure budget required");
  Result out;out.rows=original.planes;out.triangle.assign(out.rows.size(),-1);
  std::set<std::vector<unsigned>> owned;
  for(unsigned i=0;i<out.rows.size();++i){out.rows[i].row=i;owned.insert(key(out.rows[i].support));}
  auto guess=initial;const auto rest=original.mechanics.model.rest();
  unsigned evaluations=0,reuses=0,iterations=0;
  for(unsigned sweep=0;sweep<maxSweeps;++sweep){
   const auto& m=original.mechanics;
   CoupledContactStep step(m.model,m.mass,m.h,m.damping,m.T,m.previous,m.previousVelocity,out.rows,original.potentialMerit,original.reuseAcceptedEvaluation);
   SphereStep exact(step,center,radius,true);exact.sqpMerit=sqp;
   out.mechanical=exact.solve(guess,trace);++out.sweeps;
   evaluations+=out.mechanical.evaluations;reuses+=out.mechanical.acceptedReuses;iterations+=out.mechanical.iterations;
   for(unsigned i=0;i<out.rows.size();++i)out.rows[i].lambda=out.mechanical.lambda(i);
   out.minimumGap=std::numeric_limits<double>::infinity();unsigned added=0;
   for(unsigned id=0;id<triangles.size();++id){
    std::vector<Point> positions;std::vector<unsigned> support;
    for(unsigned node:triangles[id]){positions.push_back(add(rest.at(node),out.mechanical.displacement.at(node)));support.push_back(node);}
    auto e=ClosestPrimitive::evaluate(positions,center,radius);
    if(!std::isfinite(e.gap.v))throw std::runtime_error("nonfinite whole-triangle gap");
    out.minimumGap=std::min(out.minimumGap,e.gap.v);
    if(e.gap.v>=-1e-10)continue;
    if(!owned.insert(key(support)).second)throw std::runtime_error("already-owned whole triangle violates final gap gate");
    if(out.rows.size()>=256)throw std::runtime_error("candidate closure row budget256;not OS resource exhaustion");
    std::vector<Point> J(rest.size());
    for(unsigned a=0;a<9;++a)J[support[a/3]][a%3]=e.gap.g[a];
    out.rows.push_back({std::move(J),0,0,static_cast<unsigned>(out.rows.size()),std::move(support)});
    out.triangle.push_back(static_cast<int>(id));++added;++out.added;
   }
   if(trace)*trace<<"candidate_closure sweep "<<sweep<<" added "<<added<<" minimum_gap "<<out.minimumGap<<'\n';
   if(added==0){out.mechanical.evaluations=evaluations;out.mechanical.acceptedReuses=reuses;out.mechanical.iterations=iterations;return out;}
   guess=out.mechanical.velocity;
  }
  throw std::runtime_error("candidate closure sweep budget;accepted state NOT committed");
 }
};
}
