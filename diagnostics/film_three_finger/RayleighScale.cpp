#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_finger;
int main(){try{
 SharedFilmSystem s(Layout(),{0,0,0},true,true);s.exactUnresolved=true;auto q=s.initial;unsigned nf=s.shared.nf,body=3*nf;Eigen::VectorXd trial=Eigen::VectorXd::Zero(q.size());
 for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f].film;auto rest=film.model.rest();std::vector<Point>shape(rest.size());for(unsigned i=0;i<rest.size();++i)shape[i][2]=std::pow(rest[i][0]/100,2);trial.segment(f*nf,nf)=film.pack(shape);auto recovered=film.expand(trial.segment(f*nf,nf));for(unsigned i=0;i<shape.size();++i)for(unsigned d=0;d<3;++d)if(shape[i][d]!=recovered[i][d])throw std::runtime_error("quadratic trial violates actual root map");}
 auto geometry=s.geometry(q);Eigen::Matrix3d object=geometry.J.block<3,3>(0,body);Eigen::FullPivLU<Eigen::Matrix3d>factor(object);if(!factor.isInvertible())throw std::runtime_error("object normal block rank");trial.segment<3>(body)=factor.solve(-geometry.J*trial);double constraint=(geometry.J*trial).norm();auto force=s.force(q,0);double stiffness=trial.dot(force.negativeTangent*trial),mass=trial.dot(s.shared.M*trial),filmMass=trial.head(body).dot(s.shared.M.topLeftCorner(body,body)*trial.head(body));
 if(stiffness<=0||mass<=0||constraint>1e-12||force.value.norm()>1e-12)throw std::runtime_error("stress-free admissible Rayleigh trial gate");double omega=std::sqrt(stiffness/mass),period=2*std::acos(-1.)/omega;
 std::cout<<std::setprecision(17)<<"{\"trial_stiffness_N_mm\":"<<stiffness<<",\"trial_mass_Ns2_mm\":"<<mass<<",\"film_kinetic_fraction\":"<<filmMass/mass<<",\"rayleigh_omega_upper_rad_s\":"<<omega<<",\"conditional_lowest_undamped_period_lower_s\":"<<period<<",\"omega_times_10ms\":"<<omega*.01<<",\"contact_trial_residual\":"<<constraint<<",\"rest_force_norm_N\":"<<force.value.norm()<<",\"body_trial_z\":"<<trial(body+2)<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
