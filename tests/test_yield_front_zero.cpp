#include "../models/yield_front_history/ScalarField.h"
#include <iostream>
int main(){regrip_yield_front::Field field(1,2);auto t=field.evaluate({0,0,0},0);std::cout<<"zero_capacity_tangent="<<double(t.measures.tangentMatrix[0])<<" expected=0\n";return t.measures.tangentMatrix[0]==0?0:1;}
