#include "../models/film_three_finger_event/BlockFree.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_event;
int main(){try{
 SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);system.exactUnresolved=true;auto q=system.initial;const unsigned n=q.size(),nf=system.shared.nf;Eigen::VectorXd v=Eigen::VectorXd::Zero(n);q(3*nf+2)+=.01;v(3*nf+2)=-1;v.tail<3>()=Eigen::Vector3d(.1,.2,.3);EventControl zero{0,.01,.02,.03,true};
 auto simple=freeMidpoint(system,q,v,0,.0001,zero,2,true);
 if(simple.momentumResidual>1e-17||system.clearance(simple.q)<=0)throw std::runtime_error("free/no-contact momentum/geometry");
 EventControl c2{.0001,.01,.02,.03,true};double h=.0001,eps=1e-7;auto at=freeMidpoint(system,q,v,.001,h,c2,2,true),plus=freeMidpoint(system,q,v,.001,h+eps,c2),minus=freeMidpoint(system,q,v,.001,h-eps,c2);Eigen::VectorXd Q=(plus.q-minus.q)/(2*eps),V=(plus.v-minus.v)/(2*eps);double qError=(Q-at.positionFamilyRate).norm()/Q.norm(),vError=(V-at.velocityFamilyRate).norm()/V.norm(),filmQ=(Q.head(3*nf)-at.positionFamilyRate.head(3*nf)).norm()/Q.head(3*nf).norm(),filmV=(V.head(3*nf)-at.velocityFamilyRate.head(3*nf)).norm()/V.head(3*nf).norm();
 std::cout<<std::setprecision(17)<<"Q_relative="<<qError<<" V_relative="<<vError<<" film_Q_relative="<<filmQ<<" film_V_relative="<<filmV<<" momentum="<<at.momentumResidual<<'\n';
 if(qError>1e-6||vError>1e-6||filmQ>1e-6||filmV>1e-6)throw std::runtime_error("free endpoint-family derivative FD failed1e-6");
 bool rejected=false;try{auto bad=system;bad.shared.M(0,0)*=2;freeMidpoint(bad,q,v,0,h,zero);}catch(const std::runtime_error&){rejected=true;}if(!rejected)throw std::runtime_error("unmatched shared mass accepted");
 std::cout<<"PASS reused three-film free blocks,ONE shared rigid midpoint,momentum,position,family derivative,explicit mass mismatch rejection;NOT impact/CCD/SOFA/grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
