#include "../../models/film_sphere_contact/SphereStep.h"
#include <fstream>
#include <iostream>
#include <string>
using namespace regrip_film_sphere;
// A rejected Newton state is a numerical diagnostic, NEVER accepted physics.
int main(int argc,char**argv){try{
 if(argc<2)throw std::runtime_error("usage: replay failure_trace [solve]");
 std::ifstream in(argv[1]);std::string word;bool found=false;
 while(in>>word)if(word=="SPHERE_FAILURE_V2"){found=true;break;}
 if(!found)throw std::runtime_error("missing complete V2 failure block");
 unsigned nx,guides,count;double offset,bond,h,damping,tension,radius;bool rootSecond,closest;Point center;
 in>>nx>>guides>>offset>>bond>>rootSecond>>h>>damping>>tension>>center[0]>>center[1]>>center[2]>>radius>>closest>>count;
 Assembly model(nx);model.guideIntervals=guides;model.guideOffset=offset;model.bondK=bond;model.rootGuideSecondOrder=rootSecond;
 auto expect=[&](const char*name){in>>word;if(word!=name)throw std::runtime_error(std::string("expected ")+name+",found "+word);};
 expect("MASS");std::vector<double>mass(model.size());for(auto&x:mass)in>>x;
 auto points=[&](const char*name){expect(name);std::vector<Point>x(model.size());for(auto&p:x)for(auto&v:p)in>>v;return x;};
 auto q=points("PREVIOUS_U"),v=points("PREVIOUS_V"),initial=points("INITIAL_V"),trial=points("REJECTED_V");
 std::vector<CoupledContactStep::Plane>planes(count);
 for(auto&p:planes){expect("PLANE");in>>p.target>>p.lambda>>p.row;p.J.resize(model.size());for(auto&j:p.J)for(auto&x:j)in>>x;expect("SUPPORT");unsigned n;in>>n;p.support.resize(n);for(auto&i:p.support)in>>i;}
 Eigen::VectorXd lambda(count);in>>word;if(word=="TRIAL_LAMBDA"){for(unsigned i=0;i<count;++i)in>>lambda(i);expect("END_SPHERE_FAILURE");}else if(word!="END_SPHERE_FAILURE"||count)throw std::runtime_error("nonempty failure lacks actual trial multipliers");if(!in)throw std::runtime_error("truncated failure block");
 CoupledContactStep base(model,mass,h,damping,tension,q,v,planes,true,true);SphereStep sphere(base,center,radius,closest);auto y=base.mechanics.pack(trial);auto e=base.mechanics.evaluate(y);auto g=sphere.geometry(y,lambda);Eigen::MatrixXd H=e.tangent-g.H;Eigen::LDLT<Eigen::MatrixXd>mechanical(e.tangent),contact(H);
 std::cout<<std::setprecision(17)<<"rows "<<count<<" closest "<<closest<<" residual "<<(e.gradient-g.C*lambda).norm()<<" gap "<<CoupledContactStep::gapError(g.gap,lambda)<<" mechanical_minD "<<mechanical.vectorD().minCoeff()<<" lagrangian_minD "<<contact.vectorD().minCoeff()<<" contact_H_norm "<<g.H.norm()<<'\n';
 for(unsigned k=0;k<count;++k)std::cout<<"row "<<k<<" support "<<planes[k].support.size()<<" gap "<<g.gap(k)<<" lambda "<<lambda(k)<<" Cnorm "<<g.C.col(k).norm()<<'\n';
 Eigen::VectorXd direction(y.size());for(int i=0;i<y.size();++i)direction(i)=std::sin(i+1.);direction.normalize();
 for(double epsilon:{1e-3,1e-4,1e-5}){auto lo=(y-epsilon*direction).eval(),hi=(y+epsilon*direction).eval();auto gl=sphere.geometry(lo,lambda),gh=sphere.geometry(hi,lambda);Eigen::VectorXd rl=base.mechanics.evaluate(lo).gradient-gl.C*lambda,rh=base.mechanics.evaluate(hi).gradient-gh.C*lambda;double defect=((rh-rl)/(2*epsilon)-H*direction).norm()/(H*direction).norm();std::cout<<"FD epsilon "<<epsilon<<" relative_tangent_defect "<<defect<<" gap_derivative_absolute_defect "<<((gh.gap-gl.gap)/(2*epsilon)-h*g.C.transpose()*direction).norm()<<'\n';}
 if(count&&contact.vectorD().minCoeff()>0){Eigen::VectorXd inverseG=contact.solve(e.gradient);Eigen::MatrixXd inverseC=contact.solve(g.C),W=h*g.C.transpose()*inverseC;Eigen::VectorXd d=g.gap-h*g.C.transpose()*inverseG,next=CoupledContactStep::dual(W,d,lambda),increment=-inverseG+inverseC*next;std::cout<<"linear_QP_gap "<<CoupledContactStep::gapError(d+W*next,next)<<" linear_stationarity "<<(e.gradient-g.C*lambda+H*increment-g.C*(next-lambda)).norm()<<" increment_norm "<<increment.norm()<<" next_lambda "<<next.transpose()<<'\n';for(double alpha:{1.,.5,.1,.01,.001,.0001}){auto trialY=(y+alpha*increment).eval(),trialLambda=(lambda+alpha*(next-lambda)).eval();auto gt=sphere.geometry(trialY,trialLambda);auto et=base.mechanics.evaluate(trialY);std::cout<<"directional_trial "<<alpha<<" residual "<<(et.gradient-gt.C*trialLambda).norm()<<" gap "<<CoupledContactStep::gapError(gt.gap,trialLambda)<<" phi_change "<<et.phi-e.phi<<" linear_residual_remainder "<<(et.gradient-gt.C*trialLambda-(1-alpha)*(e.gradient-g.C*lambda)).norm()<<'\n';}}
 if(argc>2&&std::string(argv[2])=="free-newton"){
  if(count)throw std::runtime_error("indefinite Newton diagnostic is unconstrained only");
  double first=e.gradient.norm();bool solved=false;
  for(unsigned iteration=0;iteration<30;++iteration){auto current=base.mechanics.evaluate(y);double residual=current.gradient.norm();Eigen::LDLT<Eigen::MatrixXd>inertia(current.tangent);std::cout<<"free_newton "<<iteration<<" residual "<<residual<<" minD "<<inertia.vectorD().minCoeff()<<'\n';if(residual<=std::max(1e-15,first*1e-7)){solved=true;break;}Eigen::FullPivLU<Eigen::MatrixXd>factor(current.tangent);if(!factor.isInvertible())throw std::runtime_error("singular exact free tangent");Eigen::VectorXd delta=factor.solve(-current.gradient);double alpha=1;bool accepted=false;for(unsigned line=0;line<16;++line){auto candidate=(y+alpha*delta).eval();if(base.mechanics.evaluate(candidate).gradient.norm()<=(1-1e-4*alpha)*residual){y=candidate;accepted=true;break;}alpha*=.5;}if(!accepted)throw std::runtime_error("free exact-tangent residual search failed");}if(!solved)throw std::runtime_error("free diagnostic Newton budget");
 }
 if(argc>2&&std::string(argv[2])=="solve"){
#ifdef REGRIP_RELEASE_ACTIVE_SET
 sphere.releaseActiveSet=true;
#endif
#ifdef REGRIP_SQP_MERIT
 sphere.sqpMerit=true;
#endif
 auto result=sphere.solve(initial,&std::cout);std::cout<<"SOLVED residual "<<result.residual<<" gap "<<result.gap<<" iterations "<<result.iterations<<'\n';}
 return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
