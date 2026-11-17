#include "../models/film_coupled_adaptive/AdaptiveStep.h"
#include <iostream>
#ifdef REGRIP_VALUE_ENERGY_REFERENCE
#include "../models/film_value_energy/ValueEnergy.h"
#endif
using namespace regrip_coupled_adaptive;
int main(int argc,char**argv){try{bool trace=false,horizon=false,actual21=false,fast=false,reuseCoarse=false;unsigned budget=256;for(int i=1;i<argc;++i){trace|=std::string(argv[i])=="--trace";horizon|=std::string(argv[i])=="--horizon";actual21|=std::string(argv[i])=="--actual21";fast|=std::string(argv[i])=="--value-energy";reuseCoarse|=std::string(argv[i])=="--reuse-coarse";if(std::string(argv[i])=="--trials"&&i+1<argc)budget=std::stoul(argv[++i]);}if(budget>384)throw std::runtime_error("profiled reference budget cap384");
 Assembly model(actual21?21:5);if(actual21)model.guideOffset=5;auto mass=model.masses();std::vector<Point>q(model.size()),v(model.size()),zero(model.size());unsigned tip=model.id(0,model.nx-1,2);v[tip][2]=-3;std::vector<std::array<unsigned,3>>triangles;
 for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<model.nx;++i)for(unsigned j=0;j+1<model.parts[part].ny;++j){unsigned a=model.id(part,i,j),b=model.id(part,i+1,j),c=model.id(part,i,j+1),d=model.id(part,i+1,j+1);triangles.push_back({a,b,c});triangles.push_back({b,d,c});}
 double radius=actual21?8.01:1;Body body;body.center=vector(model.rest()[tip])-Eigen::Vector3d(0,0,radius+.001);CoupledPlaneStep m(model,mass,.001,2,0,q,v,zero,0);System system(m,triangles,body,radius);EventControl control;
 EnergyEvaluator evaluator;
#ifdef REGRIP_VALUE_ENERGY_REFERENCE
 if(fast)evaluator=[](const Assembly&m,const std::vector<Point>&q){return regrip_value_energy::evaluate({m.nx,m.guideIntervals,m.guideOffset,m.bondK,m.rootGuideSecondOrder},q);};
#else
 if(fast)throw std::runtime_error("value backend not linked");
#endif
 auto result=adaptiveStep(system,0,control,1e-4,budget,12,trace?&std::cerr:nullptr,horizon,evaluator,reuseCoarse);double elapsed=0;unsigned events=0;for(const auto&s:result.segments){if(s.error>1e-4||s.result.minimumGap< -1e-10||std::abs(s.time-elapsed)>1e-14)throw std::runtime_error("adaptive accepted segment gates");elapsed+=s.h;events+=bool(s.result.event);}
 if(std::abs(elapsed-.001)>1e-14||events!=1||result.rejected==0)throw std::runtime_error("adaptive event/refinement coverage");
 if(!actual21){auto repeated=adaptiveStep(system,0,control,1e-4,256,12,nullptr,horizon);if(repeated.segments.size()!=result.segments.size()||repeated.trials!=result.trials)throw std::runtime_error("adaptive query/optimization branch impurity");for(unsigned i=0;i<result.segments.size();++i){const auto&a=result.segments[i];const auto&b=repeated.segments[i];if(a.time!=b.time||a.h!=b.h||a.error!=b.error||a.result.state.q!=b.result.state.q||a.result.state.v!=b.result.state.v||a.result.state.body.center!=b.result.state.body.center||a.result.state.body.linear!=b.result.state.body.linear)throw std::runtime_error("value/coarse reuse changes accepted physical states");}}
 bool rejected=false;try{adaptiveStep(system,0,control,1e-12,1,0);}catch(const std::runtime_error&){rejected=true;}if(!rejected)throw std::runtime_error("adaptive unresolved error silently ignored");
 double jerk=1,h=.001,coarseEnergy=.5*std::pow(jerk*h*h*h/4,2),fineEnergy=.5*std::pow(3*jerk*h*h*h/16,2);if(std::abs((coarseEnergy-fineEnergy)/coarseEnergy-7./16)>1e-14)throw std::runtime_error("newborn jerk energy reference");
 std::cout<<"PASS adaptive independent trials "<<result.trials<<" rejected "<<result.rejected<<" accepted_segments "<<result.segments.size()<<" max_controller_error "<<result.maximumAcceptedError<<" max_instantaneous_relative_error "<<result.maximumInstantaneousRelativeError<<" horizon_norm "<<horizon<<" value_energy "<<fast<<" coarse_reuses "<<result.coarseReuses<<" subintegrations "<<result.subintegrations<<";NOT SOFA/global time qualification\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
