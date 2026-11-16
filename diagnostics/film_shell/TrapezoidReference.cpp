#include "../../models/film_shell/PlaneContact.h"
#include <Eigen/Sparse>
#include <Eigen/SparseLU>
#include <iostream>
#include <iomanip>
using namespace regrip_film;
// Independent exact-slope reduced-mass trapezoidal reference. Same energy/tangent,
// explicit root-slope fixture/fixed plane. This is NOT an actual SOFA run.
int main(int argc,char**argv){try{
 unsigned steps=argc>=2?std::stoul(argv[1]):100;if(steps<1||steps>1000)throw std::invalid_argument("steps");
 Film f(21,5,100,24,{250,0,.0610194155});unsigned n=f.nx*f.ny,offset=3*f.ny,nd=0;std::vector<int>index(3*n,-1);std::vector<double>weights(3*n,1);for(unsigned i=offset;i<3*n;++i)if(!(i<2*offset&&i%3==2))index[i]=nd++;for(unsigned j=0;j<f.ny;++j){unsigned i=3*f.id(1,j)+2;index[i]=index[3*f.id(2,j)+2];weights[i]=.25;}
 double duration=argc>=3?std::stod(argv[2]):20,dt=duration/steps,mass=1e-6/n;Eigen::VectorXd u=Eigen::VectorXd::Zero(nd),v=u,historyU=u,historyV=v;
 Eigen::VectorXd masses=Eigen::VectorXd::Zero(nd);for(unsigned i=offset;i<3*n;++i)masses[index[i]]+=mass*weights[i]*weights[i];Eigen::SparseMatrix<double>M(nd,nd);for(unsigned i=0;i<nd;++i)M.insert(i,i)=masses[i];
 auto evaluate=[&](const Eigen::VectorXd&q,Eigen::VectorXd&g,Eigen::SparseMatrix<double>&H){std::vector<Point>x(n);for(unsigned i=offset;i<3*n;++i)x[i/3][i%3]=weights[i]*q[index[i]];g=Eigen::VectorXd::Zero(nd);std::vector<Eigen::Triplet<double>>trip;double U=0;
  auto append=[&](const std::vector<unsigned>&ids,const AD&e,bool){U+=e.v;for(unsigned a=0;a<3*ids.size();++a){unsigned ar=3*ids[a/3]+a%3;int row=index[ar];if(row<0)continue;g[row]+=weights[ar]*e.g[a];for(unsigned b=0;b<3*ids.size();++b){unsigned bc=3*ids[b/3]+b%3;int col=index[bc];if(col>=0&&e.h[N*a+b])trip.emplace_back(row,col,weights[ar]*weights[bc]*e.h[N*a+b]);}}};
  f.elements(x,append,true);
  for(unsigned i=0;i<f.nx-1;++i)for(unsigned j=0;j<f.ny-1;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{f.id(i+1,j+1),f.id(i,j+1),f.id(i+1,j)}:std::vector<unsigned>{f.id(i,j),f.id(i+1,j),f.id(i,j+1)};std::array<AD,3>gaps;for(int a=0;a<3;++a)gaps[a]=AD::variable(x[ids[a]][2]-.1,3*a+2);append(ids,planeContact(gaps,.5*f.L*f.W/((f.nx-1)*(f.ny-1)),1e-5).energy,false);}
  H.resize(nd,nd);H.setFromTriplets(trip.begin(),trip.end());return U;
 };
 std::cout<<std::setprecision(17)<<"time,tip_z,U,max_speed,dynamic_residual,static_residual,iterations\n";
 for(unsigned step=0;step<steps;++step){double force=1e-6*std::min(1.,(step+1)*dt/10);Eigen::VectorXd load=Eigen::VectorXd::Zero(nd);for(unsigned j=0;j<f.ny;++j)load[index[3*f.id(f.nx-1,j)+2]]=force/f.ny;
  auto previous=u,velocity=v;Eigen::VectorXd oldG;Eigen::SparseMatrix<double>oldH;evaluate(previous,oldG,oldH);Eigen::VectorXd oldLoad=Eigen::VectorXd::Zero(nd);for(unsigned j=0;j<f.ny;++j)oldLoad[index[3*f.id(f.nx-1,j)+2]]=1e-6*std::min(1.,step*dt/10)/f.ny;Eigen::VectorXd oldForce=-oldG+oldLoad-2*M*velocity;Eigen::VectorXd q=u+dt*v,g,residual;Eigen::SparseMatrix<double>H;
  auto residualAt=[&](const Eigen::VectorXd&trial){evaluate(trial,g,H);Eigen::VectorXd trialV=2*(trial-previous)/dt-velocity;return (g-load+2*M*(trialV-velocity)/dt+2*M*trialV-oldForce).eval();};
  unsigned iteration=0;for(;iteration<30;++iteration){residual=residualAt(q);if(residual.norm()<1e-12)break;
   for(unsigned i=0;i<nd;++i)H.coeffRef(i,i)+=masses[i]*(4/(dt*dt)+4/dt);
   Eigen::SparseLU<Eigen::SparseMatrix<double>>solver;solver.compute(H);if(solver.info()!=Eigen::Success)throw std::runtime_error("reference factorization");Eigen::VectorXd increment=solver.solve(-residual);double norm=residual.squaredNorm();bool accepted=false;
   for(unsigned cut=0;cut<14;++cut){Eigen::VectorXd candidate=q+std::ldexp(1.,-int(cut))*increment;auto r=residualAt(candidate);if(r.squaredNorm()<norm){q=candidate;accepted=true;break;}}
   if(!accepted)throw std::runtime_error("reference line search failure at step "+std::to_string(step));
  }
  if(iteration==30)throw std::runtime_error("reference Newton limit");residual=residualAt(q);u=q;v=2*(u-previous)/dt-velocity;historyU=previous;historyV=velocity;double U=evaluate(u,g,H),tip=0,speed=0;for(unsigned j=0;j<f.ny;++j)tip+=u[index[3*f.id(f.nx-1,j)+2]]/f.ny;for(unsigned i=0;i<n;++i){double squared=0;for(unsigned j=0;j<3;++j){unsigned scalar=3*i+j;double value=index[scalar]<0?0:weights[scalar]*v[index[scalar]];squared+=value*value;}speed=std::max(speed,std::sqrt(squared));}std::cout<<(step+1)*dt<<','<<tip<<','<<U<<','<<speed<<','<<residual.norm()<<','<<(g-load).norm()<<','<<iteration<<'\n';
 }return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
