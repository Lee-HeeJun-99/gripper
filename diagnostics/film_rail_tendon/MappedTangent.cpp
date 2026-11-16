#include "../../models/film_rail_tendon/Kernel.h"
#include <Eigen/Dense>
#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
using namespace regrip_film_rail;
std::vector<double>numbers(std::string s){for(auto&c:s)if(c==',')c=' ';std::istringstream in(s);std::vector<double>r;double v;while(in>>v)r.push_back(v);return r;}
int main(int argc,char**argv){try{
 if(argc!=3)throw std::invalid_argument("actual tangent prefix and frozen T_per_rail");std::string prefix=argv[1],line;double tension=std::stod(argv[2]);std::ifstream state(prefix+".state.csv"),matrix(prefix+".matrix.csv");if(!state||!matrix)throw std::runtime_error("probe files");std::getline(state,line);std::getline(state,line);auto factors=numbers(line);std::getline(state,line);std::vector<Point>q;while(std::getline(state,line)){auto v=numbers(line);if(v.size()!=3)throw std::runtime_error("state row");q.push_back({v[0],v[1],v[2]});}
 Assembly model(q.size()/11);unsigned n=q.size(),nd=3*n;Eigen::MatrixXd J=Eigen::MatrixXd::Identity(nd,nd),H=Eigen::MatrixXd::Zero(nd,nd),M=H,actual=H;
 for(const auto&p:model.parts)for(unsigned j=0;j<p.ny;++j){unsigned i=p.offset+p.ny+j;J(3*i+2,3*i+2)=0;J(3*i+2,3*(i+p.ny)+2)=.25;q[i][2]=.25*q[i+p.ny][2];}
 model.elements(q,tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b)H(3*e.ids[a/3]+a%3,3*e.ids[b/3]+b%3)+=e.energy.h[N*a+b];});auto mass=model.masses();for(unsigned i=0;i<nd;++i)M(i,i)=mass[i/3];
 Eigen::MatrixXd expected=J.transpose()*(factors.at(2)*M-factors.at(3)*H)*J;
 std::getline(matrix,line);while(std::getline(matrix,line)){auto v=numbers(line);if(v.size()!=3||v[0]>=nd||v[1]>=nd)throw std::runtime_error("unexpected actual matrix size");actual(int(v[0]),int(v[1]))=v[2];}
 auto fixed=[&](unsigned i){unsigned node=i/3;for(const auto&p:model.parts)if((node>=p.offset&&node<p.offset+p.ny)||(node>=p.offset+p.ny&&node<p.offset+2*p.ny&&i%3==2))return true;return false;};
 double error=0,norm=0,max=0;for(unsigned i=0;i<nd;++i)for(unsigned j=0;j<nd;++j)if(!fixed(i)&&!fixed(j)){double d=actual(i,j)-expected(i,j);error+=d*d;norm+=expected(i,j)*expected(i,j);max=std::max(max,std::abs(d));}
 std::cout<<std::setprecision(17)<<"{\"relative_free_matrix_error\":"<<std::sqrt(error/norm)<<",\"maximum_absolute_error\":"<<max<<",\"scope\":\"independent three-part J^T(M+H)J versus actual SDK public matrix\"}\n";return std::sqrt(error/norm)<1e-10?0:2;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
