#include "../models/film_three_finger_event/DenseSurfacePath.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_event;
int main(){try{
 SharedFilmSystem s(Layout(),{0,0,-.001},true,true);auto q=s.initial;unsigned body=3*s.shared.nf;Eigen::VectorXd v=Eigen::VectorXd::Zero(q.size());q(body+2)+=.0001;v(body+2)=-1;EventControl control{.0001,.01,.02,.03,true};double h=.0002;auto endpoint=freeMidpoint(s,q,v,0,h,control);auto dense=denseSurfacePath(s,q,v,endpoint,h);
 auto at=dense.path.position(1);double error=0;unsigned offset=0;for(unsigned f=0;f<3;++f){const auto&film=s.shared.films[f].film;auto rest=film.model.rest(),local=film.expand(endpoint.q.segment(f*s.shared.nf,s.shared.nf));for(unsigned i=0;i<local.size();++i){Eigen::Vector3d expected=s.layout.world(f,add(rest[i],local[i]))-endpoint.q.segment<3>(body);error=std::max(error,(vector(at[offset+i])-expected).norm());}offset+=local.size();}
 if(error>1e-13)throw std::runtime_error("shared dense endpoint mismatch");auto event=regrip_film_impact::earliestSurfaceEvent(dense.path,dense.triangles,{0,0,0},s.layout.bufferRadius,1e-13/h,1e-12);
 if(!event||event->rows.empty())throw std::runtime_error("missing whole three-film numerical-path impact");std::array<unsigned,3>counts{};for(const auto&row:event->rows)++counts[dense.owners.at(row.triangle).first];if(!counts[0]||!counts[1]||!counts[2])throw std::runtime_error("missing simultaneous material frame");
 std::cout<<std::setprecision(17)<<"dense_event_time="<<h*event->fraction<<" rows="<<event->rows.size()<<" triangles="<<dense.triangles.size()<<" endpoint_error="<<error<<" evaluations="<<event->evaluations<<'\n';std::cout<<"PASS whole3film relative quadratic numerical-path earliest event;NOT globally earliest partial nonlinear family/SOFA/grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
