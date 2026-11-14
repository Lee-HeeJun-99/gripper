#include "../models/stabilization/Compensated.h"
#include <cmath>
#include <iostream>
int main(){double naive=100,value=100;long double carry=0;for(int i=0;i<24000;++i){naive+=1e-15;double rounded=value+1e-15;value=regrip_compensated::update(value,rounded,1e-15L,carry);}double exact=double(100.L+24000*1e-15L);if(naive!=100||std::abs(value-exact)>1.5e-14)return 1;std::cout<<"PASS sub-ULP Euler increments accumulated; error="<<std::abs(value-exact)<<" naive lost24000increments\n";}
