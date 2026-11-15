#include "../models/conservative_beam/EnergyKernel.h"
#include "../models/stabilization/Compensated.h"
#include <iostream>
int main(){double x=100,naive=100;long double carry=0;for(int i=0;i<24000;++i){naive+=1e-15;x=regrip_compensated::update(x,x+1e-15,1e-15L,carry);}using namespace regrip_beam;Pose a,b;b.p={100,0,0};auto deformed=b;deformed.p[0]=x;Properties p{183,60,60,8,10,10};auto r=evaluate(a,deformed,a,b,p);double analytic=183*(x-100)/100,err=std::abs(r.force[6]+analytic);std::cout<<"PRECISION naive="<<naive<<" compensated="<<x<<" force_error="<<err<<"; unchanged SO3 DOFs; R3 Euler addition only\n";return naive==100&&x>100&&std::abs(x-double(100.L+24000e-15L))<1.5e-14&&err<1e-12?0:1;}
