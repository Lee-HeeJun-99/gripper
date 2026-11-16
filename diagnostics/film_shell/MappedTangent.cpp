#include "../../models/film_shell/PlaneContact.h"
#include <Eigen/Dense>
#include <fstream>
#include <sstream>
#include <iostream>
#include <iomanip>
using namespace regrip_film;
std::vector<double>numbers(std::string line){for(auto&c:line)if(c==',')c=' ';std::istringstream in(line);std::vector<double>r;double v;while(in>>v)r.push_back(v);return r;}
int main(int argc,char**argv){try{
 if(argc!=2&&argc!=3)throw std::invalid_argument("actual tangent prefix [plane]");std::string prefix=argv[1],line;double plane=argc==3?std::stod(argv[2]):.1;
 std::ifstream state(prefix+".state.csv"),matrix(prefix+".matrix.csv");if(!state||!matrix)throw std::runtime_error("missing actual probe");
 std::getline(state,line);std::getline(state,line);auto factors=numbers(line);if(factors.size()!=4)throw std::runtime_error("coefficients");std::getline(state,line);
 std::vector<Point>q;while(std::getline(state,line)){auto p=numbers(line);if(p.size()!=3)throw std::runtime_error("state row");q.push_back({p[0],p[1],p[2]});}
 const unsigned ny=5,n=q.size(),nd=3*n;Film f(n/ny,ny,100,24,{250,0,.0610194155});
 Eigen::MatrixXd actual=Eigen::MatrixXd::Zero(nd,nd),expected=actual;
 std::getline(matrix,line);while(std::getline(matrix,line)){auto row=numbers(line);if(row.size()!=3)throw std::runtime_error("matrix row");actual(int(row[0]),int(row[1]))=row[2];}
 std::vector<unsigned>index(nd);std::vector<double>weights(nd,1);for(unsigned i=0;i<nd;++i)index[i]=i;
 for(unsigned j=0;j<ny;++j){q[ny+j][2]=.25*q[2*ny+j][2];index[3*(ny+j)+2]=3*(2*ny+j)+2;weights[3*(ny+j)+2]=.25;}
 auto append=[&](const std::vector<unsigned>&ids,const AD&e,bool){for(unsigned a=0;a<3*ids.size();++a)for(unsigned b=0;b<3*ids.size();++b){unsigned i=3*ids[a/3]+a%3,j=3*ids[b/3]+b%3;expected(index[i],index[j])+=-factors[3]*weights[i]*weights[j]*e.h[N*a+b];}};
 f.elements(q,append,true);
 for(unsigned i=0;i<f.nx-1;++i)for(unsigned j=0;j<f.ny-1;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{f.id(i+1,j+1),f.id(i,j+1),f.id(i+1,j)}:std::vector<unsigned>{f.id(i,j),f.id(i+1,j),f.id(i,j+1)};std::array<AD,3>gaps;for(int a=0;a<3;++a)gaps[a]=AD::variable(q[ids[a]][2]-plane,3*a+2);append(ids,planeContact(gaps,.5*f.L*f.W/((f.nx-1)*(f.ny-1)),1e-5).energy,false);}
 for(unsigned i=0;i<nd;++i)expected(index[i],index[i])+=factors[2]*1e-6/n*weights[i]*weights[i];
 auto fixed=[&](unsigned i){return i<3*ny||(i<6*ny&&i%3==2);};
 double error=0,norm=0,maxError=0;unsigned worstI=0,worstJ=0;
 for(unsigned i=0;i<nd;++i)for(unsigned j=0;j<nd;++j)if(!fixed(i)&&!fixed(j)){double d=actual(i,j)-expected(i,j);error+=d*d;norm+=expected(i,j)*expected(i,j);if(std::abs(d)>maxError){maxError=std::abs(d);worstI=i;worstJ=j;}}
 std::cout<<std::setprecision(17)<<"{\"relative_free_matrix_error\":"<<std::sqrt(error/norm)<<",\"maximum_absolute_error\":"<<maxError<<",\"worst_row\":"<<worstI<<",\"worst_col\":"<<worstJ<<",\"actual\":"<<actual(worstI,worstJ)<<",\"expected\":"<<expected(worstI,worstJ)<<",\"a2\":"<<factors[1]<<",\"scope\":\"independent mapped tangent versus actual public SOFA matrix; not dynamics qualification\"}\n";
 return std::sqrt(error/norm)<1e-10?0:2;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
