#include "../../models/film_shell/PlaneContact.h"
#include <Eigen/Sparse>
#include <Eigen/SparseLU>
#include <Eigen/Eigenvalues>
#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
using namespace regrip_film;
// Independent full Newton backward Euler reference. Same energy/tangent,
// explicit root-slope fixture/fixed plane. This is NOT an actual SOFA run.
int main(int argc,char**argv){try{
 if(argc!=2)throw std::invalid_argument("actual journal path required");unsigned steps=200;
 Film f(21,5,100,24,{250,0,.06101941552425123});unsigned n=f.nx*f.ny,offset=3*f.ny,nd=3*n-offset;
 double dt=20./steps,mass=1e-6/n;Eigen::VectorXd u=Eigen::VectorXd::Zero(nd),v=u;
 auto evaluate=[&](const Eigen::VectorXd&q,Eigen::VectorXd&g,Eigen::SparseMatrix<double>&H){std::vector<Point>x(n);for(unsigned i=offset;i<3*n;++i)x[i/3][i%3]=q[i-offset];g=Eigen::VectorXd::Zero(nd);std::vector<Eigen::Triplet<double>>trip;double U=0;
  auto append=[&](const std::vector<unsigned>&ids,const AD&e,bool){U+=e.v;for(unsigned a=0;a<3*ids.size();++a){int row=int(3*ids[a/3]+a%3)-int(offset);if(row<0)continue;g[row]+=e.g[a];for(unsigned b=0;b<3*ids.size();++b){int col=int(3*ids[b/3]+b%3)-int(offset);if(col>=0&&e.h[N*a+b])trip.emplace_back(row,col,e.h[N*a+b]);}}};
  f.elements(x,append,true);
  for(unsigned j=0;j<f.ny;++j){std::vector<unsigned>ids{f.id(0,j),f.id(1,j),f.id(2,j)};AD slope;double c[3]={-3,4,-1};for(unsigned a=0;a<3;++a)slope=slope+AD(c[a]*(f.nx-1)/(2*f.L))*AD::variable(x[ids[a]][2],3*a+2);append(ids,AD(.5*100*f.W/(f.ny-1)*(j==0||j==f.ny-1?.5:1))*slope*slope,false);}
  for(unsigned i=0;i<f.nx-1;++i)for(unsigned j=0;j<f.ny-1;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{f.id(i+1,j+1),f.id(i,j+1),f.id(i+1,j)}:std::vector<unsigned>{f.id(i,j),f.id(i+1,j),f.id(i,j+1)};std::array<AD,3>gaps;for(int a=0;a<3;++a)gaps[a]=AD::variable(x[ids[a]][2]-.1,3*a+2);append(ids,planeContact(gaps,.5*f.L*f.W/((f.nx-1)*(f.ny-1)),1e-5).energy,false);}
  H.resize(nd,nd);H.setFromTriplets(trip.begin(),trip.end());return U;
 };

 std::ifstream input(argv[1]);if(!input)throw std::runtime_error("missing journal");std::string line,last;while(std::getline(input,line))if(line.find('"')!=std::string::npos)last=line;
 auto quote=last.find('"');if(quote==std::string::npos)throw std::runtime_error("missing actual coordinates");std::istringstream coords(last.substr(quote+1));auto rest=f.rest();
 for(unsigned i=0;i<3*n;++i){double value;if(!(coords>>value))throw std::runtime_error("truncated actual coordinates");if(i>=offset)u[i-offset]=value-rest[i/3][i%3];}
 Eigen::VectorXd g;Eigen::SparseMatrix<double> H;evaluate(u,g,H);Eigen::MatrixXd dense(H);Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> spectrum(dense/mass);
 if(spectrum.info()!=Eigen::Success)throw std::runtime_error("eigensolver");
 Eigen::MatrixXd transverse(nd/3,nd/3);for(unsigned i=0;i<nd/3;++i)for(unsigned j=0;j<nd/3;++j)transverse(i,j)=dense(3*i+2,3*j+2)/mass;
 Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd> z(transverse);
 std::cout<<std::setprecision(17)<<"{\"source\":\"Independent tangent spectrum at actual SOFA state; not an accuracy certificate\",\"minimum_eigenvalue\":"<<spectrum.eigenvalues()[0]<<",\"max_frequency_rad_s\":"<<std::sqrt(spectrum.eigenvalues().maxCoeff())<<",\"transverse_max_frequency_rad_s\":"<<std::sqrt(z.eigenvalues().maxCoeff())<<",\"transverse_omega_dt_0025\":"<<.0025*std::sqrt(z.eigenvalues().maxCoeff())<<"}\n";
 return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
