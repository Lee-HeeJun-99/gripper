#pragma once
#include "FrameLayout.h"
#include "PreciseDistanceOrder.h"
#include "../film_coupled_collocation/PersistentRows.h"
namespace regrip_three_finger {
// Independent nonlinear FEM adapter. Three material frames,ONE free sphere.
// Only a fixed three-row branch;NOT yet a SOFA owner or active-set gripper.
struct SharedFilmSystem {
 Layout layout;
 SharedPointSystem shared;
 std::array<unsigned,3>owned,features;
 Eigen::VectorXd initial;
 Eigen::Vector3d external;
 bool rescanClosest,preciseTies;
 bool exactUnresolved=false;
 mutable unsigned exactFallbackCalls=0;
 const regrip_film::PassiveProfile*meter=nullptr;
 const regrip_film::PassiveProfile&cost()const{static const regrip_film::PassiveProfile disabled;return meter?*meter:disabled;}
 int order(const TriangleCoordinates&a,const TriangleCoordinates&b)const{
  try{return preciseOrder(a,b);}catch(const UnresolvedDistanceOrder&){
   if(!exactUnresolved)throw;
   ++exactFallbackCalls;cost().count("rational_distance_fallback");return rationalOrder(a,b);
  }
 }
 // Optional passive failed-query observation;never changes the returned law.
 std::function<void(const Eigen::VectorXd&,unsigned,const Row&,const Row&)> ambiguityObserver;
 SharedFilmSystem(Layout geometry=Layout(),Eigen::Vector3d bodyForce={0,0,0},bool rescan=false,bool precise=false,const regrip_film::PassiveProfile*profile=nullptr)
  :layout(geometry),shared(sharedPointReference(layout)),external(bodyForce),rescanClosest(rescan),preciseTies(precise),meter(profile){
  regrip_film::PassiveProfile::Scope timer(cost(),"constructor_row_search");
  initial=Eigen::VectorXd::Zero(shared.M.rows());initial.segment<3>(3*shared.nf)=layout.bodyCenter;
  for(unsigned f=0;f<3;++f){double minimum=std::numeric_limits<double>::infinity();auto state=local(initial,f);for(unsigned k=0;k<shared.films[f].triangles.size();++k){cost().count("constructor_candidate_AD");double gap=shared.films[f].primitive(state,k).gap.v;if(gap<minimum){minimum=gap;owned[f]=k;}}features[f]=shared.films[f].geometry(state,owned[f]).feature;}
 }
 Row selected(const Eigen::VectorXd&x,unsigned f)const{
  regrip_film::PassiveProfile::Scope timer(cost(),"selected_geometry");
  auto state=local(x,f);const auto&s=shared.films[f];
  if(!rescanClosest){auto row=s.geometry(state,owned[f]);if(row.feature!=features[f])throw std::domain_error("three-film owned feature changed;active-set not implemented");return row;}
  // Explicit new selector:whole surface at EVERY query,not a predictor's row.
  unsigned id=0;double minimum=std::numeric_limits<double>::infinity();
  std::vector<double>gaps(s.triangles.size());
  for(unsigned k=0;k<s.triangles.size();++k){cost().count("candidate_AD");gaps[k]=s.primitive(state,k).gap.v;if(gaps[k]<minimum){minimum=gaps[k];id=k;}}
  std::vector<TriangleCoordinates>exact;
  if(preciseTies){auto rest=s.film.model.rest();exact.resize(s.triangles.size());for(unsigned k=0;k<exact.size();++k)for(unsigned a=0;a<3;++a){unsigned node=s.triangles[k][a];exact[k][a]=sub(add(rest[node],state.q[node]),point(state.body.center));}id=0;for(unsigned k=1;k<exact.size();++k)if(order(exact[k],exact[id])<0)id=k;minimum=gaps[id];}
  auto row=s.geometry(state,id);
  // Shared-edge/vertex duplicates are allowed ONLY for the same generalized
  // normal. Independent tied supports need MORE rows,not an arbitrary winner.
  for(unsigned k=0;k<gaps.size();++k)if(k!=id&&std::abs(gaps[k]-minimum)<=1e-12){auto other=s.geometry(state,k);if((other.gradient-row.gradient).norm()>1e-10&&(!preciseTies||order(exact[k],exact[id])==0)){if(ambiguityObserver)ambiguityObserver(x,f,row,other);throw std::domain_error("ambiguous independent closest supports;three-row branch insufficient");}}
  return row;
 }
 State local(const Eigen::VectorXd&x,unsigned f)const{
  const auto&s=shared.films[f];State state=s.before;state.q=s.film.expand(x.segment(f*shared.nf,shared.nf));state.body.center=layout.mount[f].R.transpose()*(x.segment<3>(3*shared.nf)-layout.mount[f].origin);return state;
 }
 regrip_collocation::Force force(const Eigen::VectorXd&x,double tension)const{
  regrip_film::PassiveProfile::Scope timer(cost(),"shared_material_force_Hessian");
  const unsigned nf=shared.nf,n=shared.M.rows();regrip_collocation::Force out{Eigen::VectorXd::Zero(n),Eigen::MatrixXd::Zero(n,n)};out.value.segment<3>(3*nf)=external;
  for(unsigned f=0;f<3;++f){const auto&s=shared.films[f];auto state=local(x,f);
   s.film.model.elements(state.q,tension,[&](const Element&e){cost().count("material_AD_dispatch");regrip_film::PassiveProfile::Scope pullback(cost(),"element_pullback");for(unsigned a=0;a<3*e.ids.size();++a){unsigned ga=3*e.ids[a/3]+a%3;int i=s.film.index[ga];if(i<0)continue;out.value(f*nf+i)-=s.film.weight[ga]*e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b){unsigned gb=3*e.ids[b/3]+b%3;int j=s.film.index[gb];if(j>=0)out.negativeTangent(f*nf+i,f*nf+j)+=s.film.weight[ga]*s.film.weight[gb]*e.energy.h[N*a+b];}}},meter);
  }return out;
 }
 regrip_collocation::RowGeometry geometry(const Eigen::VectorXd&x,std::array<Row,3>*snapshot=nullptr)const{
  regrip_film::PassiveProfile::Scope timer(cost(),"shared_geometry_and_pullback");
  const unsigned nf=shared.nf,n=shared.M.rows(),body=3*nf;regrip_collocation::RowGeometry out{Eigen::VectorXd(3),Eigen::MatrixXd::Zero(3,n),std::vector<Eigen::MatrixXd>(3,Eigen::MatrixXd::Zero(n,n))};
  for(unsigned f=0;f<3;++f){auto row=selected(x,f);
   // Isotropic spherical normal force has EXACT zero rotational block.
   if(row.gradient.tail<3>().norm()!=0||row.hessian.bottomRows(3).norm()!=0||row.hessian.rightCols(3).norm()!=0)throw std::domain_error("unexpected spherical rotational contact coupling");
   const auto&R=layout.mount[f].R;out.gap(f)=row.gap;out.J.block(f,f*nf,1,nf)=row.gradient.head(nf).transpose();out.J.block<1,3>(f,body)=row.gradient.segment<3>(nf).transpose()*R.transpose();auto&H=out.H[f];H.block(f*nf,f*nf,nf,nf)=row.hessian.topLeftCorner(nf,nf);H.block(f*nf,body,nf,3)=row.hessian.block(0,nf,nf,3)*R.transpose();H.block(body,f*nf,3,nf)=R*row.hessian.block(nf,0,3,nf);H.block<3,3>(body,body)=R*row.hessian.block<3,3>(nf,nf)*R.transpose();
   if(snapshot)(*snapshot)[f]=std::move(row);
  }return out;
 }
 double clearance(const Eigen::VectorXd&x)const{double gap=std::numeric_limits<double>::infinity();for(unsigned f=0;f<3;++f){auto state=local(x,f);for(unsigned k=0;k<shared.films[f].triangles.size();++k)gap=std::min(gap,shared.films[f].primitive(state,k).gap.v);}return gap;}
};
}
