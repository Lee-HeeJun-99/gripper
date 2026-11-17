#include "../../models/film_coupled_contact/CoupledSphere.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_coupled;
// Frozen BILATERAL single-row diagnostic only. No nonlinear path certification.
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("actual event input/output required");std::ifstream in(argv[1]);
 unsigned nx,intervals,root,count,nt;double offset,bond,start,tau,c,r;in>>nx>>intervals>>offset>>bond>>root>>start>>tau>>c>>r;
 Body b;in>>b.mass>>b.inertia;for(double&x:b.center)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;for(double&x:b.force)in>>x;
 EventControl control;in>>control.maximum>>control.ramp>>control.release>>control.end>>control.c2>>count;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=root;
 if(count!=model.size())throw std::runtime_error("actual size mismatch");
 std::vector<double>mass(count);std::vector<Point>q0(count),v0(count),q(count),v(count),zero(count);for(double&x:mass)in>>x;
 for(auto*values:{&q0,&v0,&q,&v})for(auto&p:*values)for(double&x:p)in>>x;
 for(double&x:b.center)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;
 in>>nt;std::vector<std::array<unsigned,3>>tri(nt);for(auto&t:tri)for(unsigned&i:t)in>>i;
 // Appended actual POST-impact velocities;positions are unchanged by impulse.
 for(auto&p:v)for(double&x:p)in>>x;for(double&x:b.linear)in>>x;for(double&x:b.angular)in>>x;
 if(!in)throw std::runtime_error("incomplete actual post-impact input");
 CoupledPlaneStep film(model,mass,1,c,control.sample(start+tau).tension,q,v,zero,0);System s(film,tri,b,r);State state{q,v,b};
 unsigned id=0;double gap=std::numeric_limits<double>::infinity();for(unsigned i=0;i<nt;++i)if(s.primitive(state,i).gap.v<gap){gap=s.primitive(state,i).gap.v;id=i;}
 auto row=s.geometry(state,id);Eigen::VectorXd j=row.gradient.head(s.nf),vf=film.pack(v);double vn=row.gradient.dot(s.pack(state));
 if(std::abs(gap)>1e-10||std::abs(vn)>1e-9)throw std::runtime_error("actual post-impact row not tangent/touching");
 Eigen::MatrixXd K=Eigen::MatrixXd::Zero(s.nf,s.nf);Eigen::VectorXd F=Eigen::VectorXd::Zero(s.nf);
 model.elements(q,control.sample(start+tau).tension,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=film.index[ga];if(i<0)continue;F(i)-=film.weight[ga]*e.energy.g[a];for(unsigned z=0;z<3*e.ids.size();++z){unsigned gz=3*e.ids[z/3]+z%3;int k=film.index[gz];if(k>=0)K(i,k)+=film.weight[ga]*film.weight[gz]*e.energy.h[N*a+z];}}});
 Eigen::MatrixXd M=s.M.topLeftCorner(s.nf,s.nf),effective=M+b.mass*j*j.transpose();double fn=row.normal.dot(b.force);F+=j*fn;
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<s.nf<<' '<<c<<' '<<b.mass<<' '<<fn<<' '<<vn<<' '<<gap<<' '<<id<<'\n';
 for(const auto*A:{&effective,&K,&M}){for(int i=0;i<A->rows();++i){for(int k=0;k<A->cols();++k)out<<(*A)(i,k)<<' ';out<<'\n';}}
 for(const auto*a:{&j,&vf,&F}){for(int i=0;i<a->size();++i)out<<(*a)(i)<<' ';out<<'\n';}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
