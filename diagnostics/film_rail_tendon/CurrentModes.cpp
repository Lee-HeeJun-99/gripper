#include "../../models/film_native_contact/CoupledPlaneStep.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace regrip_film_native;
// Instantaneous FULL stored/generator tangent,not a modal dynamics certificate.
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("current state input required");std::ifstream in(argv[1]);unsigned nx,guides;double offset,bond,tension;in>>nx>>guides>>offset>>bond>>tension;Assembly model(nx);model.guideIntervals=guides;model.guideOffset=offset;model.bondK=bond;std::vector<double>mass(model.size());for(auto&m:mass)in>>m;std::vector<Point>q(model.size()),error(model.size()),zero(model.size());auto rest=model.rest();for(unsigned i=0;i<model.size();++i)for(unsigned d=0;d<3;++d){in>>q[i][d];q[i][d]-=rest[i][d];}for(auto&p:error)for(auto&v:p)in>>v;if(!in)throw std::runtime_error("incomplete modal snapshot");
 CoupledPlaneStep mechanics(model,mass,1,0,tension,q,zero,zero,0);auto n=mechanics.freeSize;Eigen::MatrixXd M=Eigen::MatrixXd::Zero(n,n),B=M;for(unsigned a=0;a<3*model.size();++a)if(mechanics.index[a]>=0)M(mechanics.index[a],mechanics.index[a])+=mass[a/3]*mechanics.weight[a]*mechanics.weight[a];
 model.elements(q,tension,[&](const Element&e){if(e.kind!=1)return;for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b){unsigned ga=3*e.ids[a/3]+a%3,gb=3*e.ids[b/3]+b%3;int i=mechanics.index[ga],j=mechanics.index[gb];if(i>=0&&j>=0)B(i,j)+=mechanics.weight[ga]*mechanics.weight[gb]*e.energy.h[N*a+b];}});
 auto e=mechanics.evaluate(Eigen::VectorXd::Zero(n));Eigen::MatrixXd K=e.tangent-M;Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd>solver(K,M);if(solver.info()!=Eigen::Success)throw std::runtime_error("modal eigensolve");auto coordinates=mechanics.pack(error);Eigen::VectorXd amplitudes=solver.eigenvectors().transpose()*M*coordinates;
 std::cout<<std::setprecision(17)<<"mode,eigenvalue,omega_rad_s,quadratic_error_projection,attachment_quadratic_share\n";for(unsigned i=0;i<n;++i){double l=solver.eigenvalues()(i),b=solver.eigenvectors().col(i).dot(B*solver.eigenvectors().col(i));std::cout<<i<<','<<l<<','<<(l>0?std::sqrt(l):0)<<','<<.5*l*amplitudes(i)*amplitudes(i)<<','<<(l!=0?b/l:0)<<'\n';}return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
