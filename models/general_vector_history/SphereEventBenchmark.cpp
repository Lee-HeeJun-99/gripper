#include "SphereEventReturn.h"
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
// Independent chord-event benchmark:one point/fixed externally supported sphere.
// Birth/Death reference, not a moving rigid object, CurvedContact or grasp.
class SphereEventBenchmark final:public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types>{
public:
 using Types=sofa::defaulttype::Vec3Types;using Base=sofa::core::behavior::ForceField<Types>;
 SOFA_CLASS(SphereEventBenchmark,Base);
 using V=regrip_history::V;using First=regrip_history::First;
 sofa::core::objectmodel::Data<unsigned>substeps;
 sofa::core::objectmodel::Data<std::string>filename;
 V previous{},elastic{};bool ready=false;unsigned commits=0;double last=-1,D=0;
 std::ofstream journal;
 explicit SphereEventBenchmark(sofa::core::behavior::MechanicalState<Types>*s=nullptr):Base(s),substeps(initData(&substeps,32u,"substeps","Fixed temporal path subdivision;not history truncation")),filename(initData(&filename,std::string(),"filename","Exclusive journal")){if(s)mstate.set(s);f_listening.setValue(true);}
 struct Trial{regrip_general_history::SphereEventResult path;std::array<First,3>force;};
 void prepare(const VecCoord&x){if(x.size()!=1)throw std::invalid_argument("one material point");for(int j=0;j<3;++j)previous[j]=x[0][j];elastic={};ready=true;query(x);}
 Trial query(const VecCoord&x)const{
  using namespace regrip_history;
  if(!ready||x.size()!=1)throw std::invalid_argument("unprepared moving sphere");
  Vec<First> p{},delta{};for(int j=0;j<3;++j){p[j]=First(x[0][j])+First::variable(j);delta[j]=p[j]-First(previous[j]);}
  auto radius=sqrtAD(dot(p,p));auto normal=scale(p,invAD(radius));auto gap=First(1.02)-radius;
  double r0=std::sqrt(dot(previous,previous)),g0=1.02-r0;
  
  (void)r0;(void)g0;Trial r;
  r.path=regrip_general_history::sphereEventReturn(previous,elastic,p,1.02,.001,.3*.001,substeps.getValue());
  for(int j=0;j<3;++j)r.force[j]=(gap.v>0?First(.001)*gap*normal[j]:First(0))-First(.001)*r.path.elastic[j];
  return r;
 }
 void init()override{Base::init();if(!mstate)throw std::runtime_error("missing state");prepare(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(!filename.getValue().empty()){std::ifstream old(filename.getValue());if(old)throw std::runtime_error("old journal");journal.open(filename.getValue());journal<<std::setprecision(17)<<"time,commits,plastic,stored,x,y,z\n";}}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{auto r=query(x.getValue());auto out=f.getValue();for(int j=0;j<3;++j)out[0][j]+=r.force[j].v;f.setValue(out);}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{auto r=query(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto out=df.getValue();for(int i=0;i<3;++i)for(int j=0;j<3;++j)out[0][i]+=p->kFactor()*r.force[i].g[j]*dx.getValue()[0][j];df.setValue(out);}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{auto r=query(x.getValue());double radius=0;for(int j=0;j<3;++j)radius+=x.getValue()[0][j]*x.getValue()[0][j];double gap=std::max(0.,1.02-std::sqrt(radius));return .5*.001*gap*gap+r.path.storedEnergy.v;/*stored inventory,NOT frictional potential*/}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{auto r=query(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto a=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());for(int i=0;i<3;++i)for(int j=0;j<3;++j)a(i,j)+=r.force[i].g[j];}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event))return;double t=getContext()->getTime();if(t==last)return;auto x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();auto r=query(x);for(int j=0;j<3;++j){elastic[j]=r.path.elastic[j].v;previous[j]=x[0][j];}D+=r.path.plasticLoss.v;++commits;last=t;if(journal){journal<<t<<','<<commits<<','<<D<<','<<r.path.storedEnergy.v;for(auto q:previous)journal<<','<<q;journal<<'\n';journal.flush();}}
};
extern "C"{__attribute__((visibility("default")))void initExternalModule(){} __attribute__((visibility("default")))const char*getModuleName(){return "ReGripSphereEventBenchmark";}__attribute__((visibility("default")))const char*getModuleVersion(){return "0.1-experimental";}__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Active changing-normal temporal-path isolation benchmark").add<SphereEventBenchmark>());}}
