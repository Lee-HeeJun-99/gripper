#include "../models/film_three_finger_resume/AccelerationRelease.h"
#include <iostream>
using namespace regrip_three_resume;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int main(){try{
 Eigen::Matrix3d W;W<<2,.2,.1,.2,3,.3,.1,.3,4;
 for(unsigned mask=0;mask<8;++mask){Eigen::Vector3d lambda=Eigen::Vector3d::Zero(),normal=Eigen::Vector3d::Zero();for(unsigned i=0;i<3;++i)if(mask&(1u<<i))lambda(i)=i+1;else normal(i)=i+1;Eigen::Vector3d free=normal-W*lambda;auto r=accelerationReaction(W,free);require((r.force-lambda).norm()<1e-13,"known coupled subset solution");require(r.force.minCoeff()>=0,"no tensile force");require(std::abs(r.force.dot(r.normal))<1e-13,"acceleration complementarity");Eigen::PermutationMatrix<3>P;P.indices()<<2,0,1;auto permuted=accelerationReaction(P*W*P.transpose(),P*free);require((permuted.force-P*r.force).norm()<1e-13,"row permutation invariance");}
 auto zero=accelerationReaction(W,Eigen::Vector3d::Zero());require(zero.force.norm()==0,"zero reaction not invented");bool singular=false,nonsymmetric=false;
 try{accelerationReaction(Eigen::Matrix3d::Zero(),Eigen::Vector3d::Ones());}catch(const std::domain_error&){singular=true;}
 try{Eigen::Matrix3d bad=W;bad(0,1)+=.1;accelerationReaction(bad,Eigen::Vector3d::Ones());}catch(const std::domain_error&){nonsymmetric=true;}
 require(singular&&nonsymmetric,"invalid compliance rejected");std::cout<<"PASS independent bounded3-row acceleration complementarity;NOT SOFA/grasp/time qualification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
