// Passive actual-SOFA accepted-state geometry observer. NO contact force.
#define REGRIP_PRECISE_TENDON_OWNER_EMBEDDED
#include "../film_precise_tendon/Owner.cpp"
#include "../film_solver_plan/Plan.h"
#include "SphereEquilibrium.h"
#include "../film_three_finger/FrameLayout.h"
namespace regrip_envelope {
using regrip_film_rail::Assembly;
using regrip_film_rail::Point;
class FilmEnvelopeObservedODE:public regrip_precise_tendon::FilmPreciseTendonSubcycledODE {
public:
 SOFA_CLASS(FilmEnvelopeObservedODE,regrip_precise_tendon::FilmPreciseTendonSubcycledODE);
 sofa::core::objectmodel::Data<bool> observe;
 mutable std::ofstream journal;
 FilmEnvelopeObservedODE():observe(initData(&observe,true,"observe","Passive envelope geometry audit;never applies force")){}
 double horizon()const override{return .001;}
 bool qualifiedSteps(unsigned n)const override{return n==40||n==80||n==160;}
 unsigned microstepCount(double t,double h)const override{return regrip_solver_plan::select(count-1,maxSteps.getValue(),t,h).microsteps;}
 double microstepTolerance(double t,double h)const override{return regrip_solver_plan::select(count-1,maxSteps.getValue(),t,h).newtonTolerance;}
 void init()override{
  FilmPreciseTendonSubcycledODE::init();
  if(observe.getValue()){auto path=filename.getValue()+".envelope.csv";if(std::ifstream(path))throw std::runtime_error("immutable geometry journal exists");journal.open(path);journal<<std::setprecision(17)<<"time,triangle,half_thickness_mm,buffered_envelope_gap_mm\n";}
 }
 regrip_transmission::Step advance(const Assembly&m,const std::vector<Point>&q,const std::vector<Point>&v,double t,double h,const std::vector<double>&mass)const override{
  auto out=FilmPreciseTendonSubcycledODE::advance(m,q,v,t,h,mass);
  if(observe.getValue()){
   auto map=regrip_transmission::mechanics(m,out.q,out.v,h,0,mass);
   regrip_three_finger::Layout layout;
   Eigen::Vector3d c=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.2)-layout.mount[0].origin);
   regrip_precise_static::SphereEquilibrium surface(map,{c[0],c[1],c[2]},layout.bufferRadius);surface.setThicknessEnvelope();
   auto g=surface.geometry(map.pack(out.q),Eigen::VectorXd::Zero(surface.triangles.size()),false);
   for(unsigned row=0;row<surface.triangles.size();++row)journal<<t+h<<','<<row<<','<<surface.rowOffsets[row]<<','<<g.gap(row)<<'\n';journal.flush();
  }return out;
 }
};
}
extern "C" {
__attribute__((visibility("default")))void initExternalModule(){}
__attribute__((visibility("default")))const char*getModuleName(){return "ReGripEnvelopeAudit";}
__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){registerFilmPreciseAttachmentField(f);f->registerObjects(sofa::core::ObjectRegistrationData("Passive thickness geometry observer;NO contact forces/grasp certification").add<regrip_envelope::FilmEnvelopeObservedODE>());}
}
