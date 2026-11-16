#include "../../models/film_shell/PlaneContact.h"
#include <Eigen/Sparse>
#include <Eigen/SparseLU>
#include <iostream>
#include <iomanip>
using namespace regrip_film;
// Independent fixed-step BDF2 with BDF1 startup and end-time load reference. Same energy/tangent,
// explicit root-slope fixture/fixed plane. This is NOT an actual SOFA run.
int main(int argc,char**argv){try{
 unsigned steps=argc>=2?std::stoul(argv[1]):100;if(steps<1||steps>1000)throw std::invalid_argument("steps");
 Film f(21,5,100,24,{250,0,.06101941552425123});unsigned n=f.nx*f.ny,offset=3*f.ny,nd=3*n-offset;
 double duration=argc>=3?std::stod(argv[2]):20,dt=duration/steps,mass=1e-6/n;Eigen::VectorXd u=Eigen::VectorXd::Zero(nd),v=u,historyU=u,historyV=v;
 auto evaluate=[&](const Eigen::VectorXd&q,Eigen::VectorXd&g,Eigen::SparseMatrix<double>&H){std::vector<Point>x(n);for(unsigned i=offset;i<3*n;++i)x[i/3][i%3]=q[i-offset];g=Eigen::VectorXd::Zero(nd);std::vector<Eigen::Triplet<double>>trip;double U=0;
  auto append=[&](const std::vector<unsigned>&ids,const AD&e,bool){U+=e.v;for(unsigned a=0;a<3*ids.size();++a){int row=int(3*ids[a/3]+a%3)-int(offset);if(row<0)continue;g[row]+=e.g[a];for(unsigned b=0;b<3*ids.size();++b){int col=int(3*ids[b/3]+b%3)-int(offset);if(col>=0&&e.h[N*a+b])trip.emplace_back(row,col,e.h[N*a+b]);}}};
  f.elements(x,append,true);
  for(unsigned j=0;j<f.ny;++j){std::vector<unsigned>ids{f.id(0,j),f.id(1,j),f.id(2,j)};AD slope;double c[3]={-3,4,-1};for(unsigned a=0;a<3;++a)slope=slope+AD(c[a]*(f.nx-1)/(2*f.L))*AD::variable(x[ids[a]][2],3*a+2);append(ids,AD(.5*100*f.W/(f.ny-1)*(j==0||j==f.ny-1?.5:1))*slope*slope,false);}
  for(unsigned i=0;i<f.nx-1;++i)for(unsigned j=0;j<f.ny-1;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{f.id(i+1,j+1),f.id(i,j+1),f.id(i+1,j)}:std::vector<unsigned>{f.id(i,j),f.id(i+1,j),f.id(i,j+1)};std::array<AD,3>gaps;for(int a=0;a<3;++a)gaps[a]=AD::variable(x[ids[a]][2]-.1,3*a+2);append(ids,planeContact(gaps,.5*f.L*f.W/((f.nx-1)*(f.ny-1)),1e-5).energy,false);}
  H.resize(nd,nd);H.setFromTriplets(trip.begin(),trip.end());return U;
 };
 std::cout<<std::setprecision(17)<<"time,tip_z,U,max_speed,dynamic_residual,static_residual,iterations\n";
 for(unsigned step=0;step<steps;++step){double force=1e-6*std::min(1.,(step+1)*dt/10);Eigen::VectorXd load=Eigen::VectorXd::Zero(nd);for(unsigned j=0;j<f.ny;++j)load[3*f.id(f.nx-1,j)+2-offset]=force/f.ny;
  auto previous=u,velocity=v;double a2=step?1.5:1,a1=step?-2:-1,a0=step?.5:0;Eigen::VectorXd q=(-a1*u-a0*historyU+dt*v)/a2,g,residual;Eigen::SparseMatrix<double>H;
  auto residualAt=[&](const Eigen::VectorXd&trial){evaluate(trial,g,H);Eigen::VectorXd trialV=(a2*trial+a1*previous+a0*historyU)/dt;return (g-load+mass/dt*(a2*trialV+a1*velocity+a0*historyV)+2*mass*trialV).eval();};
  unsigned iteration=0;for(;iteration<30;++iteration){residual=residualAt(q);if(residual.norm()<1e-12)break;
   for(unsigned i=0;i<nd;++i)H.coeffRef(i,i)+=mass*a2*a2/(dt*dt)+2*mass*a2/dt;
   Eigen::SparseLU<Eigen::SparseMatrix<double>>solver;solver.compute(H);if(solver.info()!=Eigen::Success)throw std::runtime_error("reference factorization");Eigen::VectorXd increment=solver.solve(-residual);double norm=residual.squaredNorm();bool accepted=false;
   for(unsigned cut=0;cut<14;++cut){Eigen::VectorXd candidate=q+std::ldexp(1.,-int(cut))*increment;auto r=residualAt(candidate);if(r.squaredNorm()<norm){q=candidate;accepted=true;break;}}
   if(!accepted)throw std::runtime_error("reference line search failure at step "+std::to_string(step));
  }
  if(iteration==30)throw std::runtime_error("reference Newton limit");residual=residualAt(q);u=q;v=(a2*u+a1*previous+a0*historyU)/dt;historyU=previous;historyV=velocity;double U=evaluate(u,g,H),tip=0,speed=0;for(unsigned j=0;j<f.ny;++j)tip+=u[3*f.id(f.nx-1,j)+2-offset]/f.ny;for(unsigned i=0;i<nd/3;++i)speed=std::max(speed,v.segment<3>(3*i).norm());std::cout<<(step+1)*dt<<','<<tip<<','<<U<<','<<speed<<','<<residual.norm()<<','<<(g-load).norm()<<','<<iteration<<'\n';
 }return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}

