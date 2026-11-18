#include "../../models/film_lateral_tendon/Step.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitive.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace regrip_lateral_tendon;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("selected static q/output required");auto m=model();std::vector<Point>q(m.size()),zero(q.size());std::ifstream in(argv[1]);double T;in>>T;for(auto&p:q)for(double&x:p)in>>x;if(!in||T!=.00009375)throw std::runtime_error("explicit lower-load witness only");auto map=mechanics(m,q,zero,.0001,T,m.masses());auto e=parts(map,q,T,6.);Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd>spectrum(e.stiffness);if(spectrum.info()!=Eigen::Success)throw std::runtime_error("actual symmetric tangent spectrum failed");auto rest=m.rest();for(unsigned i=0;i<q.size();++i)rest[i]=add(rest[i],q[i]);regrip_three_finger::Layout layout;auto worldCenter=layout.bodyCenter+Eigen::Vector3d(0,0,.0001);Eigen::Vector3d localCenter=layout.mount[0].R.transpose()*(worldCenter-layout.mount[0].origin);Point center{localCenter[0],localCenter[1],localCenter[2]};double gap=1e99;
 for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<m.nx;++i)for(unsigned j=0;j+1<m.parts[part].ny;++j){unsigned a=m.id(part,i,j),b=m.id(part,i+1,j),c=m.id(part,i,j+1),d=m.id(part,i+1,j+1);for(auto tri:{std::array<unsigned,3>{a,b,c},std::array<unsigned,3>{b,d,c}}){auto geo=regrip_film_sphere::ClosestPrimitive::evaluate({rest[tri[0]],rest[tri[1]],rest[tri[2]]},center,layout.bufferRadius);gap=std::min(gap,geo.gap.v);}}
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"tension_N,force_residual_N,U_skin,U_rails,U_attachment,cable_length_mm,minimum_tangent_eigenvalue_N_mm,maximum_tangent_eigenvalue_N_mm,tangent_asymmetry_N_mm,virtual_sphere_buffer_gap_mm\n"<<T<<','<<e.force.norm()<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<e.cable<<','<<spectrum.eigenvalues().minCoeff()<<','<<spectrum.eigenvalues().maxCoeff()<<','<<(e.stiffness-e.stiffness.transpose()).cwiseAbs().maxCoeff()<<','<<gap<<'\n';std::cout<<"COMPLETED independent selected lower-load force/spectrum/virtual overlay;NOT full static continuation or actual SOFA/contact/stability certificate\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
