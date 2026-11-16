#include "Kernel.h"
#include "../film_shell/PassiveProfile.h"
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip_film_rail {
class FilmRailTendon final:public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types>{
public:
 using Types=sofa::defaulttype::Vec3Types;using Base=sofa::core::behavior::ForceField<Types>;SOFA_CLASS(FilmRailTendon,Base);
 sofa::core::objectmodel::Data<unsigned>nx;
 sofa::core::objectmodel::Data<bool>rootGuideSecondOrder;
 mutable bool cacheRootGuide=false;
 sofa::core::objectmodel::Data<double>maximumTension,rampTime,releaseBegin,releaseEnd,bondStiffness,guideOffset;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<std::string>costProfileFilename;
 mutable regrip_film::PassiveProfile cost;
 double stepT=0,lastBegin=-1,lastRecord=-1,previousLength=200,previousT=0,work=0;
 mutable bool cached=false;mutable VecCoord cacheX;mutable double cacheT=-1,cacheK=-1,cacheOffset=0;mutable unsigned cacheNx=0;mutable std::vector<Element>cache;
 const DataVecCoord*forceStage=nullptr;std::ofstream journal;
 explicit FilmRailTendon(sofa::core::behavior::MechanicalState<Types>*state=nullptr):Base(state),rootGuideSecondOrder(initData(&rootGuideSecondOrder,false,"rootGuideSecondOrder","Separate guide design:quadratic root tangent,not baseline secant")),nx(initData(&nx,21u,"nx","Independent strips,quarter-aligned mesh")),maximumTension(initData(&maximumTension,.001,"maximumTension","Research tension PER routed rail;not actuator specification")),rampTime(initData(&rampTime,1.,"rampTime","Actuation ramp seconds")),releaseBegin(initData(&releaseBegin,1.,"releaseBegin","Release starts seconds")),releaseEnd(initData(&releaseEnd,2.,"releaseEnd","Zero tension seconds")),bondStiffness(initData(&bondStiffness,.001,"bondStiffness","Assumed point attachment F/mm")),guideOffset(initData(&guideOffset,.2,"guideOffset","Signed eccentric guide offset mm;positive routes behind rails")),costProfileFilename(initData(&costProfileFilename,std::string(),"costProfileFilename","Opt-in passive inclusive cost counters;empty disables")),filename(initData(&filename,std::string(),"filename","Exclusive actual-state journal")){if(state)mstate.set(state);f_listening.setValue(true);}
 Assembly model()const{Assembly m(nx.getValue());m.bondK=bondStiffness.getValue();m.guideOffset=guideOffset.getValue();m.rootGuideSecondOrder=rootGuideSecondOrder.getValue();return m;}
 double control(double t)const{double T=maximumTension.getValue(),r=rampTime.getValue(),b=releaseBegin.getValue(),e=releaseEnd.getValue();if(!std::isfinite(T+r+b+e)||T<0||T>.1||r<=0||b<r||e<=b)throw std::invalid_argument("bounded research tension schedule");return T*std::clamp(t/r,0.,1.)*(t<=b?1.:std::clamp((e-t)/(e-b),0.,1.));}
 const std::vector<Element>&values(const VecCoord&x)const{regrip_film::PassiveProfile::Scope timer(cost,"values");auto m=model();if(x.size()!=m.size())throw std::invalid_argument("assembly DOF size");bool same=cached&&cacheRootGuide==rootGuideSecondOrder.getValue()&&cacheNx==nx.getValue()&&cacheT==stepT&&cacheK==bondStiffness.getValue()&&cacheOffset==guideOffset.getValue()&&cacheX.size()==x.size();if(same)for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j)if(x[i][j]!=cacheX[i][j])same=false;if(same){cost.count("cache_hit");return cache;}cost.count("cache_miss");
  std::vector<Point>q(x.size());for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j)q[i][j]=x[i][j];cache.clear();m.elements(q,stepT,[&](const Element&e){cost.count("AD2_element");cost.count(e.kind==0?"shell_element":e.kind==1?"attachment_element":e.kind==2?"tendon_element":"contact_element");cost.count("cache_element_copy");if(cache.size()==cache.capacity())cost.count("cache_capacity_growth");cache.push_back(e);},&cost);cacheX=x;cacheT=stepT;cacheK=bondStiffness.getValue();cacheOffset=guideOffset.getValue();cacheNx=nx.getValue();cacheRootGuide=rootGuideSecondOrder.getValue();cached=true;return cache;}
 void init()override{cost.open(costProfileFilename.getValue());Base::init();if(!mstate)throw std::runtime_error("assembly missing state");values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(!filename.getValue().empty()){std::ifstream old(filename.getValue());if(old)throw std::runtime_error("assembly journal exists");journal.open(filename.getValue());journal<<std::setprecision(17)<<"time,U_shell,U_attachment,U_tendon_generator,K,T_per_rail,cable_length,tendon_work,skin_tip_z,left_tip_z,right_tip_z,max_speed,x\n";}}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{regrip_film::PassiveProfile::Scope timer(cost,"force");forceStage=&x;auto y=f.getValue();for(const auto&e:values(x.getValue()))for(unsigned a=0;a<3*e.ids.size();++a)y[e.ids[a/3]][a%3]-=e.energy.g[a];f.setValue(y);}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{regrip_film::PassiveProfile::Scope timer(cost,"dforce");double k=p->kFactorIncludingRayleighDamping(rayleighStiffness.getValue());if(k==0)return;auto y=df.getValue();for(const auto&e:values(p->readX(mstate.get())->getValue()))for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b)y[e.ids[a/3]][a%3]-=k*e.energy.h[N*a+b]*dx.getValue()[e.ids[b/3]][b%3];df.setValue(y);}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{regrip_film::PassiveProfile::Scope timer(cost,"matrix_assembly");auto matrix=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());for(const auto&e:values((forceStage?forceStage:mstate->read(sofa::core::vec_id::read_access::position))->getValue()))for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b)if(e.energy.h[N*a+b])matrix(3*e.ids[a/3]+a%3,3*e.ids[b/3]+b%3)+=-e.energy.h[N*a+b];}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{regrip_film::PassiveProfile::Scope timer(cost,"energy_query");double e=0;for(const auto&v:values(x.getValue()))e+=v.energy.v;return e;}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){double time=getContext()->getTime();if(time!=lastBegin){stepT=control(time+getContext()->getDt());lastBegin=time;}return;}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!journal)return;double t=getContext()->getTime();if(t==lastRecord)return;lastRecord=t;const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();const auto&v=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();auto m=model();double energies[4]{},K=0,speed=0;for(const auto&e:values(x))energies[e.kind]+=e.energy.v;auto mass=m.masses();std::vector<Point>u(x.size());for(unsigned i=0;i<x.size();++i){for(unsigned j=0;j<3;++j)u[i][j]=x[i][j];K+=.5*mass[i]*v[i].norm2();speed=std::max(speed,v[i].norm());}double length=m.cableLength(u);work-=.5*(stepT+previousT)*(length-previousLength);previousLength=length;previousT=stepT;
  journal<<t<<','<<energies[0]<<','<<energies[1]<<','<<energies[2]<<','<<K<<','<<stepT<<','<<length<<','<<work;for(unsigned s=0;s<3;++s){double tip=0;for(unsigned j=0;j<m.parts[s].ny;++j)tip+=u[m.id(s,m.nx-1,j)][2]/m.parts[s].ny;journal<<','<<tip;}journal<<','<<speed<<",\"";auto rest=m.rest();for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j)journal<<rest[i][j]+x[i][j]<<' ';journal<<"\"\n";journal.flush();
 }
};
void registerFilmAssemblyRootMapping(sofa::core::ObjectFactory*);
void registerFilmAssemblyWorldMapping(sofa::core::ObjectFactory*);
}
extern "C" {__attribute__((visibility("default")))void initExternalModule(){}__attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmRailTendon";}__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){regrip_film_rail::registerFilmAssemblyRootMapping(f);regrip_film_rail::registerFilmAssemblyWorldMapping(f);f->registerObjects(sofa::core::ObjectRegistrationData("Experimental separate film/rails/point-attachments/eccentric-tendon system;not qualified grasp").add<regrip_film_rail::FilmRailTendon>());}}
