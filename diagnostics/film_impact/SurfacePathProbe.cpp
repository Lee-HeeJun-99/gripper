#include "../../models/film_impact/WholeSurfaceMidpoint.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_film_impact;using namespace regrip_film_native;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::invalid_argument("input and CSV output required");std::ifstream in(argv[1]);
 unsigned nx,intervals,rootGuide,count,nt;double offset,bond,h,damping,time,radius;EventControl control;Point center;
 in>>nx>>intervals>>offset>>bond>>rootGuide>>h>>damping>>time>>control.maximum>>control.ramp>>control.release>>control.end>>radius;
 for(auto&x:center)in>>x;in>>count>>nt;
 Assembly model(nx);model.guideIntervals=intervals;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=rootGuide;
 if(count!=model.size())throw std::runtime_error("probe geometry dimension");std::vector<double>mass(count);std::vector<Point>q(count),v(count);
 for(auto&x:mass)in>>x;for(auto&p:q)for(auto&x:p)in>>x;for(auto&p:v)for(auto&x:p)in>>x;
 std::vector<std::array<unsigned,3>>triangles(nt);for(auto&t:triangles)for(auto&i:t)in>>i;if(!in)throw std::runtime_error("probe incomplete input");
 CoupledContactStep midpoint(model,mass,h/2,damping,control.sample(time+h/2).tension,q,v,{},true,true);auto mid=midpoint.solve(v);
 QuadraticSurfacePath path{model.rest(),std::vector<Point>(count),std::vector<Point>(count)};
 for(unsigned i=0;i<count;++i)for(unsigned d=0;d<3;++d){path.a0[i][d]+=q[i][d];path.a1[i][d]=h*v[i][d];path.a2[i][d]=h*(mid.velocity[i][d]-v[i][d]);}
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"fraction,time,minimum_gap,triangle,rate,global_speed_bound,local_speed_bound\n";
 for(unsigned k=0;k<=128;++k){double a=k/128.,gap=std::numeric_limits<double>::infinity(),rate=0;unsigned id=0;auto x=path.position(a),velocity=path.derivative(a);
  for(unsigned j=0;j<nt;++j){auto t=triangles[j];std::vector<Point>p;for(unsigned i:t)p.push_back(x[i]);auto e=regrip_film_sphere::ClosestPrimitive::evaluate(p,center,radius);
   if(e.gap.v<gap){gap=e.gap.v;id=j;rate=0;for(unsigned z=0;z<9;++z)rate+=e.gap.g[z]*velocity[t[z/3]][z%3];}
  }
  double local=0;for(unsigned i:triangles[id])for(double b:{a,1.}){Point d;for(unsigned z=0;z<3;++z)d[z]=path.a1[i][z]+2*b*path.a2[i][z];local=std::max(local,std::sqrt(dot(d,d)));}
  out<<a<<','<<time+h*a<<','<<gap<<','<<id<<','<<rate<<','<<path.speedBound()<<','<<local<<'\n';
 }
 std::cout<<"Diagnostic sampled numerical path only;NOT CCD proof or convergence PASS\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
