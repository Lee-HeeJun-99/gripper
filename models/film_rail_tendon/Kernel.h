#pragma once
#include "../film_shell/PlaneContact.h"
#include <algorithm>
#include "../film_shell/PassiveProfile.h"
namespace regrip_film_rail {
using namespace regrip_film;
struct Part{unsigned offset,nx,ny;double width,thickness,y,z;};
struct Element{std::vector<unsigned>ids;AD energy;unsigned kind;double area=0,normal=0;};
// RECTANGULAR research coupon, not the tapered equal_volume_v2 geometry.
// All parts have independent Cartesian displacement DOFs. Rails are narrow
// finite-width film strips, not rigid edges or a widened centerline beam.
struct Assembly {
 unsigned nx;double L=100,W=24,skinT=.05,railT=.1,railW,E=250,nu=0;
 double bondK=1e-3,guideOffset=.2,plane=.1,kn=0;
 int contactSide=1;
 bool rootGuideSecondOrder=false; // Separate routing design: tangent consistent with quadratic root clamp.
 std::vector<Part>parts;
 explicit Assembly(unsigned nodes=21):nx(nodes){
  if(nodes<5||nodes>81||(nodes-1)%4)throw std::invalid_argument("assembly requires quarter-aligned21/41/81-style mesh");
  const double fingerVolume=439.3397917746089/3;
  railW=(fingerVolume-L*W*skinT)/(2*L*railT);
  if(railW<=0)throw std::invalid_argument("positive rail volume");
  parts={{0,nx,5,W,skinT,0,0},{5*nx,nx,3,railW,railT,0,-(skinT+railT)/2},{8*nx,nx,3,railW,railT,W-railW,-(skinT+railT)/2}};
 }
 unsigned size()const{return 11*nx;}
 unsigned id(unsigned part,unsigned i,unsigned j)const{const auto&p=parts.at(part);return p.offset+i*p.ny+j;}
 double volume()const{double v=0;for(const auto&p:parts)v+=L*p.width*p.thickness;return v;}
 std::vector<Point>rest()const{std::vector<Point>x(size());for(unsigned s=0;s<3;++s){const auto&p=parts[s];for(unsigned i=0;i<nx;++i)for(unsigned j=0;j<p.ny;++j)x[id(s,i,j)]={L*i/(nx-1),p.y+p.width*j/(p.ny-1),p.z};}return x;}
 std::vector<double>masses(double total=1e-6)const{std::vector<double>m(size());for(const auto&p:parts){double value=total*(L*p.width*p.thickness/volume())/(p.nx*p.ny);for(unsigned i=0;i<p.nx*p.ny;++i)m[p.offset+i]=value;}return m;}
 std::vector<unsigned>guideIds(unsigned part,unsigned i)const{auto ids=std::vector<unsigned>{id(part,i,0),id(part,i,2),id(part,i+1<nx?i+1:i-1,0)};if(rootGuideSecondOrder&&i==0)ids.push_back(id(part,2,0));return ids;}
 struct Local {
  std::vector<unsigned>ids;const std::vector<Point>&actual;
  Local(std::vector<unsigned>nodes,const std::vector<Point>&x):ids(std::move(nodes)),actual(x){std::sort(ids.begin(),ids.end());ids.erase(std::unique(ids.begin(),ids.end()),ids.end());if(ids.size()>9)throw std::invalid_argument("local AD27 support exceeded");}
  Vec<AD>point(unsigned id)const{auto it=std::lower_bound(ids.begin(),ids.end(),id);if(it==ids.end()||*it!=id)throw std::invalid_argument("local node");unsigned a=it-ids.begin();return {AD::variable(actual.at(id)[0],3*a),AD::variable(actual.at(id)[1],3*a+1),AD::variable(actual.at(id)[2],3*a+2)};}
 };
 Vec<AD>guide(const Local&local,unsigned part,unsigned i,double offset)const{
  auto a=local.point(id(part,i,0)),b=local.point(id(part,i,2)),c=local.point(id(part,i+1<nx?i+1:i-1,0));
  auto longitudinal=i+1<nx?sub(c,a):sub(a,c);if(rootGuideSecondOrder&&i==0)longitudinal=sub(add(scale(a,AD(-3)),scale(c,AD(4))),local.point(id(part,2,0)));auto normal=cross(longitudinal,sub(b,a));normal=scale(normal,inverse(root(dot(normal,normal))));
  return add(scale(add(a,b),AD(.5)),scale(normal,AD(offset)));
 }
 using Visitor=std::function<void(const Element&)>;
#ifdef REGRIP_FILM_DIRECT_VISITOR
 template<class Callback>
 void elements(const std::vector<Point>&u,double tension,Callback&&visit,const PassiveProfile*profile=nullptr)const{
#else
 void elements(const std::vector<Point>&u,double tension,const Visitor&visit,const PassiveProfile*profile=nullptr)const{
#endif
  if(u.size()!=size()||!std::isfinite(tension+bondK+guideOffset+kn)||tension<0||bondK<0||kn<0)throw std::invalid_argument("assembly parameters");
  auto actual=rest();for(unsigned i=0;i<size();++i)actual[i]=add(actual[i],u[i]);
  PassiveProfile disabled;const auto&cost=profile?*profile:disabled;
  {PassiveProfile::Scope timer(cost,"shell_AD_and_dispatch");for(const auto&p:parts){Film film(p.nx,p.ny,L,p.width,{E,nu,p.thickness});std::vector<Point>q(u.begin()+p.offset,u.begin()+p.offset+p.nx*p.ny);
   film.elements(q,[&](const auto&ids,const AD&e,bool){auto global=ids;for(auto&i:global)i+=p.offset;visit({global,e,0});},true,true);
  }
  }
  // Five physical attachment epochs per rail, fixed under mesh refinement.
  // Current rail normal carries the through-thickness attachment offset.
  // No fixed world-vector bond, full-sheet rigid tie or fictitious jamming.
  {PassiveProfile::Scope timer(cost,"attachment_AD_and_dispatch");for(unsigned part:{1u,2u})for(unsigned k=0;k<5;++k){unsigned i=(nx-1)*k/4;auto nodes=guideIds(part,i);
   unsigned ja=part==1?0:3,jb=ja+1;nodes.push_back(id(0,i,ja));nodes.push_back(id(0,i,jb));Local local(nodes,actual);
   double eta=part==1?(railW/2)/(W/4):1-(railW/2)/(W/4);
   auto skin=add(scale(local.point(id(0,i,ja)),AD(1-eta)),scale(local.point(id(0,i,jb)),AD(eta)));
   auto rail=guide(local,part,i,(skinT+railT)/2),gap=sub(skin,rail);
   visit({local.ids,AD(.5*bondK)*dot(gap,gap),1});
  }
  }
  // Actual eccentric routed path: five normal-offset guides per rail.
  // T*d(length)/dq generates endpoint AND guide forces/virtual moments.
  // T*length is a force generator, not stored cable elastic energy.
  {PassiveProfile::Scope timer(cost,"tendon_AD_and_dispatch");for(unsigned part:{1u,2u})for(unsigned k=0;k<4;++k){unsigned a=(nx-1)*k/4,b=(nx-1)*(k+1)/4;auto nodes=guideIds(part,a),next=guideIds(part,b);nodes.insert(nodes.end(),next.begin(),next.end());Local local(nodes,actual);
   auto d=sub(guide(local,part,b,-guideOffset),guide(local,part,a,-guideOffset));
   visit({local.ids,AD(tension)*(root(dot(d,d))-AD(L/4)),2});
  }
  }
  PassiveProfile::Scope contactTimer(cost,"contact_AD_and_dispatch");if(kn>0)for(unsigned i=0;i<nx-1;++i)for(unsigned j=0;j<4;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{id(0,i+1,j+1),id(0,i,j+1),id(0,i+1,j)}:std::vector<unsigned>{id(0,i,j),id(0,i+1,j),id(0,i,j+1)};std::array<AD,3>gap;for(unsigned a=0;a<3;++a)gap[a]=AD::variable(actual[ids[a]][2]-plane,3*a+2);visit({ids,planeContact(gap,.5*L*W/((nx-1)*4),kn).energy,3});}
 }
 double energy(const std::vector<Point>&u,double tension)const{double value=0;elements(u,tension,[&](const Element&e){value+=e.energy.v;});return value;}
 double cableLength(const std::vector<Point>&u)const{auto actual=rest();for(unsigned i=0;i<size();++i)actual[i]=add(actual[i],u[i]);double length=0;for(unsigned part:{1u,2u})for(unsigned k=0;k<4;++k){unsigned a=(nx-1)*k/4,b=(nx-1)*(k+1)/4;auto ids=guideIds(part,a),next=guideIds(part,b);ids.insert(ids.end(),next.begin(),next.end());Local local(ids,actual);auto d=sub(guide(local,part,b,-guideOffset),guide(local,part,a,-guideOffset));length+=root(dot(d,d)).v;}return length;}
};
}
