#include "../../models/film_shell/Kernel.h"
#include <Eigen/Sparse>
#include <Eigen/SparseLU>
#include <iostream>
#include <iomanip>
using namespace regrip_film;
int main(){try{std::cout<<std::setprecision(17)<<"nx,ny,clamp,tip,EB,relative,linear_residual\n";
 for(unsigned nx:{11u,21u,41u})for(unsigned ny:{3u,5u})for(unsigned kind:{0u,1u}){
 Film f(nx,ny,100,10,{250,0,.2});auto x=f.rest();unsigned n=nx*ny;Eigen::SparseMatrix<double>K(n,n);std::vector<Eigen::Triplet<double>>tr;
 f.elements(x,[&](const auto&ids,const AD&e,bool){for(unsigned i=0;i<ids.size();++i)for(unsigned j=0;j<ids.size();++j)if(e.h[N*(3*i+2)+3*j+2])tr.emplace_back(ids[i],ids[j],e.h[N*(3*i+2)+3*j+2]);});K.setFromTriplets(tr.begin(),tr.end());
 Eigen::SparseMatrix<double>B(n,(nx-2)*ny);tr.clear();for(unsigned i=2;i<nx;++i)for(unsigned j=0;j<ny;++j)tr.emplace_back(f.id(i,j),(i-2)*ny+j,1);if(kind==1)for(unsigned j=0;j<ny;++j)tr.emplace_back(f.id(1,j),j,.25);B.setFromTriplets(tr.begin(),tr.end());
 Eigen::SparseMatrix<double>A=B.transpose()*K*B;Eigen::VectorXd load=Eigen::VectorXd::Zero(n);for(unsigned j=0;j<ny;++j)load[f.id(nx-1,j)]=1e-7/ny;Eigen::VectorXd rhs=B.transpose()*load;
 Eigen::SparseLU<Eigen::SparseMatrix<double>>solver;solver.compute(A);if(solver.info()!=Eigen::Success)throw std::runtime_error("film linear factorization");Eigen::VectorXd q=solver.solve(rhs),z=B*q;double tip=0;for(unsigned j=0;j<ny;++j)tip+=z[f.id(nx-1,j)]/ny;double EB=1e-7*1e6/(3*250*10*.008/12);std::cout<<nx<<','<<ny<<','<<(kind?"one_sided_slope":"two_fixed_rows")<<','<<tip<<','<<EB<<','<<std::abs(tip-EB)/EB<<','<<(A*q-rhs).norm()/rhs.norm()<<'\n';
 }return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
