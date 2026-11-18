#include "../models/film_lateral_tendon/Route.h"
#include <Eigen/Geometry>
#include <iomanip>
#include <iostream>
using namespace regrip_lateral_tendon;
struct Result{double E=0;Eigen::VectorXd f;Eigen::MatrixXd H;};
Result evaluate(const Assembly&m,const std::vector<Point>&q,double lateral,bool original=false){unsigned n=3*m.size();Result out{0,Eigen::VectorXd::Zero(n),Eigen::MatrixXd::Zero(n,n)};auto visit=[&](const Element&e){out.E+=e.energy.v;for(unsigned a=0;a<3*e.ids.size();++a){unsigned i=3*e.ids[a/3]+a%3;out.f[i]-=e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b){unsigned j=3*e.ids[b/3]+b%3;out.H(i,j)+=e.energy.h[N*a+b];}}};if(original)m.elements(q,.001,visit);else elements(m,q,.001,lateral,visit);return out;}
int main(){try{
 Assembly m(21);m.guideOffset=5;m.guideIntervals=4;m.rootGuideSecondOrder=true;auto rest=m.rest();std::vector<Point>q(m.size());for(unsigned i=0;i<q.size();++i){auto x=rest[i];q[i]={.002*std::sin(.05*x[0]),.001*std::cos(.02*x[0]+.2*x[1]),.01*std::sin(.03*x[0])*std::cos(.04*x[1])};}double maxF=0,maxH=0,baseline=0,objective=0;
 Eigen::Matrix3d R=Eigen::AngleAxisd(.3,Eigen::Vector3d(.3,.4,.5).normalized()).toRotationMatrix();
 for(double lateral:{0.,6.}){auto e=evaluate(m,q,lateral);if(lateral==0){auto old=evaluate(m,q,0,true);baseline=std::max({std::abs(old.E-e.E),(old.f-e.f).cwiseAbs().maxCoeff(),(old.H-e.H).cwiseAbs().maxCoeff()});if(length(m,q,0)!=m.cableLength(q))throw std::runtime_error("zero-lateral baseline length parity failed");}
  for(unsigned j:{3*m.id(0,5,0)+2,3*m.id(1,5,0)+2,3*m.id(2,10,2)}){double h=1e-6;auto plus=q,minus=q;plus[j/3][j%3]+=h;minus[j/3][j%3]-=h;auto p=evaluate(m,plus,lateral),a=evaluate(m,minus,lateral);maxF=std::max(maxF,std::abs(-(p.E-a.E)/(2*h)-e.f[j]));for(unsigned i=0;i<e.f.size();++i)maxH=std::max(maxH,std::abs((p.f[i]-a.f[i])/(2*h)+e.H(i,j)));}
  auto rotated=q;for(unsigned i=0;i<q.size();++i){Eigen::Vector3d x(rest[i][0]+q[i][0],rest[i][1]+q[i][1],rest[i][2]+q[i][2]);x=R*x+Eigen::Vector3d(1,2,3);for(unsigned d=0;d<3;++d)rotated[i][d]=x[d]-rest[i][d];}auto r=evaluate(m,rotated,lateral);objective=std::max(objective,std::abs(r.E-e.E));Point total{},moment{};
  for(unsigned i=0;i<q.size();++i){Eigen::Vector3d f=e.f.segment<3>(3*i);objective=std::max(objective,(r.f.segment<3>(3*i)-R*f).cwiseAbs().maxCoeff());for(unsigned j=0;j<q.size();++j)objective=std::max(objective,(r.H.block<3,3>(3*i,3*j)-R*e.H.block<3,3>(3*i,3*j)*R.transpose()).cwiseAbs().maxCoeff());Point fp{f[0],f[1],f[2]};total=add(total,fp);moment=add(moment,cross(add(rest[i],q[i]),fp));}
  if(std::sqrt(dot(total,total))>1e-10||std::sqrt(dot(moment,moment))>1e-9)throw std::runtime_error("full nodal force/moment balance failed");
 }
 if(maxF>1e-8||maxH>1e-5||baseline>1e-12||objective>1e-8)throw std::runtime_error("existing FD/objectivity/baseline gates failed");
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"force_FD_N\":"<<maxF<<",\"Hessian_FD_N_mm\":"<<maxH<<",\"baseline_F_H_E_max_abs\":"<<baseline<<",\"rigid_objectivity_F_H_E_max_abs\":"<<objective<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
