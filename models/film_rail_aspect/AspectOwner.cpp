#define REGRIP_TRANSMISSION_EMBEDDED
#include "../film_transmission/Owner.cpp"
#include "../film_lateral_tendon/Step.h"
#include "Design.h"
namespace regrip_rail_aspect {
class FilmRailAspectODE:public regrip_transmission::FilmTransmissionAlignedODE {
public:
 SOFA_CLASS(FilmRailAspectODE,regrip_transmission::FilmTransmissionAlignedODE);
 mutable double frozenThickness=-1;
 std::string expectedFieldClass()const override{return "FilmAspectTendon";}
 regrip_film_rail::Assembly assembly()const override{
  double h=parameter<double>("railThickness");if(frozenThickness<0)frozenThickness=h;if(h!=frozenThickness)throw std::runtime_error("frozen physical rail geometry changed without parameter work");
  auto m=design(h);if(parameter<double>("bondStiffness")!=m.bondK||parameter<double>("guideOffset")!=m.guideOffset||parameter<double>("lateralOffset")!=6.)throw std::runtime_error("single-factor physical rail comparison required");return m;
 }
 regrip_transmission::Step advance(const regrip_film_rail::Assembly&m,const std::vector<regrip_film::Point>&q,const std::vector<regrip_film::Point>&v,double time,double h,const std::vector<double>&mass)const override{
  using namespace regrip_transmission;auto map=mechanics(m,q,v,h,0,mass);auto input=prescribedControl();auto out=gauss(filmMass(map),map.pack(q),map.pack(v),time,h,[&](const Eigen::VectorXd&x,double t){return regrip_lateral_tendon::parts(map,map.expand(x),input.sample(t).tension,6.);});Step r{map.expand(out.q),map.expand(out.v),out.residual,out.evaluations};r.highOrder=true;for(unsigned j=0;j<2;++j){r.stageQ[j]=map.expand(out.stageQ[j]);r.stageV[j]=map.expand(out.stageV[j]);r.stageTime[j]=time+h*(.5+(j?1:-1)*std::sqrt(3.)/6);r.stageT[j]=input.sample(r.stageTime[j]).tension;}return r;
 }
};
}
void registerFilmAspectField(sofa::core::ObjectFactory*);
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmRailAspect";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmAspectField(f);f->registerObjects(sofa::core::ObjectRegistrationData("EXPERIMENTAL same-core-volume physical rail-aspect single free coupon;NOT contact/time/grasp certification").add<regrip_rail_aspect::FilmRailAspectODE>());}
}
