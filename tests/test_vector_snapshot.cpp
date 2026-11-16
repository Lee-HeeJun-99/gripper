#include "../models/yield_front_history/VectorField.h"
#include "../models/yield_front_history/AdaptiveSnapshot.h"
#include "../models/yield_front_history/ExactInterval.h"
#include <iomanip>
#include <iostream>
#include <memory>
using namespace regrip_vector_history;
int main(){try{
 constexpr R k=.001L,C=3e-6L,a=.3192L;VectorField exact(a,k);
 for(int i=0;i<24;++i){Step s;s.capacity=C;s.increment={V{.0012L*std::cos(.9L*i),.0009L*std::sin(.7L*i),0},V{.0001L,-.00013L,0},V{.00003L,.00002L,0}};auto t=exact.evaluate(s,1e-6L,1e-25L);exact.commit(t);}
 std::vector<V>probes{{1e-8L,0,0},{0,1e-8L,0},{-1e-8L,0,0},{0,-1e-8L,0},{1e-5L,-2e-5L,0}};
 std::cout<<std::setprecision(18);
 for(R stateTolerance:{1e-5L,1e-7L,1e-9L}){
  AdaptiveSnapshot snapshot([&](R x){return exact.elasticAt(x);},k,C,stateTolerance,probes,stateTolerance*C*1e-3L);
  R Uexact=0,Ufit=0,maxState=0;std::vector<R>Dexact(probes.size()),Dfit(probes.size());
  // Independent dense WITHHELD material points,not the builder's points.
  constexpr unsigned n=131072;
  for(unsigned j=0;j<n;++j){R x=-1+2*(R(j)+.5L)/n,w=2*a/n;V old=exact.elasticAt(x),fit=snapshot.at(x);
   Uexact+=w*.5L*k*dot(old,old);Ufit+=w*.5L*k*dot(fit,fit);maxState=std::max(maxState,norm(add(old,scale(fit,-1))));
   for(unsigned p=0;p<probes.size();++p){Dexact[p]+=w*radialReturn(old,probes[p],{0,0,1},k,C*(1-x*x)).loss;Dfit[p]+=w*radialReturn(fit,probes[p],{0,0,1},k,C*(1-x*x)).loss;}
  }
  R worst=0;for(unsigned p=0;p<probes.size();++p){R error=Dexact[p]?std::abs(Dfit[p]-Dexact[p])/Dexact[p]:(Dfit[p]==0?0:INFINITY);worst=std::max(worst,error);std::cout<<"SNAPSHOT_PROBE "<<stateTolerance<<' '<<p<<' '<<Dexact[p]<<' '<<Dfit[p]<<' '<<error<<'\n';}
  std::cout<<"SNAPSHOT {\"state_tolerance\":"<<stateTolerance<<",\"cells\":"<<snapshot.cells.size()<<",\"source_queries\":"<<snapshot.sourceQueries<<",\"max_withheld_state_error\":"<<maxState<<",\"representation_energy_change\":"<<Ufit-Uexact<<",\"worst_probe_loss_relative\":"<<worst<<",\"loss_gate\":\""<<(worst<.01L?"PASS":"FAIL")<<"\"}\n";
  // Coarse failures are outcomes,not removed. The final candidate must meet
  // the unchanged1%prospective-loss gate on this independent reference.
  if(stateTolerance==1e-9L&&!(worst<.01L))throw std::runtime_error("fine adaptive snapshot fails independent loss gate");
  if(stateTolerance==1e-9L&&maxState>stateTolerance)throw std::runtime_error("fine snapshot fails independent withheld state tolerance");
  if(stateTolerance==1e-9L){
   auto saved=std::make_shared<const AdaptiveSnapshot>(snapshot);
   for(unsigned p=0;p<probes.size();++p){Step step;step.capacity=C;step.increment[0]=probes[p];
    auto integrationKnots=saved->yieldKnots(probes[p]);
    VectorField compressed(a,k,{0,0,1},[saved](R x){return VectorField::MaterialValue{saved->at(x),saved->onYield(x)};},C,saved->lipschitzBound(),integrationKnots,[saved](R lo,R hi){return saved->localBound(lo,hi);},[saved](const Step&s,R lo,R hi){if(s.capacity!=saved->C||s.increment[1]!=V{}||s.increment[2]!=V{})return -1.L;return certifiedStickDensityError(*saved,s.increment[0],lo,hi);});
    VectorField referenceSeed(a,k,{0,0,1},[&](R x){return exact.materialAt(x);},C,exact.lipschitzUpperBound(),integrationKnots);
    std::cout<<"PROBE_BEGIN "<<p<<" knots="<<integrationKnots.size()<<std::endl;
    auto reference=referenceSeed.evaluate(step,1e-7L,1e-35L);
    std::cout<<"REFERENCE_LOSS "<<p<<' '<<reference.integral.v[2]<<" evaluations="<<reference.integral.evaluations<<std::endl;
    auto candidate=compressed.evaluate(step,1e-7L,1e-35L);
    R truth=reference.integral.v[2],fit=candidate.integral.v[2];R error=truth?std::abs(fit-truth)/truth:(fit==0?0:INFINITY);
    std::cout<<"ADAPTIVE_PROBE "<<p<<' '<<truth<<' '<<fit<<' '<<error<<" dense_reference="<<Dexact[p]<<'\n';
    if(!(error<.01L))throw std::runtime_error("snapshot fails adaptive reference: dense zero is not permission to discard new loss");
   }
  }
 }
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
