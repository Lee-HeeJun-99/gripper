#pragma once
#include "../film_three_finger/SharedFilmSystem.h"
namespace regrip_stationary_contact {
template<class System>inline double readContactFooter(std::istream&in,const System&s,
 const Eigen::VectorXd&q,const Eigen::VectorXd&v,double time){
 std::string label,value;unsigned count;in>>label>>count;
 if(label!="CONTACT_ROWS"||count!=3)throw std::runtime_error("three explicit stationary contact owners required");
 for(unsigned f=0;f<3;++f){unsigned finger,triangle,feature;in>>finger>>triangle>>feature;auto row=s.selected(q,f);if(!in||finger!=f||triangle!=row.triangle||feature!=row.feature)throw std::runtime_error("exact accepted stationary contact identity differs");}
 double observed,born,clock;in>>label>>observed;if(label!="ROWS_OBSERVED_AT"||observed!=time)throw std::runtime_error("contact observation clock differs");
 in>>label>>born;if(label!="LAST_IMPACT_TIME"||!(born>0&&born<=time))throw std::runtime_error("known global impact provenance missing");
 in>>label>>value;if(label!="INITIAL_CONDITION"||value!="STATIONARY_SEPARATED")throw std::runtime_error("stationary origin missing");in>>label>>clock;
 auto geo=s.geometry(q);if(!in||label!="ACCUMULATED_TIME"||clock!=time||s.clearance(q)<-1e-10||geo.gap.cwiseAbs().maxCoeff()>1e-10||(geo.J*v).cwiseAbs().maxCoeff()>1e-10)throw std::runtime_error("stationary contact state/gap/velocity/clock rejected");
 return born;
}
}
