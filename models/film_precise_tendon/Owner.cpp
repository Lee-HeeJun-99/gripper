#define REGRIP_PRECISE_OWNER_EMBEDDED
#include "../film_precise_attachment/Owner.cpp"
#include "Force.h"
namespace regrip_precise_tendon {
class FilmPreciseTendonSubcycledODE:public regrip_precise_attachment::FilmPreciseStartupODE {
public:
 SOFA_CLASS(FilmPreciseTendonSubcycledODE,regrip_precise_attachment::FilmPreciseStartupODE);
 std::string expectedFieldClass()const override{return "FilmPreciseTendon";}
 regrip_transmission::Parts physicalParts(const regrip_transmission::CoupledPlaneStep&map,const std::vector<Point>&q,double T)const override{return regrip_precise_tendon::parts(map,q,T,6.);}
 virtual unsigned microstepCount(double,double)const{return 8;}
 virtual double microstepTolerance(double,double)const{return 1e-24;}
 regrip_transmission::Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const override{
  using namespace regrip_transmission;
  if(!(h>0&&h<=.000025000000000001)||time<0||time+h>horizon()+1e-18)throw std::runtime_error("bounded separate subcycled startup/window only");
  auto x=q,y=v;double clock=time,finish=time+h,residual=0;unsigned calls=0;auto input=prescribedControl();
  unsigned subdivisions=microstepCount(time,h);double tolerance=microstepTolerance(time,h);
  if(subdivisions!=1&&subdivisions!=8)throw std::runtime_error("declared1/8 microstep plan required");
  for(unsigned micro=0;micro<subdivisions;++micro){double step=micro+1==subdivisions?finish-clock:h/subdivisions;auto map=mechanics(m,x,y,step,0,mass);auto out=regrip_c2_startup::gauss4(filmMass(map),map.pack(x),map.pack(y),clock,step,[&](const Eigen::VectorXd&z,double t){return physicalParts(map,map.expand(z),input.sample(t).tension);},false,tolerance);
   for(unsigned j=0;j<4;++j){double t=clock+step*regrip_c2_startup::c[j];fourStages<<count<<','<<micro*4+j<<','<<t<<','<<step*regrip_c2_startup::b[j]<<','<<input.sample(t).tension;quote(fourStages,map.expand(out.stageQ[j]));quote(fourStages,map.expand(out.stageV[j]));fourStages<<",\"";for(double f:out.internalForce[j])fourStages<<f<<' ';fourStages<<"\"\n";}
   x=map.expand(out.q);y=map.expand(out.v);clock+=step;residual+=out.residual;calls+=out.evaluations;
  }
  if(clock!=finish||residual>1e-17)throw std::runtime_error("exact micro-to-macro clock/momentum gate failed");fourStages.flush();return {x,y,residual,calls};
 }
};
}
void registerFilmPreciseAttachmentField(sofa::core::ObjectFactory*);
#ifndef REGRIP_PRECISE_TENDON_OWNER_EMBEDDED
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripPreciseTendonSubcycled";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmPreciseAttachmentField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL material tendon eight-microstep startup;NO contact/grasp certification").add<regrip_precise_tendon::FilmPreciseTendonSubcycledODE>());}
}
#endif
