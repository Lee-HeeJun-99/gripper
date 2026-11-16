#pragma once
#include "AD.h"
#include "MembraneAD.h"
#include <vector>
#include <functional>
namespace regrip_film {
using Point=Vec<double>;
struct Properties{double E=250,nu=.3,t=.1;void validate()const{if(!std::isfinite(E+nu+t)||E<=0||t<=0||nu<=-1||nu>=.5)throw std::invalid_argument("film E/nu/t");}double D()const{return E*t*t*t/(12*(1-nu*nu));}};
// Independent structured flat-reference Koiter-like ROM. Membrane uses linear
// triangles/Green strain. Bending uses second material-coordinate differences,
// current unit normal and nodal trapezoid integration. NOT general curved-rest
// shell FEM, laminated friction, through-thickness stress or self-contact.
struct Film {
 unsigned nx,ny;double L,W;Properties material;
 Film(unsigned x,unsigned y,double l,double w,Properties m):nx(x),ny(y),L(l),W(w),material(m){m.validate();if(nx<3||ny<3||nx>101||ny>41||L<=0||W<=0||!std::isfinite(L+W))throw std::invalid_argument("bounded rectangular film grid");}
 unsigned id(unsigned i,unsigned j)const{return i*ny+j;}
 std::vector<Point>rest()const{std::vector<Point>x(nx*ny);for(unsigned i=0;i<nx;++i)for(unsigned j=0;j<ny;++j)x[id(i,j)]={L*i/(nx-1),W*j/(ny-1),0};return x;}
 using Visitor=std::function<void(const std::vector<unsigned>&,const AD&,bool)>;
#ifdef REGRIP_FILM_DIRECT_VISITOR
 template<class Callback>
 void elements(const std::vector<Point>&x,Callback&&visit,bool displacement=false,bool compactMembrane=false)const{
#else
 void elements(const std::vector<Point>&x,const Visitor&visit,bool displacement=false,bool compactMembrane=false)const{
#endif
  material.validate();if(x.size()!=nx*ny)throw std::invalid_argument("film state size");for(auto&p:x)for(auto v:p)if(!std::isfinite(v))throw std::invalid_argument("finite film positions");
  double dx=L/(nx-1),dy=W/(ny-1),lambda=material.E*material.nu/(1-material.nu*material.nu),mu=material.E/(2*(1+material.nu));
#ifdef REGRIP_FILM_REUSE_LIFT
  std::vector<Vec<AD>>workspace;workspace.reserve(9);
  auto lift=[&](const std::vector<unsigned>&ids)->const std::vector<Vec<AD>>&{workspace.resize(ids.size());auto&p=workspace;for(unsigned a=0;a<ids.size();++a)for(int j=0;j<3;++j){double ref=j==0?dx*(ids[a]/ny):j==1?dy*(ids[a]%ny):0;p[a][j]=AD::variable(x[ids[a]][j]-(displacement?0:ref),3*a+j);}return p;};
#else
  auto lift=[&](const std::vector<unsigned>&ids){std::vector<Vec<AD>>p(ids.size());for(unsigned a=0;a<ids.size();++a)for(int j=0;j<3;++j){double ref=j==0?dx*(ids[a]/ny):j==1?dy*(ids[a]%ny):0;p[a][j]=AD::variable(x[ids[a]][j]-(displacement?0:ref),3*a+j);}return p;};
#endif
  for(unsigned i=0;i<nx-1;++i)for(unsigned j=0;j<ny-1;++j)for(unsigned side=0;side<2;++side){
   std::vector<unsigned>ids=side?std::vector<unsigned>{id(i+1,j+1),id(i,j+1),id(i+1,j)}:std::vector<unsigned>{id(i,j),id(i+1,j),id(i,j+1)};
   if(compactMembrane){std::array<Point,3>u;for(int a=0;a<3;++a)for(int j=0;j<3;++j){double ref=j==0?dx*(ids[a]/ny):j==1?dy*(ids[a]%ny):0;u[a][j]=x[ids[a]][j]-(displacement?0:ref);}visit(ids,compact::triangle(u,side?-1:1,dx,dy,material.t,lambda,mu),false);continue;}
   const auto&p=lift(ids);double sign=side?-1:1;auto a=scale(sub(p[1],p[0]),AD(sign/dx)),b=scale(sub(p[2],p[0]),AD(sign/dy));
   // F=I+grad(u). This is algebraically identical Green strain without
   // subtracting nearly equal squared lengths. No force/tolerance correction.
   AD ex=a[0]+AD(.5)*dot(a,a),ey=b[1]+AD(.5)*dot(b,b),g=AD(.5)*(a[1]+b[0]+dot(a,b)),tr=ex+ey;
   AD energy=AD(.5*dx*dy*material.t)*(AD(.5*lambda)*tr*tr+AD(mu)*(ex*ex+ey*ey+AD(2)*g*g));visit(ids,energy,false);
  }
  auto weights=[](unsigned index,unsigned count,double h){std::array<double,3>f{};if(index==0)f={-1.5/h,2/h,-.5/h};else if(index==count-1)f={.5/h,-2/h,1.5/h};else f={-.5/h,0,.5/h};return f;};
  for(unsigned i=0;i<nx;++i)for(unsigned j=0;j<ny;++j){unsigned si=i==0?0:i==nx-1?nx-3:i-1,sj=j==0?0:j==ny-1?ny-3:j-1;
   std::vector<unsigned>ids;for(unsigned a=0;a<3;++a)for(unsigned b=0;b<3;++b)ids.push_back(id(si+a,sj+b));const auto&p=lift(ids);
   auto wx=weights(i,nx,dx),wy=weights(j,ny,dy);unsigned ci=i-si,cj=j-sj;
   Vec<AD>a{},b{},xx{},yy{},xy{};double second[3]={1,-2,1};
   for(unsigned u=0;u<3;++u){a=add(a,scale(p[3*u+cj],AD(wx[u])));b=add(b,scale(p[3*ci+u],AD(wy[u])));xx=add(xx,scale(p[3*u+cj],AD(second[u]/(dx*dx))));yy=add(yy,scale(p[3*ci+u],AD(second[u]/(dy*dy))));for(unsigned v=0;v<3;++v)xy=add(xy,scale(p[3*u+v],AD(wx[u]*wy[v])));}
   a[0]=a[0]+AD(1);b[1]=b[1]+AD(1);auto normal=cross(a,b);normal=scale(normal,inverse(root(dot(normal,normal))));auto kx=dot(normal,xx),ky=dot(normal,yy),kxy=dot(normal,xy);
   double area=dx*dy*(i==0||i==nx-1?.5:1)*(j==0||j==ny-1?.5:1);
   AD energy=AD(.5*material.D()*area)*(kx*kx+ky*ky+AD(2*material.nu)*kx*ky+AD(2*(1-material.nu))*kxy*kxy);visit(ids,energy,true);
  }
 }
 double energy(const std::vector<Point>&x)const{double e=0;elements(x,[&](const auto&,const AD&a,bool){e+=a.v;});return e;}
};
}
