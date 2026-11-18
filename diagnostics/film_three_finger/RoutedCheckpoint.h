#pragma once
#include "../../models/film_three_finger/SharedFilmSystem.h"
#include <fstream>
namespace regrip_routed_checkpoint {
using namespace regrip_three_finger;
inline void read(const std::string&path,SharedFilmSystem&s,Eigen::VectorXd&q,Eigen::VectorXd&v,double&time,double&h){
 std::ifstream in(path);std::string magic,token;unsigned step;in>>magic>>time>>h>>step>>token;
 if(magic!="REGRIP_ROUTED_PERSISTENT_V1"||token.size()!=64||h!=.0002||!(time>0&&time<.03))throw std::runtime_error("bounded route-bound source checkpoint required");
 unsigned n=s.initial.size(),nf=s.shared.nf,body=3*nf;q.resize(n);v.resize(n);for(auto*z:{&q,&v})for(double&x:*z)in>>x;Eigen::Vector4d quaternion;for(double&x:quaternion)in>>x;
 if(!q.allFinite()||!v.allFinite()||q.tail<3>().norm()!=0||v.tail<3>().norm()!=0||std::abs(quaternion.squaredNorm()-1)>1e-14)throw std::runtime_error("finite actual zero-spin sphere checkpoint required");
 s.shared.M.setZero();for(unsigned f=0;f<3;++f){auto&m=s.shared.films[f].film;for(unsigned i=0;i<m.model.size();++i){double mass;in>>mass;if(!(mass>0))throw std::runtime_error("positive public mass required");m.mass[i]=mass;for(unsigned d=0;d<3;++d){unsigned a=3*i+d;int k=m.index[a];if(k>=0)s.shared.M(f*nf+k,f*nf+k)+=mass*m.weight[a]*m.weight[a];}}}for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)in>>s.shared.M(body+i,body+j);
 for(unsigned f=0;f<3;++f){const auto&m=s.shared.films[f].film;for(unsigned a=0;a<m.index.size();++a){int index;double weight;in>>index>>weight;if(index!=m.index[a]||weight!=m.weight[a])throw std::runtime_error("exact actual root map differs");}}
 for(unsigned f=0;f<3;++f){unsigned triangle,feature;in>>triangle>>feature;auto row=s.selected(q,f);if(triangle!=row.triangle||feature!=row.feature)throw std::runtime_error("accepted row identity differs");}
 std::string extra;if(!in||in>>extra||s.clearance(q)< -1e-10||(s.geometry(q).J*v).cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("checkpoint physical input invalid");
}
}
