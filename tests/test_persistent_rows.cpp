#include "../models/film_coupled_collocation/PersistentRows.h"
#include <iostream>
#include <iomanip>
using namespace regrip_collocation;
void require(bool value,const char*msg){if(!value)throw std::runtime_error(msg);}
int main(){try{
 const int n=4;Eigen::MatrixXd M=1e-6*Eigen::MatrixXd::Identity(n,n);M(0,1)=M(1,0)=2e-7;
 Eigen::VectorXd q=Eigen::VectorXd::Zero(n),v=q;v(2)=1;v(3)=-.5;
 auto linear=[](const Eigen::VectorXd&q){RowGeometry g;g.gap=q.head(2);g.J=Eigen::MatrixXd::Zero(2,4);g.J(0,0)=1;g.J(1,1)=1;g.H.assign(2,Eigen::MatrixXd::Zero(4,4));return g;};
 auto force=[](const Eigen::VectorXd&q,double){Eigen::VectorXd f(4);f<<-2e-6,-3e-6,-4e-4*q(2),-9e-4*q(3);Eigen::MatrixXd K=Eigen::MatrixXd::Zero(4,4);K(2,2)=4e-4;K(3,3)=9e-4;return Force{f,K};};
 double errors[3];unsigned grids[3]={4,8,16};double maxfd=0;
 for(int grid=0;grid<3;++grid){auto qq=q,vv=v;double h=.02/grids[grid];
  for(unsigned i=0;i<grids[grid];++i){auto step=persistentRows(M,0,qq,vv,i*h,h,force,linear,i==0);qq=step.q;vv=step.v;maxfd=std::max(maxfd,step.tangentError);require(step.initialForce.minCoeff()>0,"positive reaction");require(step.momentumResidual<=1e-17&&step.velocityResidual<=1e-10,"strict residual");}
  Eigen::VectorXd reference=q;reference(2)=std::sin(.4)/20;reference(3)=-.5*std::sin(.6)/30;errors[grid]=(qq-reference).norm();require(qq.head(2).norm()<1e-15,"no hidden gap drift");
 }
 require(errors[0]/errors[1]>14&&errors[1]/errors[2]>14,"fourth order two-row analytic test");
 // Coupled changing normals:two circles in disjoint coordinate planes.
 auto curved=[](const Eigen::VectorXd&q){RowGeometry g;g.gap.resize(2);g.J=Eigen::MatrixXd::Zero(2,4);g.H.assign(2,Eigen::MatrixXd::Zero(4,4));for(int r=0;r<2;++r){Eigen::Vector2d p=q.segment<2>(2*r);double d=p.norm();if(d==0)throw std::domain_error("undefined circle normal");Eigen::Vector2d normal=p/d;g.gap(r)=d-1;g.J.block<1,2>(r,2*r)=normal.transpose();g.H[r].block<2,2>(2*r,2*r)=(Eigen::Matrix2d::Identity()-normal*normal.transpose())/d;}return g;};
 auto inward=[](const Eigen::VectorXd&q,double){return Force{-1e-4*q,1e-4*Eigen::MatrixXd::Identity(4,4)};};
 Eigen::VectorXd cq(4),cv(4);cq<<1,0,1,0;cv<<0,.2,0,-.3;
 auto curvedStep=persistentRows(M,0,cq,cv,0,1e-4,inward,curved,true);maxfd=std::max(maxfd,curvedStep.tangentError);
 require(curvedStep.stages.back().geometry.gap.cwiseAbs().maxCoeff()<1e-10,"curved two-row endpoint");
 bool dependent=false,releasing=false,nonsymmetric=false;
 try{persistentRows(M,0,q,v,0,.001,force,[&](const Eigen::VectorXd&x){auto g=linear(x);g.gap(1)=g.gap(0);g.J.row(1)=g.J.row(0);return g;});}catch(const std::domain_error&){dependent=true;}
 try{persistentRows(M,0,q,v,0,.001,[](const Eigen::VectorXd&q,double){return Force{Eigen::VectorXd::Ones(q.size())*1e-6,Eigen::MatrixXd::Zero(q.size(),q.size())};},linear);}catch(const std::domain_error&){releasing=true;}
 try{auto bad=M;bad(0,1)+=1e-7;persistentRows(bad,0,q,v,0,.001,force,linear);}catch(const std::invalid_argument&){nonsymmetric=true;}
 require(dependent&&releasing&&nonsymmetric,"dependent/release/nonsymmetric guards");
 std::cout<<std::setprecision(17)<<"PASS two-row independent Lobatto;NOT SOFA/active-set/grasp\nanalytic_errors "<<errors[0]<<' '<<errors[1]<<' '<<errors[2]<<"\nmax_tangent_FD "<<maxfd<<"\ncurved_gap "<<curvedStep.stages.back().geometry.gap.cwiseAbs().maxCoeff()<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
