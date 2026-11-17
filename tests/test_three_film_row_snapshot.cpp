#include "../models/film_three_finger/SharedFilmSystem.h"
#include <iostream>
using namespace regrip_three_finger;
int main(){try{
 SharedFilmSystem system(Layout(),Eigen::Vector3d(0,0,-.001),true,true);system.exactUnresolved=true;
 for(unsigned state=0;state<2;++state){auto q=system.initial;if(state){q(0)+=1e-8;q(3*system.shared.nf+2)-=1e-8;}std::array<Row,3>rows;auto plain=system.geometry(q),snapshot=system.geometry(q,&rows);
  if((plain.gap.array()!=snapshot.gap.array()).any()||(plain.J.array()!=snapshot.J.array()).any()||plain.J.norm()==0)throw std::runtime_error("global snapshot geometry changed");
  for(unsigned f=0;f<3;++f){auto again=system.selected(q,f);const auto&row=rows[f];if(row.triangle!=again.triangle||row.feature!=again.feature||row.gap!=again.gap||(row.gradient.array()!=again.gradient.array()).any()||(row.hessian.array()!=again.hessian.array()).any()||(plain.H[f].array()!=snapshot.H[f].array()).any()||(row.normal.array()!=again.normal.array()).any()||(row.contact.array()!=again.contact.array()).any())throw std::runtime_error("selected row snapshot differs from pure requery");}
 }
 std::cout<<"PASS exact geometry/J/H/feature/normal/point snapshots at two states;NOT time convergence or grasp\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
