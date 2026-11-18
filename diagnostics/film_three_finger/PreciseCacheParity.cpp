#include "../../models/film_three_finger/SharedFilmSystem.h"
#include "../../models/film_three_finger/CachedSharedFilmSystem.h"
#include <cstring>
#include <fstream>
#include <iostream>
using namespace regrip_three_finger;
int main(int argc,char**argv){try{
 if(argc!=2)throw std::runtime_error("actual stored query samples required");SharedFilmSystem a(Layout(),{0,0,-.001},true,true);CachedSharedFilmSystem b(Layout(),{0,0,-.001},true,true);a.exactUnresolved=b.exactUnresolved=true;std::ifstream in(argv[1]);unsigned count;in>>count;if(!in||count==0||count>32)throw std::runtime_error("bounded actual query set required");regrip_film_impact::EventControl c{.0001,.01,.02,.03,true};double maximum=0;
 for(unsigned i=0;i<count;++i){double t;in>>t;Eigen::VectorXd q(a.initial.size());for(double&x:q)in>>x;if(!in||!q.allFinite())throw std::runtime_error("actual sample missing");auto original=q;std::array<Row,3>ra,rb;auto ga=a.geometry(q,&ra),gb=b.geometry(q,&rb);auto fa=a.force(q,c.sample(t).tension),fb=b.force(q,c.sample(t).tension);
  maximum=std::max({maximum,(ga.gap-gb.gap).cwiseAbs().maxCoeff(),(ga.J-gb.J).cwiseAbs().maxCoeff(),(fa.value-fb.value).cwiseAbs().maxCoeff(),(fa.negativeTangent-fb.negativeTangent).cwiseAbs().maxCoeff()});
  for(unsigned f=0;f<3;++f){if(ra[f].triangle!=rb[f].triangle||ra[f].feature!=rb[f].feature)throw std::runtime_error("selected row identity differs");maximum=std::max(maximum,(ga.H[f]-gb.H[f]).cwiseAbs().maxCoeff());}
  if(std::memcmp(original.data(),q.data(),q.size()*sizeof(double)))throw std::runtime_error("query changed input state");
 }
 if(maximum!=0)throw std::runtime_error("force/Hessian/gap/Jacobian/Hessian not EXACT");std::cout<<"{\"status\":\"PASS\",\"actual_stored_queries\":"<<count<<",\"force_H_gap_J_contact_H_max_abs\":"<<maximum<<",\"query_purity\":true}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
