#include "../models/film_coupled_adaptive/ErrorBudget.h"
#include <iostream>
int main(){
 using regrip_coupled_adaptive::defectWeight;const double tolerance=1e-4;
 for(unsigned n:{16u,32u,64u,128u}){
  double total=0;unsigned events=0;
  for(unsigned i=0;i<n;++i){bool event=i%(n/16)==0;events+=event;total+=tolerance/defectWeight(1.,1./n,event,16);}
  if(events!=16||total>tolerance)return 1;
 }
 if(defectWeight(1.,1e-9,true,16)!=32||defectWeight(1.,.125,false,16)!=16)return 2;
 bool rejected=false;try{defectWeight(1.,.1,true,17);}catch(const std::invalid_argument&){rejected=true;}if(!rejected)return 3;
 std::cout<<"PASS sum of event/smooth local defect budgets <= unchanged total;NOT nonlinear stability or SOFA time qualification\n";
}
