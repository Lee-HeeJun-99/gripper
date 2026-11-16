#include "../../models/film_shell/PlaneContact.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <iostream>
#include <numeric>
using namespace regrip_film;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("snapshot q/v CSV");std::ifstream in(argv[1]);if(!in)throw std::runtime_error("snapshot");std::string line;std::getline(in,line);std::vector<Point>q,velocity;
 while(std::getline(in,line)){for(auto&c:line)if(c==',')c=' ';std::istringstream row(line);Point p,v;if(!(row>>p[0]>>p[1]>>p[2]>>v[0]>>v[1]>>v[2]))throw std::runtime_error("snapshot row");q.push_back(p);velocity.push_back(v);}
 Film f(q.size()/5,5,100,24,{250,0,.0610194155});unsigned n=q.size(),nd=0;std::vector<int>index(3*n,-1);std::vector<double>w(3*n,1);
 for(unsigned i=15;i<3*n;++i)if(!(i<30&&i%3==2))index[i]=nd++;
 for(unsigned j=0;j<5;++j){index[3*(5+j)+2]=index[3*(10+j)+2];w[3*(5+j)+2]=.25;}
 Eigen::MatrixXd H=Eigen::MatrixXd::Zero(nd,nd),C=H;Eigen::VectorXd mass=Eigen::VectorXd::Zero(nd),v=mass;
 for(unsigned i=15;i<3*n;++i){mass[index[i]]+=1e-6/n*w[i]*w[i];if(w[i]==1)v[index[i]]=velocity[i/3][i%3];}
 auto append=[&](Eigen::MatrixXd&matrix,const std::vector<unsigned>&ids,const AD&e){for(unsigned a=0;a<3*ids.size();++a)for(unsigned b=0;b<3*ids.size();++b){unsigned i=3*ids[a/3]+a%3,j=3*ids[b/3]+b%3;if(index[i]>=0&&index[j]>=0)matrix(index[i],index[j])+=w[i]*w[j]*e.h[N*a+b];}};
 f.elements(q,[&](const auto&ids,const AD&e,bool){append(H,ids,e);},true);
 for(unsigned i=0;i<f.nx-1;++i)for(unsigned j=0;j<4;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{f.id(i+1,j+1),f.id(i,j+1),f.id(i+1,j)}:std::vector<unsigned>{f.id(i,j),f.id(i+1,j),f.id(i,j+1)};std::array<AD,3>gap;for(unsigned a=0;a<3;++a)gap[a]=AD::variable(q[ids[a]][2]-.1,3*a+2);append(C,ids,planeContact(gap,.5*f.L*f.W/((f.nx-1)*4),1e-5).energy);}
 Eigen::MatrixXd M=mass.asDiagonal();Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd>solver(H+C,M);if(solver.info()!=Eigen::Success)throw std::runtime_error("modal solve");
 auto values=solver.eigenvalues();auto basis=solver.eigenvectors();Eigen::VectorXd projection=basis.transpose()*M*v,energy=.5*projection.array().square().matrix();double K=.5*v.dot(M*v),sum=energy.sum();
 std::vector<unsigned>order(nd);std::iota(order.begin(),order.end(),0);std::sort(order.begin(),order.end(),[&](unsigned a,unsigned b){return energy[a]>energy[b];});
 std::cout<<std::setprecision(17)<<"{\"kinetic\":"<<K<<",\"modal_sum\":"<<sum<<",\"kinetic_decomposition_relative_error\":"<<(K?std::abs(sum-K)/K:0)<<",\"minimum_eigenvalue\":"<<values[0]<<",\"top_modes\":[";
 for(unsigned rank=0;rank<10;++rank){unsigned i=order[rank];double omega=values[i]>0?std::sqrt(values[i]):0,contact=basis.col(i).dot(C*basis.col(i));if(rank)std::cout<<',';std::cout<<"{\"omega\":"<<omega<<",\"kinetic_fraction\":"<<(K?energy[i]/K:0)<<",\"contact_tangent_fraction\":"<<(values[i]?contact/values[i]:0)<<'}';}
 std::cout<<"],\"underresolved_kinetic_fractions\":[";bool first=true;
 for(double dt:{.01,.005,.0025,.000625}){double coarse=0,very=0;for(unsigned i=0;i<nd;++i)if(values[i]>0){double scaled=std::sqrt(values[i])*dt;if(scaled>1)coarse+=energy[i];if(scaled>.1)very+=energy[i];}if(!first)std::cout<<',';first=false;std::cout<<"{\"dt\":"<<dt<<",\"omega_dt_over_1\":"<<(K?coarse/K:0)<<",\"omega_dt_over_point1\":"<<(K?very/K:0)<<'}';}
 std::cout<<"],\"scope\":\"Frozen coupled tangent and reconstructed actual BDF2 velocity;not nonlinear modal energy or time qualification\"}\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
