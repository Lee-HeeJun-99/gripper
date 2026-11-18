#include "../models/film_sphere_contact/ClosestPrimitive.h"
#include <Eigen/Geometry>
#include <iostream>
#include <iomanip>
using namespace regrip_film_sphere;
int main(){try{
 std::vector<Point>triangle={{0,0,0},{1,0,0},{0,1,0}};double fdError=0,translation=0,moment=0,objective=0;Eigen::Matrix3d R=Eigen::AngleAxisd(.37,Eigen::Vector3d(1,2,3).normalized()).toRotationMatrix();Eigen::Vector3d t(2,-3,5);
 for(double x:{-.1,-.0001,.0001,.1}){Point center={x,.25,1};auto e=ClosestPrimitive::evaluate(triangle,center,1);double expected=x>=0?0:std::sqrt(1+x*x)-1;if(std::abs(e.gap.v-expected)>1e-14||e.feature!=(x>=0?6:4))throw std::runtime_error("analytic face/edge distance/feature differs");Eigen::Vector3d sum=Eigen::Vector3d::Zero(),torque=sum;std::vector<Point>rotated;
  for(unsigned i=0;i<3;++i){Eigen::Vector3d p(triangle[i][0],triangle[i][1],triangle[i][2]),g(e.gap.g[3*i],e.gap.g[3*i+1],e.gap.g[3*i+2]);sum+=g;torque+=p.cross(g);Eigen::Vector3d rp=R*p+t;rotated.push_back({rp.x(),rp.y(),rp.z()});}Eigen::Vector3d c(center[0],center[1],center[2]),rc=R*c+t;auto er=ClosestPrimitive::evaluate(rotated,{rc.x(),rc.y(),rc.z()},1);torque-=c.cross(sum);moment=std::max(moment,torque.norm());objective=std::max(objective,std::abs(e.gap.v-er.gap.v));
  for(unsigned i=0;i<3;++i){Eigen::Vector3d g(e.gap.g[3*i],e.gap.g[3*i+1],e.gap.g[3*i+2]),gr(er.gap.g[3*i],er.gap.g[3*i+1],er.gap.g[3*i+2]);objective=std::max(objective,(R*g-gr).norm());}
  for(unsigned a=0;a<9;++a){auto plus=triangle,minus=triangle;double h=1e-6;plus[a/3][a%3]+=h;minus[a/3][a%3]-=h;auto ep=ClosestPrimitive::evaluate(plus,center,1),em=ClosestPrimitive::evaluate(minus,center,1);if(ep.feature!=e.feature||em.feature!=e.feature)throw std::runtime_error("one-sided FD crossed feature");for(unsigned b=0;b<9;++b)fdError=std::max(fdError,std::abs((ep.gap.g[b]-em.gap.g[b])/(2*h)-e.gap.h[regrip_film::N*b+a]));}
  // Independent body-coordinate FD checks the relative-coordinate pullback.
  for(unsigned d=0;d<3;++d){Point cp=center,cm=center;cp[d]+=1e-6;cm[d]-=1e-6;double fd=(ClosestPrimitive::evaluate(triangle,cp,1).gap.v-ClosestPrimitive::evaluate(triangle,cm,1).gap.v)/(2e-6);translation=std::max(translation,std::abs(fd+sum(d)));}
 }
 double continuity=0;for(double eps:{1e-3,1e-5,1e-7}){auto left=ClosestPrimitive::evaluate(triangle,{-eps,.25,1},1),right=ClosestPrimitive::evaluate(triangle,{eps,.25,1},1);double norm=0;for(unsigned i=0;i<9;++i)norm+=std::pow(left.gap.g[i]-right.gap.g[i],2);double error=std::sqrt(norm);if(error>4*eps)throw std::runtime_error("face/edge gap gradient not C1");continuity=error;}
 bool degenerate=false;try{ClosestPrimitive::evaluate({{0,0,0},{1,0,0},{2,0,0}},{0,.2,1},1);}catch(const std::runtime_error&){degenerate=true;}if(!degenerate||fdError>1e-8||translation>1e-8||moment>1e-12||objective>1e-12)throw std::runtime_error("feature derivative/objectivity/degenerate gate");std::cout<<std::setprecision(17)<<"PASS independent triangle face-edge C1 gap/gradient,one-sided Hessian FD/objectivity;NOT temporal transition/SOFA\nHessian_FD_abs "<<fdError<<"\naction_reaction_FD_abs "<<translation<<"\nrotation_objectivity "<<objective<<"\nradial_moment "<<moment<<"\nlast_C1_gradient_difference "<<continuity<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
