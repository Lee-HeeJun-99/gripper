// Reuse the exact read-only constitutive observer, not midpoint quadrature.
#define main archivedMidpointObserverMain
#include "TransmissionObserve.cpp"
#undef main
int main(int argc,char**argv){try{
 if(argc!=6)throw std::runtime_error("bond,offset,mass,actual stages,output required");auto m=model(std::stod(argv[1]),std::stod(argv[2]));auto mass=publicMass(argv[3]);std::ifstream in(argv[4]);unsigned samples;in>>samples;if(samples<2||samples>4000||samples%2)throw std::runtime_error("complete bounded Gauss stage pairs required");std::ofstream out(argv[5]);out<<std::setprecision(17)<<"time,weight,T,tendon_power_Nmm_s,damping_power_Nmm_s,tendon_work_Nmm,damping_work_Nmm\n";double W=0,D=0;
 for(unsigned k=0;k<samples;++k){double time,weight,T;in>>time>>weight>>T;std::vector<Point>q(m.size()),v(m.size());for(auto&x:q)for(double&y:x)in>>y;for(auto&x:v)for(double&y:x)in>>y;if(!in||weight<=0||T<0||!std::isfinite(time))throw std::runtime_error("invalid actual Gauss stage payload");auto e=observe(m,mass,q,v);double power=T*e.unitPower,damping=4*e.K;W+=weight*power;D+=weight*damping;out<<time<<','<<weight<<','<<T<<','<<power<<','<<damping<<','<<W<<','<<D<<'\n';}
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
