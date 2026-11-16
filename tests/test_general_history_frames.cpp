#include "../models/general_vector_history/Owner.h"
#include <iostream>
using namespace regrip_general_history;
int main(){try{
 Owner a,b;Owner::Physics physics;Pose object,transformed;
 auto rotation=regrip3d::exp({.7,-.9,.4});V shift{2,-1,.3};
 auto transform=[rotation,shift](Pose p){p.p=regrip3d::add(regrip3d::rotate(rotation,p.p),shift);p.q=regrip3d::multiply(rotation,p.q);return p;};
 transformed=transform(object);
 auto geometry=[](int t){return [t](double s){Pose p;double angle=.2*(s-.5)+.001*t;p.p={1.01*std::sin(angle),1.01*std::cos(angle),.0002*t};return p;};};
 Owner::Geometry previous=geometry(0),previousRotated=[&](double s){return transform(previous(s));};
 double covariance=0;unsigned slipped=0;
 for(int step=1;step<=40;++step){
  Owner::Geometry current=geometry(step),oldRotated=[transform,previous](double s){return transform(previous(s));},newRotated=[transform,current](double s){return transform(current(s));};
  auto ta=a.trial(previous,current,object,object,physics),tb=b.trial(oldRotated,newRotated,transformed,transformed,physics);
  a.commit(ta);b.commit(tb);
  for(double s:{.123456789,.5,.876543211}){auto h=a.at(s),g=b.at(s);slipped+=h.sliding;for(int j=0;j<3;++j)covariance=std::max(covariance,std::abs(h.elastic[j]-g.elastic[j]));}
  previous=current;
 }
 if(covariance>1e-13||!slipped)throw std::runtime_error("moving-normal frame covariance");
 regrip_vector_history::SphereChartInput chart;chart.left.p={-.3,.98,0};chart.right.p={.3,.98,0};chart.length=.6;
 chart.history.lo=-1;chart.history.hi=1;
 chart.history.left=chart.history.control1=chart.history.control2=chart.history.right={.5L,{0,0,1}};
 Owner seeded;seeded.seedSphereChart(chart);auto h=seeded.at(.5);auto expected=regrip_vector_history::sphereHistoryChart(chart,0);
 for(int j=0;j<3;++j)if(h.elastic[j]!=double(expected.elastic.value[j]))throw std::runtime_error("sphere chart seed value");
 bool guard=false;Owner limited(1);auto t=limited.trial(previous,previous,object,object,physics);limited.commit(t);
 try{limited.trial(previous,previous,object,object,physics);}catch(const std::length_error&){guard=true;}
 if(!guard)throw std::runtime_error("finite replay bound");
 std::cout<<"PASS moving-normal covariance="<<covariance<<" slip_states="<<slipped<<" chart_seed_and_budget=PASS\n";return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
