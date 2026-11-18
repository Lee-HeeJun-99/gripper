#pragma once
#include "../film_three_finger/SharedFilmSystem.h"
namespace regrip_three_resume {
using namespace regrip_three_finger;
struct ContactOwner {unsigned finger,triangle,feature;};
// Same virtual-work pullback as SharedFilmSystem,arbitrary independently owned
// rows. No min-distance row replacement inside a persistent material branch.
inline regrip_collocation::RowGeometry ownedGeometry(const SharedFilmSystem&s,
 const Eigen::VectorXd&q,const std::vector<ContactOwner>&owners){
 const unsigned nf=s.shared.nf,n=q.size(),body=3*nf,m=owners.size();regrip_collocation::RowGeometry g{Eigen::VectorXd(m),Eigen::MatrixXd::Zero(m,n),std::vector<Eigen::MatrixXd>(m,Eigen::MatrixXd::Zero(n,n))};
 for(unsigned k=0;k<m;++k){const auto&o=owners[k];if(o.finger>=3)throw std::runtime_error("invalid row owner finger");auto row=s.shared.films[o.finger].geometry(s.local(q,o.finger),o.triangle);if(row.feature!=o.feature)throw std::runtime_error("owned feature transition:separate event required");if(row.gradient.tail<3>().norm()!=0||row.hessian.bottomRows(3).norm()!=0||row.hessian.rightCols(3).norm()!=0)throw std::runtime_error("sphere torque pullback invalid");const auto&R=s.layout.mount[o.finger].R;unsigned begin=o.finger*nf;g.gap(k)=row.gap;g.J.block(k,begin,1,nf)=row.gradient.head(nf).transpose();g.J.block<1,3>(k,body)=row.gradient.segment<3>(nf).transpose()*R.transpose();auto&H=g.H[k];H.block(begin,begin,nf,nf)=row.hessian.topLeftCorner(nf,nf);H.block(begin,body,nf,3)=row.hessian.block(0,nf,nf,3)*R.transpose();H.block(body,begin,3,nf)=R*row.hessian.block(nf,0,3,nf);H.block<3,3>(body,body)=R*row.hessian.block<3,3>(nf,nf)*R.transpose();}
 return g;
}
}
