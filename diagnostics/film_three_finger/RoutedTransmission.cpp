#include "../../models/film_routed_tendon/Step.h"
#include <iomanip>
#include <iostream>
using namespace regrip_routed_tendon;
// Read-only endpoint force inventory;no invented integration weights/work.
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("samples,exclusive output required");
 auto m=model();validate(m,4.5);std::ifstream in(argv[1]);unsigned count;in>>count;
 if(!in||count==0||count>1000||std::ifstream(argv[2]))throw std::runtime_error("bounded exclusive endpoint inventory required");
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time_s,finger,T_per_rail_N,skin_direct_tendon_norm_N,rail_tendon_norm_N,skin_attachment_norm_N,rail_attachment_norm_N,skin_attachment_power_Nmm_s,rail_attachment_power_Nmm_s,tendon_power_Nmm_s,skin75_attachment_Fz_N,rail75_attachment_Fz_N,rail75_tendon_Fz_N,skin75_mean_vz_mm_s,rail75_mean_vz_mm_s,attachment_net_force_norm_N,attachment_net_moment_norm_Nmm,cable_length_mm\n";
 for(unsigned k=0;k<count;++k){double t,T;unsigned f;in>>t>>f>>T;std::vector<Point>q(m.size()),v(m.size()),bond(m.size()),cable(m.size());for(auto&x:q)for(double&y:x)in>>y;for(auto&x:v)for(double&y:x)in>>y;if(!in||f>=3||T<0)throw std::runtime_error("invalid actual endpoint payload");
  elements(m,q,T,4.5,[&](const Element&e){if(e.kind==1||e.kind==2)for(unsigned a=0;a<3*e.ids.size();++a)(e.kind==1?bond:cable)[e.ids[a/3]][a%3]-=e.energy.g[a];});
  double cs=0,cr=0,bs=0,br=0,ps=0,pr=0,pc=0,fs=0,fr=0,fc=0,vs=0,vr=0;unsigned ns=0,nr=0;Point net{},moment{};
  auto actual=m.rest();for(unsigned i=0;i<m.size();++i)for(unsigned d=0;d<3;++d)actual[i][d]+=q[i][d];
  for(unsigned i=0;i<m.size();++i){(i<105?cs:cr)+=dot(cable[i],cable[i]);(i<105?bs:br)+=dot(bond[i],bond[i]);(i<105?ps:pr)+=dot(bond[i],v[i]);pc+=dot(cable[i],v[i]);auto torque=cross(actual[i],bond[i]);for(unsigned d=0;d<3;++d){net[d]+=bond[i][d];moment[d]+=torque[d];}}
  for(unsigned part=0;part<3;++part)for(unsigned j=0;j<m.parts[part].ny;++j){unsigned id=m.id(part,15,j);if(part==0){fs+=bond[id][2];vs+=v[id][2];++ns;}else{fr+=bond[id][2];fc+=cable[id][2];vr+=v[id][2];++nr;}}
  out<<t<<','<<f<<','<<T<<','<<std::sqrt(cs)<<','<<std::sqrt(cr)<<','<<std::sqrt(bs)<<','<<std::sqrt(br)<<','<<ps<<','<<pr<<','<<pc<<','<<fs<<','<<fr<<','<<fc<<','<<vs/ns<<','<<vr/nr<<','<<std::sqrt(dot(net,net))<<','<<std::sqrt(dot(moment,moment))<<','<<length(m,q,4.5)<<'\n';
 }
 std::string extra;if(in>>extra)throw std::runtime_error("trailing samples");
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
