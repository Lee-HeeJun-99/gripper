#include "../../models/film_transmission/Gauss.h"
#include <iomanip>
#include <iostream>
using namespace regrip_transmission;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::runtime_error("plan,mass,prefix required");std::ifstream in(argv[1]);unsigned n;in>>n;if(!in||n<1||n>2000)throw std::runtime_error("bounded public plan required");auto m=model();auto mass=publicMass(argv[2]);std::vector<Point>q(m.size()),v(m.size());std::string prefix=argv[3];std::ofstream out(prefix+".states.csv"),stages(prefix+".stages.csv");out<<std::setprecision(17)<<"time,dt,momentum_residual,evaluations,T_mid,T_end,q,v\n";stages<<std::setprecision(17)<<"macro,stage,time,weight,T,q,v\n";double time=0;
 for(unsigned i=0;i<n;++i){double end;in>>end;if(!in||end<=time||end>.05)throw std::runtime_error("invalid independent endpoint plan");double h=end-time;auto after=stepGauss(m,q,v,time,h,mass,holdControl());q=after.q;v=after.v;out<<end<<','<<h<<','<<after.residual<<','<<after.evaluations<<','<<holdControl().sample(time+h/2).tension<<','<<holdControl().sample(end).tension;quote(out,q);quote(out,v);out<<'\n';out.flush();for(unsigned j=0;j<2;++j){stages<<i+1<<','<<j<<','<<after.stageTime[j]<<','<<h/2<<','<<after.stageT[j];quote(stages,after.stageQ[j]);quote(stages,after.stageV[j]);stages<<'\n';}stages.flush();time=end;
 }
 std::string extra;if(in>>extra)throw std::runtime_error("independent plan trailing data");std::cout<<"PASS standalone variable-plan kernel;NOT actual/time/grasp certificate\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
