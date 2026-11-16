#pragma once
#include "Kernel.h"
namespace regrip_film {
// Exact reference-area integration of quadratic unilateral plane penalty on a
// linear triangle. Plane is an explicitly EXTERNALLY FIXED frictionless stop.
// It is not a freely moving object, Coulomb contact, pressure film or grasp.
struct PlaneResult{AD energy,area,normalForce;};
inline PlaneResult planeContact(const std::array<AD,3>&gap,double referenceArea,double kn){
 if(referenceArea<=0||kn<0)throw std::invalid_argument("plane area/stiffness");
 struct Vertex{AD u,v,g;};std::vector<Vertex>polygon{{AD(0),AD(0),gap[0]},{AD(1),AD(0),gap[1]},{AD(0),AD(1),gap[2]}},clipped;
 for(unsigned i=0;i<polygon.size();++i){auto a=polygon[i],b=polygon[(i+1)%polygon.size()];bool inA=a.g.v>0,inB=b.g.v>0;if(inA)clipped.push_back(a);if(inA!=inB){auto alpha=a.g*inverse(a.g-b.g);clipped.push_back({a.u+alpha*(b.u-a.u),a.v+alpha*(b.v-a.v),AD(0)});}}
 PlaneResult r;if(clipped.size()<3)return r;
 for(unsigned i=1;i+1<clipped.size();++i){auto a=clipped[0],b=clipped[i],c=clipped[i+1];AD fraction=(b.u-a.u)*(c.v-a.v)-(c.u-a.u)*(b.v-a.v),area=AD(referenceArea)*fraction;
  if(area.v<0)throw std::domain_error("inverted reference clipping polygon");
  r.area=r.area+area;r.normalForce=r.normalForce+AD(kn/3)*area*(a.g+b.g+c.g);
  r.energy=r.energy+AD(kn/12)*area*(a.g*a.g+b.g*b.g+c.g*c.g+a.g*b.g+b.g*c.g+c.g*a.g);
 }return r;
}
}
