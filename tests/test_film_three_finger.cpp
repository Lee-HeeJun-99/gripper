#include "../models/film_three_finger/FrameLayout.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("explicit geometry output required");Layout layout;auto s=sharedPointReference(layout);auto impact=manyRowImpact(s.M,s.J,s.velocity,1e-10);if(impact.state.impulse.minCoeff()<0||impact.state.normalVelocity.minCoeff()< -1e-10||impact.state.momentumResidual>1e-14)throw std::runtime_error("3finger shared impulse conditions");
 Eigen::Vector3d total=Eigen::Vector3d::Zero(),moment=total;double wedge=0,minGap=1;std::ofstream geometry(argv[1]);geometry<<std::setprecision(17)<<"finger,node,x,y,z\n";
 for(unsigned f=0;f<3;++f){auto&film=s.films[f];auto before=film.film.expand(s.velocity.segment(f*s.nf,s.nf)),after=film.film.expand(impact.state.velocity.segment(f*s.nf,s.nf));auto rest=film.film.model.rest();minGap=std::min(minGap,film.clearance(film.before));
  for(unsigned i=0;i<rest.size();++i){auto point=layout.world(f,rest[i]);geometry<<f<<','<<i<<','<<point.x()<<','<<point.y()<<','<<point.z()<<'\n';Eigen::Vector3d dp=film.film.mass[i]*layout.mount[f].R*(vector(after[i])-vector(before[i]));total+=dp;moment+=point.cross(dp);
   double phi=2*std::acos(-1.)*f/3;Eigen::Vector2d radial(std::cos(phi),std::sin(phi)),tangent(-std::sin(phi),std::cos(phi));double r=point.head<2>().dot(radial),t=point.head<2>().dot(tangent);if(!(r>0))throw std::runtime_error("rest film crosses central axis");wedge=std::max(wedge,std::abs(std::atan2(t,r)));}
 }
 Eigen::Vector3d bodyP=.0001*(impact.state.velocity.segment<3>(3*s.nf)-s.velocity.segment<3>(3*s.nf));total+=bodyP;moment+=layout.bodyCenter.cross(bodyP)+(.4*.0001*30*30)*(impact.state.velocity.tail<3>()-s.velocity.tail<3>());
 if(total.norm()>1e-15||moment.norm()>1e-14||minGap< -1e-10||wedge>=std::acos(-1.)/3||bodyP.z()<=0||(impact.state.velocity.tail<3>()-s.velocity.tail<3>()).norm()!=0)throw std::runtime_error("shared action/reaction,moment,rest wedge or FREE spin");
 auto rotated=layout;Eigen::Matrix3d Q=Eigen::AngleAxisd(.7,Eigen::Vector3d(1,2,3).normalized()).toRotationMatrix();Eigen::Vector3d shift(13,-7,4);rotated.bodyCenter=Q*layout.bodyCenter+shift;for(auto&m:rotated.mount){m.origin=Q*m.origin+shift;m.rootCenter=Q*m.rootCenter+shift;m.R=Q*m.R;}
 auto other=sharedPointReference(rotated);other.velocity.tail<3>()=Q*s.velocity.tail<3>();auto objective=manyRowImpact(other.M,other.J,other.velocity,1e-10);
 double impulseError=(objective.state.impulse-impact.state.impulse).norm(),bodyError=(objective.state.velocity.segment<3>(3*s.nf)-Q*impact.state.velocity.segment<3>(3*s.nf)).norm();if(impulseError>1e-18||bodyError>1e-14||std::abs(objective.state.energyLoss-impact.state.energyLoss)>1e-18)throw std::runtime_error("shared impact rigid-motion objectivity");
 Layout small(50,8);double crossing=50/std::sin(small.angle);if(!(crossing>0&&crossing<100))throw std::runtime_error("small-object negative geometry control missing");auto cross0=small.world(0,{crossing,12,0});for(unsigned f=1;f<3;++f)if((small.world(f,{crossing,12,0})-cross0).norm()>1e-12)throw std::runtime_error("flat small-object mount crossing is not shared");
 std::ofstream dimensions(std::string(argv[1])+".layout.csv");dimensions<<std::setprecision(17)<<"palm_radius,body_radius,body_x,body_y,body_z,mount_angle,small_body_radius,small_crossing_material_x\n"<<layout.palmRadius<<','<<layout.bodyRadius<<','<<layout.bodyCenter.x()<<','<<layout.bodyCenter.y()<<','<<layout.bodyCenter.z()<<','<<layout.angle<<",8,"<<crossing<<'\n';
 std::cout<<std::setprecision(17)<<"PASS independent3film/ONE free sphere,DOFs "<<s.M.rows()<<" mount_angle "<<layout.angle<<" min_gap "<<minGap<<" rest_half_wedge "<<wedge<<" linear "<<total.norm()<<" angular "<<moment.norm()<<" objectivity_impulse "<<impulseError<<" body "<<bodyError<<" loss "<<impact.state.energyLoss<<" small_R8_flat_mount_crossing_x "<<crossing<<";prescribed vertex approach,NOT SOFA/tendon grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
