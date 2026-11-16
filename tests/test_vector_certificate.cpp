#include "../models/yield_front_history/VectorField.h"
#include "../models/yield_front_history/ExactInterval.h"
#include <iostream>
#include <memory>
using namespace regrip_vector_history;
int main(){try{
 if(bernsteinSign(QP{-1,0,1},Q(-1)/2,Q(1)/2)!=PolynomialSign::Nonpositive||bernsteinSign(QP{0},0,1)!=PolynomialSign::Zero)throw std::runtime_error("exact Bernstein regression");
 for(R x:{.1L,-.3L,0.L,1e-20L})if(binaryRational(x).convert_to<R>()!=x)throw std::runtime_error("binary rational roundtrip");
 constexpr R k=.001L,C=3e-6L,a=.3192L;VectorField exact(a,k);
 for(int i=0;i<24;++i){Step s;s.capacity=C;s.increment={V{.0012L*std::cos(.9L*i),.0009L*std::sin(.7L*i),0},V{.0001L,-.00013L,0},V{.00003L,.00002L,0}};auto t=exact.evaluate(s,1e-6L,1e-25L);exact.commit(t);}
 std::vector<V>probes{{1e-8L,0,0},{0,1e-8L,0},{-1e-8L,0,0},{0,-1e-8L,0},{1e-5L,-2e-5L,0}};
 AdaptiveSnapshot snapshot([&](R x){return exact.elasticAt(x);},k,C,1e-9L,probes,3e-18L);
 R lo=.963612886301514045L,hi=.963612886595943825L;auto cell=std::lower_bound(snapshot.cells.begin(),snapshot.cells.end(),lo,[](const auto&c,R p){return c.hi<p;});
 auto regime=certifyIdealCell(*cell,k,C,probes[0],lo,hi);
 auto snapshotPtr=std::make_shared<const AdaptiveSnapshot>(snapshot);IdealYieldState phases(snapshotPtr);auto partition=phases.tangentKnots(V{.2L,.1L,0});
 for(unsigned j=0;j<257;++j){R x=-1+2*(R(j)+.314159L)/257;if(phases.at(x)!=phases.uncachedAt(x))throw std::runtime_error("exact range cache differs from rational point predicate");}
 std::cout<<"EXACT_RANGE_CACHE points=257 knots="<<partition.size()<<'\n';
 std::cout<<"EXACT_CELL {\"classification\":"<<int(regime)<<",\"stick\":0,\"slip\":1,\"equality\":2,\"unknown\":3,\"scope\":\"exact finite-input ideal function;floating evaluator NOT certified\"}\n";
 if(regime==CellRegime::Unknown)return 1;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
