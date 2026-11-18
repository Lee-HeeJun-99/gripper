#include "RoutedCheckpoint.h"
#include "../../models/film_routed_contact/DefectStep.h"
#include <iomanip>
#include <iostream>
using namespace regrip_routed_checkpoint;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("checkpoint,refinement,exclusive output required");unsigned refinement=std::stoul(argv[2]);if(refinement!=1&&refinement!=2&&refinement!=4)throw std::runtime_error("three declared local refinements only");SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;read(argv[1],s,q,v,time,h);double end=time+h;EventControl control{.0001,.01,.02,.03,true};if(std::ifstream(argv[3]))throw std::runtime_error("output exists");std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time,h,minimum_gap_mm,momentum_Ns,normal_velocity_mm_s,minimum_force_N,triangle0,feature0,q,v\n";unsigned trials=0,rejected=0,leaves=0,depth=0;double minimum=s.clearance(q),momentum=0,velocity=0,force=1e9;
 for(unsigned i=0;i<refinement;++i){double dt=h/refinement;if(i+1==refinement&&time+dt!=end)dt=end-time;auto r=regrip_defect_step::integrate(s.shared.M,2,q,v,time,dt,[&](const auto&x,double t){return s.force(x,control.sample(t).tension);},[&](const auto&x){return s.geometry(x);},[&](const auto&x){return s.clearance(x);});
  trials+=r.trials;rejected+=r.rejected;leaves+=r.leaves.size();depth=std::max(depth,r.maximumDepth);minimum=std::min(minimum,r.minimumGap);
  for(const auto&leaf:r.leaves){momentum=std::max(momentum,leaf.result.momentumResidual);velocity=std::max(velocity,leaf.result.velocityResidual);force=std::min(force,leaf.result.initialForce.minCoeff());for(const auto&z:leaf.result.stages)force=std::min(force,z.force.minCoeff());auto row=s.selected(leaf.result.q,0);out<<leaf.begin+leaf.h<<','<<leaf.h<<','<<s.clearance(leaf.result.q)<<','<<leaf.result.momentumResidual<<','<<leaf.result.velocityResidual<<','<<leaf.result.stages.back().force.minCoeff()<<','<<row.triangle<<','<<row.feature;for(const auto*z:{&leaf.result.q,&leaf.result.v}){out<<',';for(int j=0;j<z->size();++j)out<<(j?" ":"")<<(*z)[j];}out<<'\n';out.flush();}
  q=r.q;v=r.v;time+=dt;
 }
 if(time!=end||minimum< -1e-10||momentum>1e-17||velocity>1e-10||force<0)throw std::runtime_error("composed physical gates failed");
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"trials\":"<<trials<<",\"rejected\":"<<rejected<<",\"leaves\":"<<leaves<<",\"maximum_depth\":"<<depth<<",\"end_time_s\":"<<time<<",\"minimum_gap_mm\":"<<minimum<<",\"momentum_Ns\":"<<momentum<<",\"normal_velocity_mm_s\":"<<velocity<<",\"minimum_force_N\":"<<force<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
