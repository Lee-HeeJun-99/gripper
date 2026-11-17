#include "../models/film_coupled_collocation/GapControlledRows.h"
#include <iostream>
using namespace regrip_collocation;
int main(){try{
 Eigen::MatrixXd M=Eigen::MatrixXd::Identity(2,2);Eigen::VectorXd q=Eigen::VectorXd::Zero(2),v(2);v<<1,0;
 auto force=[](const Eigen::VectorXd&,double){Force f{Eigen::VectorXd(2),Eigen::MatrixXd::Zero(2,2)};f.value<<0,-1;return f;};
 auto geometry=[](const Eigen::VectorXd&x){RowGeometry g{Eigen::VectorXd(1),Eigen::MatrixXd::Zero(1,2),{Eigen::MatrixXd::Zero(2,2)}};g.gap<<x(1);g.J(0,1)=1;return g;};
 auto plain=gapControlledRows(M,0,q,v,0,.01,force,geometry,[](const auto&x){return x(1);});
 if(plain.attempts!=1||plain.rejected||plain.accepted.size()!=1||std::abs(plain.q(0)-.01)>1e-15)throw std::runtime_error("no-reject plane trajectory");
 // Explicit MOCK predicate for controller branch testing,NOT a physical model:
 // reject ONLY the first coarse trial; all reintegrated halves must be retained.
 unsigned queries=0;auto mock=[&](const Eigen::VectorXd&){return ++queries==1?-2e-10:0.;};
 auto split=gapControlledRows(M,0,q,v,0,.01,force,geometry,mock);
 if(split.attempts!=3||split.rejected!=1||split.accepted.size()!=2||queries!=9||(split.q-plain.q).norm()>1e-15||(split.v-plain.v).norm()>1e-15)throw std::runtime_error("discard/reintegration transaction mismatch");
 bool budget=false;try{gapControlledRows(M,0,q,v,0,.01,force,geometry,[](const auto&){return -2e-10;},32,0);}catch(const std::runtime_error&){budget=true;}if(!budget)throw std::runtime_error("depth policy ignored");
 bool invalid=false;try{gapControlledRows(M,0,q,v,0,.01,force,geometry,[](const auto&){return std::numeric_limits<double>::quiet_NaN();});}catch(const std::domain_error&){invalid=true;}if(!invalid)throw std::runtime_error("nonfinite clearance hidden");
 std::cout<<"PASS plane/no-split,MOCK reject/reintegrate transaction,budget,nonfinite;NOT physical curved-contact/time-convergence certification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
