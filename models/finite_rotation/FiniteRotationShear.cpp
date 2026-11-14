#include "Kernel.h"
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <limits>
#include <algorithm>
#include <vector>
namespace regrip3d {
using Types=sofa::defaulttype::Rigid3Types;
using Inherit=sofa::core::behavior::ForceField<Types>;
class FiniteRotationShear final:public Inherit {
public:
 SOFA_CLASS(FiniteRotationShear,Inherit);
 sofa::core::objectmodel::Data<double> stiffness,height;
 sofa::core::objectmodel::Data<unsigned> nodes;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> connectors;
 explicit FiniteRotationShear(sofa::core::behavior::MechanicalState<Types>*state=nullptr):Inherit(state),
 stiffness(initData(&stiffness,1.,"stiffness","Per-connector model F/mm")),height(initData(&height,.4,"height","Centroid separation mm")),
 nodes(initData(&nodes,11u,"nodesPerLayer","Nodes per layer")),connectors(initData(&connectors,"connectorIndices","Non-root indices; empty=all")){if(state)mstate.set(state);}
 bool selected(unsigned i)const{const auto&ids=connectors.getValue();return ids.empty()||std::find(ids.begin(),ids.end(),i)!=ids.end();}
 Pose pose(const Types::Coord&p)const{Pose v;for(int i=0;i<3;++i)v.p[i]=p.getCenter()[i];for(int i=0;i<4;++i)v.q[i]=p.getOrientation()[i];return v;}
 void invalid(const char*why){msg_error()<<why;d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);}
 void check(const VecCoord&x)const{
  unsigned n=nodes.getValue();if(n<2||n>10000||x.size()!=2*size_t(n))throw std::invalid_argument("invalid state size");
  const auto&ids=connectors.getValue();for(size_t j=0;j<ids.size();++j)if(ids[j]==0||ids[j]>=n||std::find(ids.begin(),ids.begin()+j,ids[j])!=ids.begin()+j)throw std::invalid_argument("invalid connector selection");
  for(const auto&p:x)validate(pose(p));
 }
 void init()override{Inherit::init();try{if(!mstate)throw std::invalid_argument("missing state");auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();check(x);evaluate(pose(x[0]),pose(x[nodes.getValue()]),stiffness.getValue(),height.getValue());}catch(const std::exception&e){invalid(e.what());}}
 std::vector<std::pair<unsigned,Result>> values(const VecCoord&x)const{check(x);std::vector<std::pair<unsigned,Result>> r;for(unsigned i=1;i<nodes.getValue();++i)if(selected(i))r.emplace_back(i,evaluate(pose(x[i]),pose(x[nodes.getValue()+i]),stiffness.getValue(),height.getValue()));return r;}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{
  try{auto results=values(x.getValue());if(f.getValue().size()!=x.getValue().size())throw std::invalid_argument("force size");auto*out=f.beginEdit();for(auto&pair:results)for(int a=0;a<12;++a)(*out)[pair.first+(a/6)*nodes.getValue()][a%6]+=pair.second.force[a];f.endEdit();}catch(const std::exception&e){invalid(e.what());}}
 void addDForce(const sofa::core::MechanicalParams*mp,DataVecDeriv&df,const DataVecDeriv&dx)override{
  try{if(!mp||!mstate||!std::isfinite(mp->kFactor()))throw std::invalid_argument("invalid parameters/state");auto results=values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(df.getValue().size()!=2*size_t(nodes.getValue())||dx.getValue().size()!=df.getValue().size())throw std::invalid_argument("dforce size");
   auto*out=df.beginEdit();for(auto&pair:results)for(int a=0;a<12;++a){double v=0;for(int b=0;b<12;++b)v+=pair.second.jacobian[12*a+b]*dx.getValue()[pair.first+(b/6)*nodes.getValue()][b%6];(*out)[pair.first+(a/6)*nodes.getValue()][a%6]+=mp->kFactor()*v;}df.endEdit();}catch(const std::exception&e){invalid(e.what());}}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*matrix)override{
  try{if(!matrix||!mstate)throw std::invalid_argument("missing matrix/state");auto results=values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto acc=matrix->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());if(!acc)throw std::invalid_argument("missing accumulator");
   for(auto&pair:results)for(int a=0;a<12;++a)for(int b=0;b<12;++b)acc(6*(pair.first+(a/6)*nodes.getValue())+a%6,6*(pair.first+(b/6)*nodes.getValue())+b%6)+=pair.second.jacobian[12*a+b];}catch(const std::exception&e){invalid(e.what());}}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{try{double e=0;for(auto&pair:values(x.getValue()))e+=pair.second.energy;return e;}catch(const std::exception&){return std::numeric_limits<double>::quiet_NaN();}}
};
}
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripFiniteRotation";}
__attribute__((visibility("default"))) const char*getModuleVersion(){return "0.1.0-experimental";}
__attribute__((visibility("default"))) const char*getModuleLicense(){return "Research prototype";}
__attribute__((visibility("default"))) const char*getModuleDescription(){return "Objective convected-tangent interface spring, experimental";}
__attribute__((visibility("default"))) const char*getModuleComponentList(){return "FiniteRotationShear";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Experimental exact 3D connector").add<regrip3d::FiniteRotationShear>());}
}
