#pragma once
#include "../contact_kinematics/HermiteMap.h"
namespace regrip_curved {
using namespace regrip_integrated;
using regrip_history::scale;
inline void validateMap(const Pose&a,const Pose&b,double s,double L){validate(a);validate(b);if(!std::isfinite(s)||s<0||s>1||!std::isfinite(L)||L<=0)throw std::invalid_argument("curved material coordinate");}
inline V position(const Pose&a,const Pose&b,double s,double L){
 validateMap(a,b,s,L);double h0=2*s*s*s-3*s*s+1,h1=1-h0,t0=L*(s*s*s-2*s*s+s),t1=L*(s*s*s-s*s);
 return add(add(scale(a.p,h0),scale(b.p,h1)),add(rotate(a.q,V{t0,0,0}),rotate(b.q,V{t1,0,0})));
}
// Uniform rigorous bound of curve minus chord, using |h10|,|h11|<=4/27.
inline double sagBound(const Pose&a,const Pose&b,double L){
 auto chord=scale(sub(b.p,a.p),1/L),u=sub(rotate(a.q,V{1,0,0}),chord),v=sub(rotate(b.q,V{1,0,0}),chord);
 return L*(4./27)*(std::sqrt(dot(u,u))+std::sqrt(dot(v,v)));
}
inline regrip_curve::Mapped map(const Pose&a,const Pose&b,double s,double L,const Result&leaf){
 validateMap(a,b,s,L);double h0=2*s*s*s-3*s*s+1,h1=1-h0;
 V arms[2]={rotate(a.q,V{L*(s*s*s-2*s*s+s),0,0}),rotate(b.q,V{L*(s*s*s-s*s),0,0})};
 double B[9][18]{};int leafIds[9]={0,1,2,6,7,8,9,10,11};
 for(int k=0;k<3;++k){B[k][k]=h0;B[k][6+k]=h1;B[3+k][12+k]=1;B[6+k][15+k]=1;}
 for(int j=0;j<3;++j){V e{};e[j]=1;for(int n=0;n<2;++n){auto v=cross(e,arms[n]);for(int k=0;k<3;++k)B[k][6*n+3+j]=v[k];}}
 double JB[9][18]{};regrip_curve::Mapped out;out.energy=leaf.energy;
 for(int u=0;u<9;++u)for(int v=0;v<9;++v){double j=leaf.jacobian[12*leafIds[u]+leafIds[v]];if(j)for(int k=0;k<18;++k)if(B[v][k])JB[u][k]+=j*B[v][k];}
 for(int i=0;i<18;++i)for(int u=0;u<9;++u)if(B[u][i]){out.force[i]+=B[u][i]*leaf.force[leafIds[u]];for(int j=0;j<18;++j)out.jacobian[18*i+j]+=B[u][i]*JB[u][j];}
 V f{leaf.force[0],leaf.force[1],leaf.force[2]};
 for(int n=0;n<2;++n){int off=6*n+3;double af=dot(arms[n],f);for(int i=0;i<3;++i)for(int j=0;j<3;++j)out.jacobian[18*(off+i)+off+j]+=arms[n][i]*f[j]-(i==j?af:0);}
 return out;
}
inline std::array<double,18> force(const Pose&a,const Pose&b,double s,double L,const Result&leaf){
 double h=2*s*s*s-3*s*s+1;V f{leaf.force[0],leaf.force[1],leaf.force[2]},a0=rotate(a.q,V{L*(s*s*s-2*s*s+s),0,0}),a1=rotate(b.q,V{L*(s*s*s-s*s),0,0}),t0=cross(a0,f),t1=cross(a1,f);std::array<double,18>r{};
 for(int j=0;j<3;++j){r[j]=h*f[j];r[j+6]=(1-h)*f[j];r[j+3]=t0[j];r[j+9]=t1[j];r[j+12]=leaf.force[j+6];r[j+15]=leaf.force[j+9];}return r;
}
}
