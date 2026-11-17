#include "../../models/film_three_finger_event/AllRowRelease.h"
#include "../../models/film_three_finger_event/DenseSurfacePath.h"
#include <fstream>
#include <iostream>
#include <iomanip>
using namespace regrip_three_event;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("mass,saved actual q/v,output required");SharedFilmSystem s(Layout(),{0,0,.001},true,true);s.exactUnresolved=true;unsigned nf=s.shared.nf,n=s.shared.M.rows();std::ifstream mass(argv[1]);unsigned count;mass>>count;if(count!=s.shared.films[0].film.mass.size())throw std::runtime_error("actual release mass dimensions");s.shared.M.setZero();for(unsigned f=0;f<3;++f){auto&film=s.shared.films[f].film;for(unsigned i=0;i<count;++i){double m;mass>>m;if(!(m>0)||std::abs(m-film.mass[i])>1e-13*film.mass[i])throw std::runtime_error("actual release mass differs");film.mass[i]=m;for(unsigned d=0;d<3;++d){unsigned a=3*i+d;int k=film.index[a];if(k>=0)s.shared.M(f*nf+k,f*nf+k)+=m*film.weight[a]*film.weight[a];}}}double m,I;mass>>m>>I;if(!mass||m!=.0001||std::abs(I-.036)>1e-16)throw std::runtime_error("actual release rigid mass");s.shared.M.bottomRightCorner<6,6>().diagonal().head<3>().setConstant(m);s.shared.M.bottomRightCorner<6,6>().diagonal().tail<3>().setConstant(I);std::ifstream in(argv[2]);unsigned size;in>>size;Eigen::VectorXd q(n),v(n);for(double&x:q)in>>x;for(double&x:v)in>>x;if(!in||size!=n)throw std::runtime_error("actual release state dimensions");EventControl control{.0001,.01,.02,.03,true};auto g=s.geometry(q);Eigen::LLT<Eigen::MatrixXd>factor(s.shared.M);auto force=s.force(q,control.sample(.0016).tension);Eigen::VectorXd acceleration=factor.solve(force.value-2*s.shared.M*v),normal=g.J*acceleration;for(unsigned i=0;i<3;++i)normal(i)+=v.dot(g.H[i]*v);Eigen::MatrixXd W=g.J*factor.solve(g.J.transpose());Eigen::VectorXd reaction=W.fullPivLu().solve(-normal);
 std::ofstream out(argv[3]);out<<std::setprecision(17)<<"row,free_normal_acceleration,bilateral_reaction_N\n";for(unsigned i=0;i<3;++i)out<<i<<','<<normal(i)<<','<<reaction(i)<<'\n';out.flush();std::cout<<std::setprecision(17)<<"free_normal_acceleration="<<normal.transpose()<<" bilateral_reaction="<<reaction.transpose()<<'\n';
 auto release=allRowRelease(s,q,v,.0016,.0001,control);auto dense=denseSurfacePath(s,q,v,release.state,.0001);
 // INSPECTION ONLY: distance >= R - existing gapTolerance is equivalent to
 // the existing g >= -1e-10 gate. Actual geometry/forces retain R30.01.
 auto violation=regrip_film_impact::earliestSurfaceEvent(dense.path,dense.triangles,{0,0,0},s.layout.bufferRadius-1e-10,1e-9,1e-12);if(violation)throw std::runtime_error("released numerical path crosses unchanged buffered gap gate");
 std::cout<<"PASS independently released saved actual deformation with whole numerical-path gate;NOT actual SOFA/tendon ungrasp/general release\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
