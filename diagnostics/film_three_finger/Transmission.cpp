#include "../../models/film_transmission/Kernel.h"
#include "../../models/film_transmission/Gauss.h"
#include <fstream>
#include <iomanip>
#include <iostream>
using namespace regrip_transmission;
int main(int argc,char**argv){try{
 if((argc!=7&&argc!=8))throw std::runtime_error("steps,duration,bond,offset,prefix,public_mass required");bool higher=argc==8&&std::string(argv[7])=="gauss";bool common=higher||(argc==8&&std::string(argv[7])=="common");unsigned steps=std::stoul(argv[1]);double duration=std::stod(argv[2]),dt=duration/steps;auto m=model(std::stod(argv[3]),std::stod(argv[4]));if(steps<1||steps>2000||duration<=0||duration>.05||dt>.001)throw std::runtime_error("profiled transmission scope");std::vector<Point>q(m.size()),v(q.size());auto mm=publicMass(argv[6]);auto map=mechanics(m,q,v,dt,0,mm);auto rest=parts(map,q,0),unit=parts(map,q,1);Eigen::MatrixXd M=filmMass(map);if(rest.force.norm()>1e-14)throw std::runtime_error("undeformed force not equilibrium");std::string prefix=argv[5];std::ofstream matrix(prefix+".linear.txt");matrix<<std::setprecision(17)<<map.freeSize<<'\n'<<M.diagonal().transpose()<<'\n'<<unit.tendon.transpose()<<'\n'<<rest.stiffness<<'\n';
 std::ofstream out(prefix+".states.csv");out<<std::setprecision(17)<<"time,dt,momentum_residual,evaluations,T_mid,T_end,q,v\n";std::ofstream stages(prefix+".stages.csv");stages<<std::setprecision(17)<<"macro,stage,time,weight,T,q,v\n";double time=0;for(unsigned i=0;i<steps;++i){double start=time,h=common?((i+1==steps?duration:time+dt)-time):dt;auto after=higher?stepGauss(m,q,v,time,h,mm):step(m,q,v,time,h,mm);time+=h;q=after.q;v=after.v;out<<time<<','<<h<<','<<after.residual<<','<<after.evaluations<<','<<control().sample(start+h/2).tension<<','<<control().sample(time).tension;quote(out,q);quote(out,v);out<<'\n';out.flush();if(after.highOrder)for(unsigned j=0;j<2;++j){stages<<i+1<<','<<j<<','<<after.stageTime[j]<<','<<h/2<<','<<after.stageT[j];quote(stages,after.stageQ[j]);quote(stages,after.stageV[j]);stages<<'\n';}stages.flush();}
 std::cout<<"PASS nonlinear standalone transmission kernel;NOT actual SOFA/time/grasp certificate\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
