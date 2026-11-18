#pragma once
#include "ContactRows.h"
namespace regrip_three_resume {
struct FaceBranchValue {regrip_film_sphere::ClosestPrimitive::Evaluation geometry;std::array<double,3>barycentric;};
// Analytic continuation of the EXISTING feature6 expression. Outside-face
// values are ONLY root-bracketing diagnostics,never accepted physical contact.
inline FaceBranchValue faceBranch(const std::vector<Point>&positions,double radius){
 if(positions.size()!=3)throw std::runtime_error("face branch requires triangle");std::vector<Vec<AD>>x;for(unsigned i=0;i<3;++i)x.push_back({AD::variable(positions[i][0],3*i),AD::variable(positions[i][1],3*i+1),AD::variable(positions[i][2],3*i+2)});Vec<AD>c{AD(0),AD(0),AD(0)};auto ab=sub(x[1],x[0]),ac=sub(x[2],x[0]),normal=cross(ab,ac);if(!(dot(normal,normal).v>0))throw std::runtime_error("degenerate face continuation");auto ap=sub(c,x[0]);auto d1=dot(ab,ap),d2=dot(ac,ap);auto bp=sub(c,x[1]);auto d3=dot(ab,bp),d4=dot(ac,bp);auto vc=d1*d4-d3*d2;auto cp=sub(c,x[2]);auto d5=dot(ab,cp),d6=dot(ac,cp);auto vb=d5*d2-d1*d6;auto va=d3*d6-d5*d4;auto den=va+vb+vc;if(!(den.v>0))throw std::runtime_error("invalid face denominator;no regularization");auto ratio=[](const AD&a,const AD&b){return a*inverse(b);};auto p=add(x[0],add(scale(ab,ratio(vb,den)),scale(ac,ratio(vc,den))));if(!(dot(p,p).v>0))throw std::runtime_error("undefined face normal");return {{root(dot(p,p))-AD(radius),p,6},{va.v/den.v,vb.v/den.v,vc.v/den.v}};
}
inline std::vector<Point>relativeTriangle(const SharedFilmSystem&s,const Eigen::VectorXd&q,const ContactOwner&o){auto state=s.local(q,o.finger);const auto&sys=s.shared.films[o.finger];auto rest=sys.film.model.rest();std::vector<Point>x;for(unsigned node:sys.triangles[o.triangle])x.push_back(sub(add(rest[node],state.q[node]),point(state.body.center)));return x;}
inline regrip_collocation::RowGeometry faceBranchGeometry(const SharedFilmSystem&s,
 const Eigen::VectorXd&q,const std::vector<ContactOwner>&owners){
 const unsigned n=q.size(),nf=s.shared.nf,nb=3*nf;regrip_collocation::RowGeometry out{Eigen::VectorXd(owners.size()),Eigen::MatrixXd::Zero(owners.size(),n),std::vector<Eigen::MatrixXd>(owners.size(),Eigen::MatrixXd::Zero(n,n))};
 for(unsigned k=0;k<owners.size();++k){const auto&o=owners[k];const auto&sys=s.shared.films[o.finger];auto e=faceBranch(relativeTriangle(s,q,o),s.layout.bufferRadius);Eigen::MatrixXd D=Eigen::MatrixXd::Zero(9,n);const auto&tri=sys.triangles[o.triangle];for(unsigned a=0;a<9;++a){unsigned ga=3*tri[a/3]+a%3;int id=sys.film.index[ga];if(id>=0)D(a,o.finger*nf+id)=sys.film.weight[ga];for(unsigned d=0;d<3;++d)D(a,nb+d)=-s.layout.mount[o.finger].R(d,a%3);}Eigen::VectorXd gradient(9);Eigen::MatrixXd H(9,9);for(unsigned a=0;a<9;++a){gradient(a)=e.geometry.gap.g[a];for(unsigned b=0;b<9;++b)H(a,b)=e.geometry.gap.h[regrip_film::N*a+b];}out.gap(k)=e.geometry.gap.v;out.J.row(k)=gradient.transpose()*D;out.H[k]=D.transpose()*H*D;
 }return out;
}
inline double minimumFaceParameter(const SharedFilmSystem&s,const Eigen::VectorXd&q,const std::vector<ContactOwner>&owners){double b=1;for(const auto&o:owners){auto e=faceBranch(relativeTriangle(s,q,o),s.layout.bufferRadius);for(double value:e.barycentric)b=std::min(b,value);}return b;}
}
