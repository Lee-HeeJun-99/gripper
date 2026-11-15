#include "../models/contact_kinematics/HermiteMap.h"
#include <iostream>
#include <iomanip>
using namespace regrip_curve;
double sparseError=0;
Mapped contact(const Pose&a,const Pose&b,const Pose&o,const regrip_history::History&history,int mode){auto p=point(a,b,.37,.6);Pose pp;for(int j=0;j<3;++j)pp.p[j]=p[j].v;auto leaf=regrip_birthlaw::evaluate(pp,o,history,V{0,1.3,.02},0,1,5,.2,1,1,mode==0?0.:mode==1?1.:.01);auto reference=pullback(p,leaf.wrench),fast=pullbackSparse(a,b,.37,.6,leaf.wrench);for(int i=0;i<18;++i)sparseError=std::max(sparseError,std::abs(fast.force[i]-reference.force[i]));for(int i=0;i<324;++i)sparseError=std::max(sparseError,std::abs(fast.jacobian[i]-reference.jacobian[i]));return fast;}
int main(){try{
 double fd=0,energyFD=0,objective=0,balance=0;
 for(int mode=0;mode<3;++mode)for(int sample=0;sample<20;++sample){Pose a,b,o;a.p={-.3,.9,.02};b.p={.3,.9,-.01};a.q=exp(V{.002*sample,.005*sample,-.004*sample});b.q=exp(V{-.003*sample,-.006*sample,.003*sample});regrip_history::History h;
  if(mode<2){auto p=point(a,b,.37,.6);for(int j=0;j<3;++j)h.local[j]=p[j].v;double n=std::sqrt(dot(h.local,h.local));h.normal=regrip_integrated::V{h.local[0]/n,h.local[1]/n,h.local[2]/n};h.elastic=cross(h.normal,V{.001,0,.002});h.active=true;}
  auto r=contact(a,b,o,h,mode);for(int k=0;k<18;++k){auto ap=a,am=a,bp=b,bm=b,op=o,om=o;if(k<6){ap=increment(a,k,1e-7);am=increment(a,k,-1e-7);}else if(k<12){bp=increment(b,k-6,1e-7);bm=increment(b,k-6,-1e-7);}else{op=increment(o,k-12,1e-7);om=increment(o,k-12,-1e-7);}auto plus=contact(ap,bp,op,h,mode),minus=contact(am,bm,om,h,mode);for(int j=0;j<18;++j)fd=std::max(fd,std::abs((plus.force[j]-minus.force[j])/2e-7-r.jacobian[18*j+k]));if(mode==0)energyFD=std::max(energyFD,std::abs((plus.energy-minus.energy)/2e-7+r.force[k]));}
  V F{},M{};for(int i=0;i<3;++i){auto pose=i==0?a:i==1?b:o;V f{r.force[6*i],r.force[6*i+1],r.force[6*i+2]},t{r.force[6*i+3],r.force[6*i+4],r.force[6*i+5]};F=add(F,f);M=add(M,add(t,cross(pose.p,f)));}for(double x:F)balance=std::max(balance,std::abs(x));for(double x:M)balance=std::max(balance,std::abs(x));
  auto R=exp(V{.8,-.4,1.1});auto transform=[&](Pose p){p.p=add(rotate(R,p.p),V{.3,-.5,.7});p.q=multiply(R,p.q);return p;};auto rr=contact(transform(a),transform(b),transform(o),h,mode);objective=std::max(objective,std::abs(rr.energy-r.energy));for(int i=0;i<6;++i){V f{r.force[3*i],r.force[3*i+1],r.force[3*i+2]};auto rotated=rotate(R,f);for(int j=0;j<3;++j)objective=std::max(objective,std::abs(rotated[j]-rr.force[3*i+j]));}
 }
 std::cout<<std::setprecision(17)<<"HERMITE {\"states\":60,\"jacobian_fd_error\":"<<fd<<",\"normal_energy_gradient_error\":"<<energyFD<<",\"objectivity_error\":"<<objective<<",\"force_moment_defect\":"<<balance<<"}\n";
 std::cout<<"SPARSE {\"maximum_reference_difference\":"<<sparseError<<"}\n";
 if(fd>1e-7||energyFD>1e-7||objective>1e-12||balance>1e-12||sparseError>1e-12)throw std::runtime_error("Hermite virtual-work/consistent tangent failed");
 return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
