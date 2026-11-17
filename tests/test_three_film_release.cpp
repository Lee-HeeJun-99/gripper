#include "../models/film_three_finger_event/AllRowRelease.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_event;
int main(){try{
 SharedFilmSystem s(Layout(),{0,0,.001},true,true);s.exactUnresolved=true;auto q=s.initial;Eigen::VectorXd v=Eigen::VectorXd::Zero(q.size());EventControl zero{0,.01,.02,.03,true};double h=.0001;auto released=allRowRelease(s,q,v,0,h,zero);unsigned body=3*s.shared.nf;
 if(released.state.q.head(body).norm()!=0||released.state.v.head(body).norm()!=0)throw std::runtime_error("stationary film reference should remain undeformed");double dz=released.state.q(body+2)-q(body+2),vz=released.state.v(body+2),expected=h*h/2*(.001/.0001)/(1+h);if(std::abs(dz-expected)>1e-14||std::abs(vz-2*expected/h)>1e-14)throw std::runtime_error("released shared body analytic midpoint reference");
 // For THIS flat undeformed reference every triangle belongs to its film
 // plane. The sphere moves monotonically away from all three planes,so
 // triangle distance >= plane distance over the WHOLE quadratic interval.
 double planeBound=1e100;for(unsigned f=0;f<3;++f){auto local=s.local(q,f);double g0=-local.body.center.z()-s.layout.bufferRadius,slope=-s.layout.mount[f].R(2,2);if(slope<=0)throw std::runtime_error("release plane direction not separating");planeBound=std::min(planeBound,g0);}
 if(planeBound< -1e-10||released.endpointGap<=0)throw std::runtime_error("whole flat-surface existing gap gate");bool rejected=false;try{SharedFilmSystem compressive(Layout(),{0,0,-.001},true,true);compressive.exactUnresolved=true;allRowRelease(compressive,q,v,0,h,zero);}catch(const std::domain_error&){rejected=true;}if(!rejected)throw std::runtime_error("compressive branch accepted as release");
 std::cout<<std::setprecision(17)<<"minimum_free_normal_acceleration="<<released.freeNormalAcceleration.minCoeff()<<" maximum_bilateral_reaction="<<released.bilateralReaction.maxCoeff()<<" endpoint_gap="<<released.endpointGap<<" whole_plane_bound="<<planeBound<<" momentum="<<released.state.momentumResidual<<'\n';std::cout<<"PASS all-row zero-impulse release,analytic free body and flat-surface path bound;NOT deformed release/re-impact/SOFA/tendon ungrasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
