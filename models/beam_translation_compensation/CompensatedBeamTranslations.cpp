#include "../stabilization/Compensated.h"
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/objectmodel/BaseComponent.h>
#include <sofa/core/behavior/MechanicalState.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <limits>
#include <set>
#include <algorithm>
#include <cmath>
#include <vector>
#include <stdexcept>
// Independent integration contrast. Only selected structural free translations
// are accumulated with the existing compensated arithmetic kernel. No object
// DOF,quaternion,force,target or boundary value is changed by this component.
class CompensatedBeamTranslations final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(CompensatedBeamTranslations,sofa::core::objectmodel::BaseComponent);
 using Types=sofa::defaulttype::Rigid3Types;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>>indices;
 sofa::core::objectmodel::Data<unsigned>objectIndex,nodes;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::behavior::MechanicalState<Types>*state=nullptr;
 std::vector<double>before;std::vector<long double>carry;
 std::ofstream file;unsigned begins=0,ends=0;size_t corrections=0;double maxCorrection=0,maxCarry=0;
 CompensatedBeamTranslations():indices(initData(&indices,"indices","Only free structural node IDs; roots excluded")),objectIndex(initData(&objectIndex,0u,"objectIndex","First nonstructural DOF; never compensated")),nodes(initData(&nodes,0u,"nodesPerLayer","Structural root periodicity")),filename(initData(&filename,std::string(""),"filename","Exclusive arithmetic diagnostic")){f_listening.setValue(true);}
 void init()override{
  BaseComponent::init();state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(getContext()->getMechanicalState());
  if(!state||nodes.getValue()<2||objectIndex.getValue()+1!=state->getSize()||objectIndex.getValue()%nodes.getValue()||indices.getValue().empty())throw std::invalid_argument("structural compensation scope");
  std::set<unsigned>seen;for(unsigned i:indices.getValue())if(i>=objectIndex.getValue()||i%nodes.getValue()==0||!seen.insert(i).second)throw std::invalid_argument("compensation touched object/root/duplicate");
  std::ifstream old(filename.getValue());if(filename.getValue().empty()||old)throw std::runtime_error("refuse old/empty compensation log");file.open(filename.getValue());if(!file)throw std::runtime_error("compensation log");file<<std::setprecision(17)<<"time,steps,corrections,max_correction_mm,max_carry_mm\n";
  before.resize(2*indices.getValue().size());carry.assign(before.size(),0);
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){
   if(begins!=ends)throw std::runtime_error("duplicate compensation begin");++begins;
   const auto&x=state->read(sofa::core::vec_id::read_access::position)->getValue();size_t k=0;for(unsigned i:indices.getValue())for(unsigned axis:{0u,2u})before[k++]=x[i].getCenter()[axis];
  }else if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)){
   if(ends+1!=begins)throw std::runtime_error("duplicate/missing compensation end");++ends;
   const auto&v=state->read(sofa::core::vec_id::read_access::velocity)->getValue();auto*data=state->write(sofa::core::vec_id::write_access::position);auto x=data->getValue();size_t k=0;
   for(unsigned i:indices.getValue())for(unsigned axis:{0u,2u}){
    double old=x[i].getCenter()[axis];long double increment=static_cast<long double>(v[i][axis])*getContext()->getDt();
    long double discrepancy=static_cast<long double>(before[k])-old+increment;
    double bound=8*std::numeric_limits<double>::epsilon()*std::max({1.,std::abs(before[k]),std::abs(old)});
    if(std::abs(discrepancy)>bound)throw std::runtime_error("not a rounded Euler translation; refuse physical position correction");
    double next=regrip_compensated::update(before[k],old,increment,carry[k]);
    double ulp=std::max(std::abs(std::nextafter(old,INFINITY)-old),std::abs(old-std::nextafter(old,-INFINITY)));
    if(std::abs(next-old)>2*ulp)throw std::runtime_error("compensation exceeds two coordinate ULPs");
    if(next!=old)++corrections;maxCorrection=std::max(maxCorrection,std::abs(next-old));maxCarry=std::max(maxCarry,double(std::abs(carry[k])));x[i].getCenter()[axis]=next;++k;
   }
   data->setValue(x);if(ends%2000==0){file<<getContext()->getTime()<<','<<ends<<','<<corrections<<','<<maxCorrection<<','<<maxCarry<<'\n';file.flush();}
  }
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripBeamTranslationCompensation";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Explicit structural-only compensated Euler accumulation; no object/rotation changes").add<CompensatedBeamTranslations>());}
}
