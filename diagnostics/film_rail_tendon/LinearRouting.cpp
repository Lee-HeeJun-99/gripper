#include "../../models/film_rail_tendon/Kernel.h"
#include <Eigen/Dense>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <complex>
using namespace regrip_film_rail;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("exclusive output CSV");std::ifstream old(argv[1]);if(old)throw std::runtime_error("existing output");std::ofstream out(argv[1]);out<<std::setprecision(17)<<"root_second_order,offset_mm,material_x,skin_z,rail_z,min_stiffness_eigenvalue,relative_residual\n";
 for(bool second:{false,true})for(double offset:{.2,2.}){Assembly m;m.rootGuideSecondOrder=second;m.guideOffset=offset;unsigned n=3*m.size();auto rest=m.rest();std::vector<int>indices(n,-1);unsigned nf=0;
  for(unsigned part=0;part<3;++part)for(unsigned i=1;i<m.nx;++i)for(unsigned j=0;j<m.parts[part].ny;++j)for(unsigned d=0;d<3;++d)if(i!=1||d!=2)indices[3*m.id(part,i,j)+d]=nf++;
  auto mapped=[&](unsigned index){unsigned node=index/3,d=index%3;for(unsigned part=0;part<3;++part){auto p=m.parts[part];if(node>=p.offset+p.ny&&node<p.offset+2*p.ny&&d==2)return std::pair<int,double>{indices[index+3*p.ny],.25};}return std::pair<int,double>{indices[index],1};};
  Eigen::MatrixXd H=Eigen::MatrixXd::Zero(nf,nf),mass=Eigen::MatrixXd::Zero(nf,nf);auto nodalMass=m.masses();for(unsigned node=0;node<m.size();++node)for(unsigned d=0;d<3;++d){auto [i,w]=mapped(3*node+d);if(i>=0)mass(i,i)+=w*w*nodalMass[node];}Eigen::VectorXd f=Eigen::VectorXd::Zero(nf);std::vector<Point>u(m.size());
  m.elements(u,0,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){auto [i,wi]=mapped(3*e.ids[a/3]+a%3);if(i<0)continue;for(unsigned b=0;b<3*e.ids.size();++b){auto [j,wj]=mapped(3*e.ids[b/3]+b%3);if(j>=0)H(i,j)+=wi*wj*e.energy.h[N*a+b];}}});
  m.elements(u,1e-6,[&](const Element&e){if(e.kind!=2)return;for(unsigned a=0;a<3*e.ids.size();++a){auto [i,w]=mapped(3*e.ids[a/3]+a%3);if(i>=0)f(i)-=w*e.energy.g[a];}});
  Eigen::VectorXd q=H.ldlt().solve(f);double residual=(H*q-f).norm()/f.norm();Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> eig(H);double smallest=eig.eigenvalues().minCoeff();
  if(!q.allFinite()||residual>1e-7||smallest<=0)throw std::runtime_error("linear fixture/system failure");
  Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd> modal(H,mass);Eigen::VectorXd amplitudes=modal.eigenvectors().transpose()*f;
  for(int k=0;k<amplitudes.size();++k){double w2=modal.eigenvalues()(k);using Complex=std::complex<double>;auto root=std::sqrt(Complex(1-w2)),r1=Complex(-1)+root,r2=Complex(-1)-root;auto A=(-1.-r2*(2/w2))/(r1-r2),B=2/w2-A;double response=std::real(Complex(.5-2/w2)+A*std::exp(r1*.5)+B*std::exp(r2*.5));amplitudes(k)*=response/w2;}Eigen::VectorXd dynamic=modal.eigenvectors()*amplitudes;
  auto z=[&](unsigned part,unsigned i,unsigned j){auto [index,w]=mapped(3*m.id(part,i,j)+2);return index<0?0:w*q(index);};
  for(unsigned i=0;i<m.nx;++i)out<<second<<','<<offset<<','<<100.*i/(m.nx-1)<<','<<z(0,i,2)<<','<<z(1,i,1)<<','<<smallest<<','<<residual<<'\n';
  std::cout<<"root="<<second<<" offset="<<offset<<" mid="<<z(0,10,2)<<" tip="<<z(0,20,2)<<" dynamic_mid="<<dynamic(indices[3*m.id(0,10,2)+2])<<" dynamic_tip="<<dynamic(indices[3*m.id(0,20,2)+2])<<" omega0="<<std::sqrt(modal.eigenvalues()(0))<<" minH="<<smallest<<" residual="<<residual<<'\n';
 }
 return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
