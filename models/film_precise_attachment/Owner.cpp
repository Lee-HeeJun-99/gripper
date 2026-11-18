#define REGRIP_TRANSMISSION_EMBEDDED
#include "../film_transmission/Owner.cpp"
#include "../film_rail_aspect/Design.h"
#include "../film_c2_startup/Gauss4.h"
#include "Force.h"
namespace regrip_precise_attachment {
class FilmPreciseStartupODE:public regrip_transmission::FilmTransmissionAlignedODE {
public:
 SOFA_CLASS(FilmPreciseStartupODE,regrip_transmission::FilmTransmissionAlignedODE);
 mutable std::ofstream fourStages;
 virtual double horizon()const{return .0002;}
 virtual double residualTolerance()const{return 1e-24;}
 virtual bool qualifiedSteps(unsigned n)const{return n==8||n==16||n==32;}
 virtual regrip_transmission::Parts physicalParts(const regrip_transmission::CoupledPlaneStep&map,const std::vector<Point>&q,double T)const{return regrip_precise_attachment::parts(map,q,T,6.);}
 std::string expectedFieldClass()const override{return "FilmPreciseAttachmentTendon";}
 Assembly assembly()const override{
  auto m=regrip_rail_aspect::design(.1);
  if(parameter<double>("railThickness")!=.1||parameter<double>("bondStiffness")!=m.bondK||parameter<double>("guideOffset")!=5.||parameter<double>("lateralOffset")!=6.)throw std::runtime_error("qualified separate startup geometry required");return m;
 }
 void init()override{
  FilmTransmissionAlignedODE::init();
  if(!qualifiedSteps(maxSteps.getValue())||endTime.getValue()!=horizon())throw std::runtime_error("independently qualified bounded startup/window ONLY");
  auto path=filename.getValue()+".gauss4.csv";if(std::ifstream(path))throw std::runtime_error("four-stage journal exists");fourStages.open(path);fourStages<<std::setprecision(17)<<"macro,stage,time,weight_s,T,q,v,reduced_physical_force_N\n";
 }
 regrip_transmission::Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double time,double h,const std::vector<double>&mass)const override{
  using namespace regrip_transmission;
  if(!(h>0&&h<=.000025000000000001)||time<0||time+h>horizon()+1e-18)throw std::runtime_error("bounded startup interval required");
  auto map=mechanics(m,q,v,h,0,mass);auto control=prescribedControl();
  auto out=regrip_c2_startup::gauss4(filmMass(map),map.pack(q),map.pack(v),time,h,[&](const Eigen::VectorXd&x,double t){return physicalParts(map,map.expand(x),control.sample(t).tension);},false,residualTolerance());
  for(unsigned j=0;j<4;++j){double t=time+h*regrip_c2_startup::c[j];fourStages<<count<<','<<j<<','<<t<<','<<h*regrip_c2_startup::b[j]<<','<<control.sample(t).tension;quote(fourStages,map.expand(out.stageQ[j]));quote(fourStages,map.expand(out.stageV[j]));fourStages<<",\"";for(double x:out.internalForce[j])fourStages<<x<<' ';fourStages<<"\"\n";}fourStages.flush();
  // Legacy two-stage observer is deliberately disabled,not populated with
  // fictitious/missing stages. All four physical stages are in gauss4.csv.
  return {map.expand(out.q),map.expand(out.v),out.residual,out.evaluations};
 }
};
class FilmPreciseWindowODE:public FilmPreciseStartupODE {
public:
 SOFA_CLASS(FilmPreciseWindowODE,FilmPreciseStartupODE);
 double horizon()const override{return .001;}
 double residualTolerance()const override{return 1e-22;}
 bool qualifiedSteps(unsigned n)const override{return n==40||n==80||n==160;}
};
}
#ifndef REGRIP_PRECISE_OWNER_EMBEDDED
void registerFilmPreciseAttachmentField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripPreciseStartup";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmPreciseAttachmentField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL reference-exact attachment four-stage startup;NO contact/grasp certification").add<regrip_precise_attachment::FilmPreciseStartupODE>());f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL independently qualified1ms four-stage window;NO contact/grasp certification").add<regrip_precise_attachment::FilmPreciseWindowODE>());}
}
#endif
