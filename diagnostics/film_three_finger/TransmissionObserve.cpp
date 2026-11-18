#include "../../models/film_transmission/Kernel.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_transmission;
struct Observation{double skin=0,rails=0,bond=0,K=0,attachmentSkin=0,attachmentRails=0,tendon=0,unitPower=0,forceBalance=0,momentBalance=0;};
inline Observation observe(const Assembly&m,const std::vector<double>&mass,const std::vector<Point>&q,const std::vector<Point>&v){
 Observation out;auto rest=m.rest();std::vector<Point>bond(m.size()),cable(m.size());m.elements(q,1.,[&](const Element&e){if(e.kind==0){if(e.ids.front()<105)out.skin+=e.energy.v;else out.rails+=e.energy.v;}else if(e.kind==1)out.bond+=e.energy.v;else if(e.kind!=2)throw std::runtime_error("unexpected coupon physical term");if(e.kind==1||e.kind==2)for(unsigned a=0;a<3*e.ids.size();++a)(e.kind==1?bond:cable)[e.ids[a/3]][a%3]-=e.energy.g[a];});
 Point sum{},moment{};double bs=0,br=0,ct=0;for(unsigned i=0;i<q.size();++i){if(i<105)bs+=dot(bond[i],bond[i]);else br+=dot(bond[i],bond[i]);ct+=dot(cable[i],cable[i]);sum=add(sum,bond[i]);moment=add(moment,cross(add(rest[i],q[i]),bond[i]));out.K+=.5*mass[i]*dot(v[i],v[i]);out.unitPower+=dot(cable[i],v[i]);}out.attachmentSkin=std::sqrt(bs);out.attachmentRails=std::sqrt(br);out.tendon=std::sqrt(ct);out.forceBalance=std::sqrt(dot(sum,sum));out.momentBalance=std::sqrt(dot(moment,moment));return out;
}
int main(int argc,char**argv){try{
 if(argc!=6)throw std::runtime_error("bond,offset,mass,samples,output required");auto m=model(std::stod(argv[1]),std::stod(argv[2]));auto mass=publicMass(argv[3]);std::ifstream in(argv[4]);unsigned samples;in>>samples;if(samples>2000||samples<1)throw std::runtime_error("bounded actual sample count");std::vector<Point>previous(m.size()),previousV(m.size());double W=0;std::ofstream out(argv[5]);out<<std::setprecision(17)<<"time,U_skin,U_rails,U_attachment,K,attachment_skin_force_norm_N,attachment_rail_force_norm_N,tendon_force_norm_N,cable_length_mm,midpoint_tendon_work_Nmm,midpoint_damping_work_Nmm,attachment_force_balance_N,attachment_moment_balance_Nmm\n";double damp=0;
 for(unsigned k=0;k<samples;++k){double time,h,Tmid,Tend;in>>time>>h>>Tmid>>Tend;std::vector<Point>q(m.size()),v(q.size()),middle(q.size()),mv(q.size());for(auto&x:q)for(double&y:x)in>>y;for(auto&x:v)for(double&y:x)in>>y;if(!in||Tmid<0||Tend<0||h<=0)throw std::runtime_error("invalid actual sample");for(unsigned i=0;i<q.size();++i){middle[i]=scale(add(q[i],previous[i]),.5);mv[i]=scale(add(v[i],previousV[i]),.5);}auto e=observe(m,mass,q,v),mid=observe(m,mass,middle,mv);W+=h*Tmid*mid.unitPower;damp+=h*4*mid.K;
  out<<time<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<e.K<<','<<e.attachmentSkin<<','<<e.attachmentRails<<','<<Tend*e.tendon<<','<<m.cableLength(q)<<','<<W<<','<<damp<<','<<e.forceBalance<<','<<e.momentBalance<<'\n';out.flush();previous=q;previousV=v;
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
