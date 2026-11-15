#pragma once
#include "../contact_birth/BirthLaw.h"
namespace regrip_curve {
using namespace regrip_integrated;
// Candidate director-Hermite kinematics, NOT yet a SOFA contact component.
// Reference tangents have length L; axial-strain interpolation is a model
// assumption to validate independently before replacing the linear centerline.
inline Vec<Jet> point(const Pose&a,const Pose&b,double s,double L){
 validate(a);validate(b);if(!std::isfinite(s)||s<0||s>1||!std::isfinite(L)||L<=0)throw std::invalid_argument("Hermite coordinate/reference length");
 double h0=2*s*s*s-3*s*s+1,h1=-2*s*s*s+3*s*s,t0=s*s*s-2*s*s+s,t1=s*s*s-s*s;
 auto d0=lifted(rotate(a.q,V{1,0,0}),3),d1=lifted(rotate(b.q,V{1,0,0}),9);Vec<Jet>p;
 for(int j=0;j<3;++j)p[j]=Jet(h0)*(Jet(a.p[j])+Jet::variable(j))+Jet(h1)*(Jet(b.p[j])+Jet::variable(6+j))+Jet(L*t0)*d0[j]+Jet(L*t1)*d1[j];
 return p;
}
struct Mapped{std::array<double,18>force{};std::array<double,324>jacobian{};double energy=0;};
inline Mapped pullback(const Vec<Jet>&p,const Result&leaf){
 Mapped r;r.energy=leaf.energy;double B[12][18]{};
 for(int k=0;k<3;++k)for(int j=0;j<12;++j)B[k][j]=p[k].g[j];
 for(int k=6;k<12;++k)B[k][12+k-6]=1;
 for(int i=0;i<18;++i){for(int a=0;a<12;++a)r.force[i]+=B[a][i]*leaf.force[a];for(int j=0;j<18;++j)for(int a=0;a<12;++a)if(B[a][i])for(int b=0;b<12;++b)r.jacobian[18*i+j]+=B[a][i]*leaf.jacobian[12*a+b]*B[b][j];}
 for(int i=0;i<12;++i)for(int j=0;j<12;++j)for(int k=0;k<3;++k)r.jacobian[18*i+j]+=leaf.force[k]*p[k].h[12*i+j];
 // Symmetric chart derivative of G is NOT the spatial torque derivative.
 // The left-SO(3) connection gives -half skew(torque) on both nodal blocks.
 for(int offset:{3,9}){double x=r.force[offset],y=r.force[offset+1],z=r.force[offset+2],S[9]={0,-z,y,z,0,-x,-y,x,0};for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.jacobian[18*(offset+i)+offset+j]-=.5*S[3*i+j];}
 return r;
}
// Sparse analytic equivalent of the AD2 pullback above. The geometric term
// differentiates spatial arm x force, not a symmetric rotation-chart Hessian.
inline Mapped pullbackSparse(const Pose&a,const Pose&b,double s,double L,const Result&leaf){
 (void)point(a,b,s,L); // retain the reference implementation's input contract
 double h0=2*s*s*s-3*s*s+1,h1=1-h0,t0=L*(s*s*s-2*s*s+s),t1=L*(s*s*s-s*s);
 V arm0=rotate(a.q,V{t0,0,0}),arm1=rotate(b.q,V{t1,0,0});
 double B[12][18]{};
 for(int k=0;k<3;++k){B[k][k]=h0;B[k][6+k]=h1;B[6+k][12+k]=1;B[9+k][15+k]=1;}
 for(int j=0;j<3;++j){V axis{};axis[j]=1;auto u=cross(axis,arm0),v=cross(axis,arm1);for(int k=0;k<3;++k){B[k][3+j]=u[k];B[k][9+j]=v[k];}}
 Mapped r;r.energy=leaf.energy;
 double JB[12][18]{};
 for(int u:{0,1,2,6,7,8,9,10,11})for(int v:{0,1,2,6,7,8,9,10,11})for(int j=0;j<18;++j)if(B[v][j])JB[u][j]+=leaf.jacobian[12*u+v]*B[v][j];
 for(int i=0;i<18;++i)for(int u:{0,1,2,6,7,8,9,10,11})if(B[u][i]){r.force[i]+=B[u][i]*leaf.force[u];for(int j=0;j<18;++j)r.jacobian[18*i+j]+=B[u][i]*JB[u][j];}
 V f{leaf.force[0],leaf.force[1],leaf.force[2]};
 for(int block=0;block<2;++block){auto arm=block?arm1:arm0;int offset=block?9:3;double af=dot(arm,f);for(int i=0;i<3;++i)for(int j=0;j<3;++j)r.jacobian[18*(offset+i)+offset+j]+=arm[i]*f[j]-(i==j?af:0);}
 return r;
}
}
