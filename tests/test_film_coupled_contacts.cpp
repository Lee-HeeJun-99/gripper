#include "../models/film_native_contact/CoupledBDFHistory.h"
#include <iostream>
using namespace regrip_film_native;
int main(){try{Assembly m(5);std::vector<Point>q(m.size()),v(m.size()),J(m.size());J[m.id(0,4,2)][2]=1;v[m.id(0,4,2)][2]=-1;std::vector<Point>initial(m.size());CoupledPlaneStep single(m,m.masses(),.005,2,.0001,q,v,J,0);auto reference=single.solve(initial,0);
 for(bool duplicate:{false,true}){std::vector<CoupledContactStep::Plane>p{{J,0,0,0}};if(duplicate)p.push_back({J,0,0,1});CoupledContactStep solver(m,m.masses(),.005,2,.0001,q,v,p);auto result=solver.solve(initial);double error=0;for(unsigned i=0;i<m.size();++i)for(unsigned d=0;d<3;++d)error=std::max(error,std::abs(reference.velocity[i][d]-result.velocity[i][d]));if(error>1e-7||result.residual>1e-12||result.lambda.minCoeff()<0||result.gap>1e-10)throw std::runtime_error("single/duplicate constraint equivalence");}
 for(double epsilon:{0.,1e-10}){Eigen::MatrixXd W(2,2);W<<1,1-epsilon,1-epsilon,1;Eigen::VectorXd d(2),warm(2);d<<-1,-1.000001;warm<<.5,.5;auto solved=CoupledContactStep::dual(W,d,warm);if(CoupledContactStep::gapError(d+W*solved,solved)>1e-10||solved.minCoeff()<0||solved(0)!=0)throw std::runtime_error("near-duplicate unequal planes active set");}
 // Verify the BDF2 position identity and physical momentum directly, including
 // the no-contact path. qold=qnow-h*v is a prescribed previous history, not
 // a claim that this synthetic history is an integrated trajectory.
 auto old=q;for(unsigned i=0;i<m.size();++i)for(unsigned d=0;d<3;++d)old[i][d]-=.005*v[i][d];
 auto qstar=CoupledBDFHistory::extrapolate(q,old),vstar=CoupledBDFHistory::extrapolate(v,v);
 double h=.005,beta=CoupledBDFHistory::beta;
 CoupledContactStep bdf(m,m.masses(),beta*h,2,.0001,qstar,vstar,{});auto b=bdf.solve(initial);
 double positionError=0;for(unsigned i=0;i<m.size();++i)for(unsigned d=0;d<3;++d)positionError=std::max(positionError,std::abs((3*b.displacement[i][d]-4*q[i][d]+old[i][d])/(2*h)-b.velocity[i][d]));
 if(positionError>1e-12||b.residual>1e-12||b.lambda.size()!=0)throw std::runtime_error("BDF2/no-contact kinematics or momentum");
 v[m.id(0,4,2)][2]=1;CoupledContactStep release(m,m.masses(),.005,2,.0001,q,v,{{J,0,0,0}});auto released=release.solve(initial);if(released.lambda.norm()!=0||released.gap>1e-10)throw std::runtime_error("unloading complementarity");std::cout<<"PASS unilateral single/duplicate-row and release reference;no regularization;not general SOFA qualification\n";return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
