#include "../../models/film_impact/FilmProjection.h"
#include "../../models/film_rail_tendon/ControlProfile.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_film_impact;using namespace regrip_film_native;
int main(int argc,char**argv){try{
 if(argc!=3&&argc!=4)throw std::invalid_argument("input,modal CSV,optional full-nodal Gram CSV required");std::ifstream input(argv[1]);
 unsigned nx,intervals,rootGuide,count;double offset,bond,h,time,T;
 input>>nx>>intervals>>offset>>bond>>rootGuide>>h>>time>>T>>count;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=rootGuide;
 if(count!=model.size())throw std::runtime_error("modal dimension");std::vector<double>mass(count);std::vector<Point>q(count),jump(count),zero(count);
 for(auto&x:mass)input>>x;for(auto&p:q)for(auto&x:p)input>>x;for(auto&p:jump)for(auto&x:p)input>>x;if(!input)throw std::runtime_error("incomplete modal input");
 std::string profile;if(input>>profile){double maximum,ramp,release,end;bool c2;input>>maximum>>ramp>>release>>end>>c2;if(profile!="PROFILE"||!input)throw std::runtime_error("invalid optional shared profile");T=regrip_film_rail::ControlProfile::evaluate(time,maximum,ramp,release,end,c2).tension;}
 CoupledPlaneStep map(model,mass,h,0,T,q,zero,zero,0);Eigen::MatrixXd M=filmMass(map),K=Eigen::MatrixXd::Zero(map.freeSize,map.freeSize);
 model.elements(q,T,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int ia=map.index[ga];if(ia<0)continue;for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int ib=map.index[gb];if(ib>=0)K(ia,ib)+=map.weight[ga]*map.weight[gb]*e.energy.h[N*a+b];}}});
 Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd>eigen(K,M);if(eigen.info()!=Eigen::Success)throw std::runtime_error("generalized eigensolve failed");
 Eigen::VectorXd dv=map.pack(jump),amplitude=eigen.eigenvectors().transpose()*M*dv;double sum=0;
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"mode,eigenvalue,omega,period,omega_dt,jump_metric_energy,signed_amplitude\n";
 for(int i=0;i<amplitude.size();++i){double lambda=eigen.eigenvalues()(i),energy=.5*amplitude(i)*amplitude(i);sum+=energy;out<<i<<','<<lambda<<',';
  if(lambda>0){double omega=std::sqrt(lambda);out<<omega<<','<<2*std::acos(-1.)/omega<<','<<omega*h;}else out<<"null,null,null";out<<','<<energy<<','<<amplitude(i)<<'\n';
 }
 if(argc==4){Eigen::MatrixXd full=Eigen::MatrixXd::Zero(3*count,map.freeSize);for(unsigned a=0;a<3*count;++a)if(map.index[a]>=0)full.row(a)=map.weight[a]*eigen.eigenvectors().row(map.index[a]);Eigen::MatrixXd gram=full.transpose()*full;std::ofstream target(argv[3]);target<<std::setprecision(17);for(int i=0;i<gram.rows();++i){for(int j=0;j<gram.cols();++j){if(j)target<<',';target<<gram(i,j);}target<<'\n';}if(!target)throw std::runtime_error("nodal Gram output failure");}
 double direct=.5*dv.dot(M*dv);if(!(direct>0)||std::abs(sum-direct)>1e-10*direct)throw std::runtime_error("modal jump-metric completeness identity");
 std::cout<<std::setprecision(17)<<"jump_metric "<<direct<<" modal_sum "<<sum<<" relative_residual "<<std::abs(sum-direct)/direct<<" minimum_eigenvalue "<<eigen.eigenvalues().minCoeff()<<" actual_shared_profile_tension "<<T<<'\n';
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
