#include "../../models/film_three_finger/FrameLayout.h"
#include <Eigen/Eigenvalues>
#include <complex>
#include <iostream>
#include <iomanip>
#include <map>
using namespace regrip_three_finger;
using C=std::complex<long double>;
C phi1(C z){if(std::abs(z)>=.5L)return (std::exp(z)-C(1))/z;C sum=1,term=1;for(unsigned k=1;k<200;++k){term*=z/(long double)(k+1);sum+=term;if(std::abs(term)<1e-22L*std::abs(sum))return sum;}throw std::runtime_error("exprel series budget");}
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("exclusive frozen output CSV");Layout layout;auto shared=sharedPointReference(layout);auto&s=shared.films[0];std::map<int,unsigned>z;for(unsigned i=0;i<s.film.index.size();++i)if(i%3==2&&s.film.index[i]>=0&&!z.count(s.film.index[i])){unsigned n=z.size();z[s.film.index[i]]=n;}unsigned n=z.size();Eigen::MatrixXd K=Eigen::MatrixXd::Zero(n,n),M=K;std::vector<Point>zero(s.film.model.size());
 s.film.model.elements(zero,0,[&](const Element&e){for(unsigned a=2;a<3*e.ids.size();a+=3){unsigned ga=3*e.ids[a/3]+2;int ia=s.film.index[ga];if(ia<0)continue;for(unsigned b=2;b<3*e.ids.size();b+=3){unsigned gb=3*e.ids[b/3]+2;int ib=s.film.index[gb];if(ib>=0)K(z.at(ia),z.at(ib))+=3*s.film.weight[ga]*s.film.weight[gb]*e.energy.h[N*a+b];}}});
 for(const auto&[full,i]:z)M(i,i)=3*s.M(full,full);Eigen::VectorXd j=Eigen::VectorXd::Zero(n);j(z.at(s.film.index[3*shared.node+2]))=1;double nz=-std::sin(layout.angle);M+=.0001/(nz*nz)*j*j.transpose();Eigen::VectorXd F=-.001/nz*j;Eigen::GeneralizedSelfAdjointEigenSolver<Eigen::MatrixXd>eigen(K,M);if(eigen.info()!=Eigen::Success||eigen.eigenvalues().minCoeff()<=0)throw std::runtime_error("frozen symmetric modal system not positive");auto amplitudes=(eigen.eigenvectors().transpose()*F).eval();std::ofstream out(argv[1]);out<<std::setprecision(17)<<"scheme,steps,U_skin,U_rails,U_attachment,contact_displacement,omega_min,omega_max\n";
 for(unsigned steps:{0u,4u,8u,16u,32u}){Eigen::VectorXd modal(n);long double T=1e-4L;
  for(unsigned mode=0;mode<n;++mode){long double w2=eigen.eigenvalues()(mode),f=amplitudes(mode);if(steps==0){C root=std::sqrt(C(1-w2)),r1=C(-1)+root,r2=C(-1)-root;modal(mode)=double(std::real(f*T*(phi1(r1*T)-phi1(r2*T))/(r1-r2)));}
   else{using V=Eigen::Matrix<long double,2,1>;using A2=Eigen::Matrix<long double,2,2>;using A4=Eigen::Matrix<long double,4,4>;using V4=Eigen::Matrix<long double,4,1>;A2 A;A<<0,1,-w2,-2;V b;b<<0,f;V state=V::Zero();long double h=T/steps,B[2][2]={{1.L/3,-1.L/24},{2.L/3,1.L/6}},known[2]={5.L/24,1.L/6};A4 matrix=A4::Zero();for(unsigned i=0;i<2;++i)for(unsigned k=0;k<2;++k)matrix.template block<2,2>(2*i,2*k)=(i==k?A2::Identity().eval():A2::Zero().eval())-h*B[i][k]*A;Eigen::FullPivLU<A4>lu(matrix);if(!lu.isInvertible())throw std::runtime_error("frozen Lobatto matrix singular");for(unsigned step=0;step<steps;++step){V4 rhs;for(unsigned i=0;i<2;++i)rhs.template segment<2>(2*i)=state+h*known[i]*(A*state+b)+h*(B[i][0]+B[i][1])*b;state=lu.solve(rhs).template tail<2>();}modal(mode)=double(state(0));}}
  Eigen::VectorXd reduced=eigen.eigenvectors()*modal,full=Eigen::VectorXd::Zero(s.nf);for(const auto&[original,index]:z)full(original)=reduced(index);auto q=s.film.expand(full);double skin=0,rails=0,attachment=0;s.film.model.elements(q,0,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)skin+=3*e.energy.v;else rails+=3*e.energy.v;}if(e.kind==1)attachment+=3*e.energy.v;});out<<(steps?"frozen_lobatto":"modal_reference")<<','<<steps<<','<<skin<<','<<rails<<','<<attachment<<','<<j.dot(reduced)<<','<<std::sqrt(eigen.eigenvalues().minCoeff())<<','<<std::sqrt(eigen.eigenvalues().maxCoeff())<<'\n';
 }
 std::cout<<"PASS frozen symmetric sector modal diagnostic;NOT actual nonlinear3finger certification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
