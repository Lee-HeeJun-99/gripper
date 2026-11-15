#include "EnergyKernel.h"
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <vector>
#include <limits>
namespace regrip_beam {
using Types=sofa::defaulttype::Rigid3Types;using Base=sofa::core::behavior::ForceField<Types>;using BeamBase=Base;
class ConservativeBeam final:public BeamBase{
public:
 SOFA_CLASS(ConservativeBeam,BeamBase);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> edges;
 sofa::core::objectmodel::Data<double> EA,GAy,GAz,GJ,EIy,EIz;
 struct Element{unsigned a,b;Pose a0,b0;};std::vector<Element> elements;size_t count=0;
 mutable VecCoord cachedX;mutable std::array<double,6>cachedMaterial{};mutable std::vector<Result>cached;mutable bool hasCache=false;
 explicit ConservativeBeam(sofa::core::behavior::MechanicalState<Types>*s=nullptr):BeamBase(s),edges(initData(&edges,"edges","Explicit pairs, no object beam or implicit cross-layer edge")),EA(initData(&EA,1.,"EA","Axial rigidity F")),GAy(initData(&GAy,1.,"GAy","Effective transverse shear rigidity F")),GAz(initData(&GAz,1.,"GAz","Effective transverse shear rigidity F")),GJ(initData(&GJ,1.,"GJ","Torsional rigidity F mm2")),EIy(initData(&EIy,1.,"EIy","Bending rigidity F mm2")),EIz(initData(&EIz,1.,"EIz","Bending rigidity F mm2")){if(s)mstate.set(s);}
 static Pose pose(const Types::Coord&c){Pose p;for(int j=0;j<3;++j)p.p[j]=c.getCenter()[j];for(int j=0;j<4;++j)p.q[j]=c.getOrientation()[j];validate(p);return p;}
 Properties properties()const{Properties p{EA.getValue(),GAy.getValue(),GAz.getValue(),GJ.getValue(),EIy.getValue(),EIz.getValue()};p.validate();return p;}
 void invalid(const char*why){msg_error()<<why;d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);}
 void init()override{BeamBase::init();try{
  if(!mstate)throw std::invalid_argument("beam missing state");
  auto&rest=mstate->read(sofa::core::vec_id::read_access::restPosition)->getValue();count=rest.size();auto ids=edges.getValue();if(ids.empty()||ids.size()%2||ids.size()>4000)throw std::invalid_argument("beam edge list size");elements.clear();
  for(size_t i=0;i<ids.size();i+=2){if(ids[i]>=count||ids[i+1]>=count||ids[i]==ids[i+1])throw std::invalid_argument("beam edge index");for(auto&e:elements)if((e.a==ids[i]&&e.b==ids[i+1])||(e.b==ids[i]&&e.a==ids[i+1]))throw std::invalid_argument("duplicate beam edge");elements.push_back({ids[i],ids[i+1],pose(rest[ids[i]]),pose(rest[ids[i+1]])});}
  hasCache=false;values(rest);
 }catch(const std::exception&e){invalid(e.what());}}
 const std::vector<Result>&values(const VecCoord&x)const{
  auto p=properties();auto ids=edges.getValue();if(!count||x.size()!=count||ids.size()!=2*elements.size())throw std::invalid_argument("beam state/topology changed");for(size_t i=0;i<elements.size();++i)if(ids[2*i]!=elements[i].a||ids[2*i+1]!=elements[i].b)throw std::invalid_argument("beam topology changed");
  bool same=hasCache&&cachedMaterial==p.values()&&cachedX.size()==x.size();for(size_t i=0;i<x.size();++i){pose(x[i]);if(same)for(int j=0;j<7;++j)if(x[i][j]!=cachedX[i][j])same=false;}
  if(same)return cached;
  std::vector<Result>next;next.reserve(elements.size());for(auto&e:elements)next.push_back(evaluate(pose(x[e.a]),pose(x[e.b]),e.a0,e.b0,p));cached=std::move(next);cachedX=x;cachedMaterial=p.values();hasCache=true;return cached;
 }
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{try{auto&r=values(x.getValue());if(f.getValue().size()!=count)throw std::invalid_argument("beam force size");auto out=f.getValue();for(size_t e=0;e<r.size();++e)for(int j=0;j<12;++j)out[j<6?elements[e].a:elements[e].b][j%6]+=r[e].force[j];for(auto&v:out)for(int j=0;j<6;++j)if(!std::isfinite(v[j]))throw std::overflow_error("beam force accumulator");f.setValue(out);}catch(const std::exception&e){invalid(e.what());}}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{try{
  if(!p||!mstate)throw std::invalid_argument("beam mechanical params/state");
  double factor=p->kFactorIncludingRayleighDamping(rayleighStiffness.getValue());if(!std::isfinite(factor))throw std::invalid_argument("beam kFactor");auto&r=values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(df.getValue().size()!=count||dx.getValue().size()!=count)throw std::invalid_argument("beam dforce size");for(auto&v:dx.getValue())for(int j=0;j<6;++j)if(!std::isfinite(v[j]))throw std::invalid_argument("beam nonfinite increment");auto out=df.getValue();
  for(size_t e=0;e<r.size();++e)for(int i=0;i<12;++i)for(int j=0;j<12;++j)out[i<6?elements[e].a:elements[e].b][i%6]+=factor*r[e].jacobian[12*i+j]*dx.getValue()[j<6?elements[e].a:elements[e].b][j%6];
  for(auto&v:out)for(int j=0;j<6;++j)if(!std::isfinite(v[j]))throw std::overflow_error("beam dforce accumulator");
  df.setValue(out);
 }catch(const std::exception&e){invalid(e.what());}}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{try{if(!m||!mstate)throw std::invalid_argument("beam matrix/state");auto&r=values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto a=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());if(!a)throw std::invalid_argument("beam accumulator");for(size_t e=0;e<r.size();++e)for(int i=0;i<12;++i)for(int j=0;j<12;++j)if(r[e].jacobian[12*i+j])a(6*(i<6?elements[e].a:elements[e].b)+i%6,6*(j<6?elements[e].a:elements[e].b)+j%6)+=r[e].jacobian[12*i+j];}catch(const std::exception&e){invalid(e.what());}}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{try{double e=0;for(auto&r:values(x.getValue()))e+=r.energy;return e;}catch(...){return std::numeric_limits<double>::quiet_NaN();}}
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripConservativeBeam";}
__attribute__((visibility("default"))) const char*getModuleVersion(){return "0.1.0-research";}
__attribute__((visibility("default"))) const char*getModuleComponentList(){return "ConservativeBeam";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Objective energy-derived midpoint SO3 rod, reduced integration research model").add<regrip_beam::ConservativeBeam>());}
}
