#include "../../models/film_three_finger_resume/FaceEdgeTransfer.h"
#include "../../models/film_three_finger_event/BlockFree.h"
#include "../../models/film_three_finger_resume/AccelerationRelease.h"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <optional>
using namespace regrip_three_resume;
int main(int argc,char**argv){try{
 if(argc!=3&&argc!=4)throw std::runtime_error("V2 checkpoint,output[,root] required");
 std::ifstream in(argv[1]);std::string magic,identity;double time,h;unsigned step;
 in>>magic>>time>>h>>step>>identity;if(magic!="REGRIP_EDGE_V2")throw std::runtime_error("V2 required");
 SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;
 unsigned n=s.initial.size(),nf=s.shared.nf;Eigen::VectorXd q(n),v(n);
 for(double&x:q)in>>x;for(double&x:v)in>>x;double unused;for(unsigned i=0;i<4;++i)in>>unused;
 s.shared.M.setZero();
 for(unsigned f=0;f<3;++f){auto&m=s.shared.films[f].film;for(unsigned i=0;i<m.mass.size();++i){in>>m.mass[i];for(unsigned d=0;d<3;++d){unsigned a=3*i+d;if(m.index[a]>=0)s.shared.M(f*nf+m.index[a],f*nf+m.index[a])+=m.mass[i]*m.weight[a]*m.weight[a];}}}
 for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)in>>s.shared.M(3*nf+i,3*nf+j);
 for(unsigned f=0;f<3;++f){const auto&m=s.shared.films[f].film;for(unsigned a=0;a<m.index.size();++a){int index;double weight;in>>index>>weight;if(index!=m.index[a]||weight!=m.weight[a])throw std::runtime_error("mapping differs");}}
 unsigned count;in>>count;if(count!=3)throw std::runtime_error("three owned edges required");std::vector<EdgeOwner>edges;
 for(unsigned f=0;f<count;++f){std::string label;EdgeOwner e;double born,parameter;in>>label>>e.finger>>e.sourceTriangle>>e.nodes[0]>>e.nodes[1]>>born>>parameter;for(unsigned d=0;d<3;++d)in>>unused;if(label!="EDGE"||e.finger!=f)throw std::runtime_error("edge identity invalid");edges.push_back(e);}
 std::string label;double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time)throw std::runtime_error("clock/input invalid");
 auto force=[&](const auto&x,double t){return s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension);};
 if(argc==4&&std::string(argv[3]).rfind("ac",0)==0){
  unsigned grid=std::stoul(std::string(argv[3]).substr(2));double window=h/5;
  auto r=accelerationRelease(s,q,v,time,window,edges,grid);
  if(r.finalMask!=0)throw std::runtime_error("bounded acceleration reference did not release all rows");
  regrip_film_impact::EventControl control;control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;
  auto after=regrip_three_event::freeMidpoint(s,r.q,r.v,r.endTime,(time+h)-r.endTime,control);
  Eigen::VectorXd midpoint=(r.q+after.q)/2;double gap=std::min({r.minimumGap,s.clearance(after.q),s.clearance(midpoint)});
  if(gap< -1e-10)throw std::runtime_error("released free remainder whole-stage clearance fails");
  std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,minimum_gap_mm,momentum_Ns,minimum_force_N,final_mask,evaluations,q,v\n"<<time+h<<','<<gap<<','<<r.momentumResidual+after.momentumResidual<<','<<r.minimumForce<<','<<r.finalMask<<','<<r.stages.size()<<",\""<<after.q.transpose()<<"\",\""<<after.v.transpose()<<"\"\n";out.flush();
  std::cout<<"PASS independent20us acceleration complementarity release plus accumulated-clock free midpoint;NOT actual SOFA/time/grasp certificate\n";return 0;
 }
 if(argc==4&&std::string(argv[3]).rfind("rk",0)==0){
  unsigned grid=std::stoul(std::string(argv[3]).substr(2));if(grid<8||grid>128)throw std::runtime_error("bounded RK reference grid8..128");
  Eigen::VectorXd diagonal=s.shared.M.diagonal();Eigen::MatrixXd off=s.shared.M-diagonal.asDiagonal().toDenseMatrix();if(off.cwiseAbs().maxCoeff()!=0||diagonal.minCoeff()<=0)throw std::runtime_error("RK reference requires exact diagonal projected mass");
  auto reaction=[&](const Eigen::VectorXd&x,const Eigen::VectorXd&vel,double t){auto g=edgeGeometry(s,x,edges);Eigen::VectorXd a=force(x,t).value.cwiseQuotient(diagonal)-2*vel;Eigen::VectorXd normal=g.J*a;for(int i=0;i<normal.size();++i)normal(i)+=vel.dot(g.H[i]*vel);Eigen::MatrixXd miJ=g.J.transpose();for(int i=0;i<miJ.rows();++i)miJ.row(i)/=diagonal(i);Eigen::MatrixXd W=g.J*miJ;Eigen::VectorXd lambda=W.fullPivLu().solve(-normal);return lambda;};
  unsigned evaluations=0;
  auto rhs=[&](const Eigen::VectorXd&y,double t){++evaluations;Eigen::VectorXd x=y.head(n),vel=y.tail(n);auto g=edgeGeometry(s,x,edges);Eigen::VectorXd a=force(x,t).value.cwiseQuotient(diagonal)-2*vel;Eigen::VectorXd normal=g.J*a;for(int i=0;i<normal.size();++i)normal(i)+=vel.dot(g.H[i]*vel);Eigen::MatrixXd miJ=g.J.transpose();for(int i=0;i<miJ.rows();++i)miJ.row(i)/=diagonal(i);Eigen::MatrixXd W=g.J*miJ;Eigen::VectorXd lambda=W.fullPivLu().solve(-normal),out(2*n);out.head(n)=vel;out.tail(n)=a+miJ*lambda;return out;};
  auto advance=[&](const Eigen::VectorXd&y,double t,double dt){Eigen::VectorXd k1=rhs(y,t),k2=rhs(y+dt/2*k1,t+dt/2),k3=rhs(y+dt/2*k2,t+dt/2),k4=rhs(y+dt*k3,t+dt);Eigen::VectorXd out=y+dt/6*(k1+2*k2+2*k3+k4);return out;};
  Eigen::VectorXd y(2*n);y.head(n)=q;y.tail(n)=v;double clock=time,dt=2e-5/grid;bool found=false;double lo=0,hi=0;
  for(unsigned i=0;i<grid;++i){auto next=advance(y,clock,dt);if(reaction(next.head(n),next.tail(n),clock+dt).minCoeff()<=0){lo=0;hi=dt;for(unsigned k=0;k<40&&hi-lo>1e-13;++k){double mid=(lo+hi)/2;auto trial=advance(y,clock,mid);if(reaction(trial.head(n),trial.tail(n),clock+mid).minCoeff()>0)lo=mid;else hi=mid;}y=advance(y,clock,(lo+hi)/2);clock+=(lo+hi)/2;found=true;break;}y=std::move(next);clock+=dt;}
  if(!found)throw std::runtime_error("RK physical reaction event not found");auto g=edgeGeometry(s,y.head(n),edges);double gap=s.clearance(y.head(n)),vn=(g.J*y.tail(n)).cwiseAbs().maxCoeff();
  std::ofstream out(argv[2]);out<<std::setprecision(17)<<"event_time_s,bracket_width_s,whole_gap_mm,normal_velocity_mm_s,evaluations,q,v\n"<<clock<<','<<hi-lo<<','<<gap<<','<<vn<<','<<evaluations<<",\""<<y.head(n).transpose()<<"\",\""<<y.tail(n).transpose()<<"\"\n";out.flush();
  if(gap< -1e-10||vn>1e-10)throw std::runtime_error("independent acceleration-ODE geometric drift gate fails;NO projection");std::cout<<"PASS bounded independent acceleration-ODE event;NOT actual SOFA/unilateral full trajectory\n";return 0;
 }
 if(argc==4){
  // Signed bilateral branch is ONLY a mathematical event bracket. It is never
  // written to SOFA or presented as an accepted unilateral state.
  auto advance=[&](double interval){std::optional<regrip_collocation::RowsResult> trial;auto capture=[&](const auto&r){trial=r;};try{return regrip_collocation::persistentRows(s.shared.M,2,q,v,time,interval,force,[&](const auto&x){return edgeGeometry(s,x,edges);},false,capture,capture);}catch(const std::domain_error&){if(!trial)throw;return *trial;}};
  Eigen::LDLT<Eigen::MatrixXd>mass(s.shared.M);
  auto signedReaction=[&](const Eigen::VectorXd&x,const Eigen::VectorXd&vel,double t){auto g=edgeGeometry(s,x,edges);Eigen::VectorXd a=mass.solve(force(x,t).value-2*s.shared.M*vel);Eigen::VectorXd normal=g.J*a;for(int i=0;i<normal.size();++i)normal(i)+=vel.dot(g.H[i]*vel);Eigen::MatrixXd W=g.J*mass.solve(g.J.transpose());Eigen::VectorXd reaction=W.fullPivLu().solve(-normal);return reaction;};
  bool admissible=std::string(argv[3])=="admissible";
  auto right=advance(h);if(signedReaction(q,v,time).minCoeff()<=0||signedReaction(right.q,right.v,time+h).maxCoeff()>=0)throw std::runtime_error("all-row reaction root not bracketed");double lo=0,hi=h;
  for(unsigned k=0;k<48&&hi-lo>(admissible?1e-17:1e-13);++k){double mid=(lo+hi)/2;auto r=advance(mid);double test=admissible?r.stages.back().force.minCoeff():signedReaction(r.q,r.v,time+mid).minCoeff();if(test>0)lo=mid;else hi=mid;}
  double interval=admissible?lo:hi;
  auto event=advance(interval);auto reaction=signedReaction(event.q,event.v,time+interval);auto g=edgeGeometry(s,event.q,edges);Eigen::VectorXd a=mass.solve(force(event.q,time+interval).value-2*s.shared.M*event.v),normal=g.J*a;for(int i=0;i<normal.size();++i)normal(i)+=event.v.dot(g.H[i]*event.v);
  regrip_film_impact::EventControl control; // same existing C2 definition below
  control.maximum=.0001;control.ramp=.01;control.release=.02;control.end=.03;control.c2=true;
  auto after=regrip_three_event::freeMidpoint(s,event.q,event.v,time+interval,h-interval,control);double gap=s.clearance(after.q);
  double preForce=event.initialForce.minCoeff(),preGap=s.clearance(event.q);for(const auto&stage:event.stages){preForce=std::min(preForce,stage.force.minCoeff());preGap=std::min(preGap,s.clearance(stage.q));}
  std::ofstream root(argv[2]);root<<std::setprecision(17)<<"event_time_s,bracket_width_s,reaction_min_N,reaction_max_N,free_normal_acceleration_min_mm_s2,end_gap_mm,free_momentum_Ns,pre_collocation_force_min_N,pre_whole_stage_gap_mm,event_normal_velocity_mm_s\n"<<time+interval<<','<<hi-lo<<','<<reaction.minCoeff()<<','<<reaction.maxCoeff()<<','<<normal.minCoeff()<<','<<gap<<','<<after.momentumResidual<<','<<preForce<<','<<preGap<<','<<(g.J*event.v).cwiseAbs().maxCoeff()<<'\n';root.flush();
  if(admissible&&preForce<0)throw std::runtime_error("admissible split would commit tensile pre-event force");
  if(reaction.maxCoeff()>0||normal.minCoeff()<0||gap< -1e-10)throw std::runtime_error("candidate release root/remainder gate fails;NOT accepted");
  std::cout<<"PASS independent signed reaction event/free remainder diagnostic;NOT actual unilateral event commit\n";return 0;
 }
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"stage,time,finger,gap_mm,normal_velocity_mm_s,force_N,momentum_residual_Ns,velocity_residual_mm_s\n";bool observed=false;
 auto observer=[&](const regrip_collocation::RowsResult&r){observed=true;auto g=edgeGeometry(s,q,edges);for(unsigned f=0;f<3;++f)out<<"accepted_initial,"<<time<<','<<f<<','<<g.gap(f)<<','<<g.J.row(f).dot(v)<<','<<r.initialForce(f)<<','<<r.momentumResidual<<','<<r.velocityResidual<<'\n';for(const auto&stage:r.stages)for(unsigned f=0;f<3;++f)out<<"REJECTED_NOT_COMMITTED,"<<stage.time<<','<<f<<','<<stage.geometry.gap(f)<<','<<stage.geometry.J.row(f).dot(stage.v)<<','<<stage.force(f)<<','<<r.momentumResidual<<','<<r.velocityResidual<<'\n';out.flush();};
 try{auto r=regrip_collocation::persistentRows(s.shared.M,2,q,v,time,h,[&](const auto&x,double t){return s.force(x,regrip_film_rail::ControlProfile::evaluate(t,.0001,.01,.02,.03,true).tension);},[&](const auto&x){return edgeGeometry(s,x,edges);},false,{},observer);throw std::runtime_error("expected rejected release was not reproduced");}
 catch(const std::domain_error&e){if(!observed)throw;std::cout<<"PASS diagnostic captured rejected signed trial;NO negative force committed: "<<e.what()<<'\n';}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
