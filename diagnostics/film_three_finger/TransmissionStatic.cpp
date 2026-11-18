#include "../../models/film_transmission/Kernel.h"
#include <Eigen/SparseLU>
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_transmission;
int main(int argc,char**argv){try{
 if(argc!=6&&argc!=7)throw std::runtime_error("bond,offset,load_stages,mass,prefix[,energy] required");bool hybrid=argc==7&&std::string(argv[6])=="hybrid";bool energy=hybrid||(argc==7&&std::string(argv[6])=="energy");auto m=model(std::stod(argv[1]),std::stod(argv[2]));unsigned stages=std::stoul(argv[3]);if(stages<8||stages>64)throw std::runtime_error("bounded8..64 load continuation stages");auto mass=publicMass(argv[4]);std::vector<Point>q(m.size()),zero(q.size());auto map=mechanics(m,q,zero,.0001,0,mass);Eigen::VectorXd x=map.pack(q);std::string prefix=argv[5];std::ofstream trace(prefix+".newton.csv"),states(prefix+".states.csv");trace<<std::setprecision(17)<<"stage,iteration,T,force_residual_N,step_length_mm,line_search_trials\n";states<<std::setprecision(17)<<"stage,T,residual_N,U_skin,U_rails,U_attachment,cable_length_mm,q\n";
 for(unsigned stage=1;stage<=stages;++stage){double T=.0001*stage/stages;bool converged=false;
  for(unsigned it=0;it<60;++it){auto e=parts(map,map.expand(x),T);double norm=e.force.norm();if(norm<=1e-12){states<<stage<<','<<T<<','<<norm<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<e.cable;quote(states,map.expand(x));states<<'\n';states.flush();converged=true;break;}
   Eigen::SparseMatrix<double>K=e.stiffness.sparseView(0.,0.);Eigen::SparseLU<Eigen::SparseMatrix<double>>factor;factor.compute(K);if(factor.info()!=Eigen::Success)throw std::runtime_error("unmodified physical static tangent singular;no regularization");Eigen::VectorXd delta=factor.solve(e.force);if(factor.info()!=Eigen::Success||!delta.allFinite())throw std::runtime_error("static Newton solve failed");bool accepted=false;
   double potential=e.skin+e.rails+e.bond+T*(e.cable-200),slope=-e.force.dot(delta);if(energy&&!hybrid&&!(slope<0))throw std::runtime_error("physical Newton direction is not potential descent;no artificial stiffness");
   for(unsigned cut=0;cut<20;++cut){double alpha=std::ldexp(1.,-int(cut));Eigen::VectorXd trial=x+alpha*delta;auto candidate=parts(map,map.expand(trial),T);double nextPotential=candidate.skin+candidate.rails+candidate.bond+T*(candidate.cable-200);bool residualMerit=candidate.force.norm()<(1-1e-4*alpha)*norm,merit=energy?((slope<0&&nextPotential<=potential+1e-4*alpha*slope)||(hybrid&&residualMerit)):residualMerit;if(merit){x=std::move(trial);trace<<stage<<','<<it<<','<<T<<','<<norm<<','<<alpha*delta.norm()<<','<<cut<<'\n';trace.flush();accepted=true;break;}}
   if(!accepted)throw std::runtime_error("static residual line search rejected;no fictitious force/compliance");
  }if(!converged)throw std::runtime_error("static60-Newton budget reached;not equilibrium");
 }
 std::cout<<"PASS independent nonlinear static force equilibrium;stability/contact/dynamic convergence NOT certified\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
