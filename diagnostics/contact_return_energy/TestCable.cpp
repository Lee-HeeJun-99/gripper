#include "FrameReturn.h"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include "FrameClassOnly.inc"
#include <iostream>
struct Collector:sofa::core::behavior::StiffnessMatrixAccumulator{
 std::vector<NormalInventory::Entry>entries;
 void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{if(v)entries.push_back({unsigned(r),unsigned(c),v});}
 void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}
};
int main(){try{
 using namespace regrip_integrated;using State=sofa::component::statecontainer::MechanicalObject<Types>;
 auto state=sofa::core::objectmodel::New<State>();state->resize(6);Types::VecCoord x(6);
 for(unsigned i=0;i<6;++i){x[i].getCenter()={5.*i,0,0};x[i].getOrientation()={0,0,0,1};}
 state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 auto cable=sofa::core::objectmodel::New<RoutedCable>(state.get());cable->route.setValue({0,1,2,3,4});cable->tension.setValue(.001);cable->init();double originalRest=cable->restLength;
 double maximum=0;sofa::core::MechanicalParams mp;
 for(unsigned step=0;step<100;++step){
  for(unsigned i=0;i<6;++i){x[i].getCenter()={5.*i+.01*std::sin(step*.1+i),.1*std::sin(step*.03+i),.2*std::cos(step*.05+i)};auto q=exp(V{.05*std::sin(step*.1+i),.1*std::cos(step*.03+i),.07*std::sin(step*.02+i)});for(unsigned j=0;j<4;++j)x[i].getOrientation()[j]=q[j];}
  state->write(sofa::core::vec_id::write_access::position)->setValue(x);auto snapshot=snapshotCableAssembly(cable.get(),x);
  RoutedCable::DataVecDeriv force,velocity;
  force.setValue(Types::VecDeriv(6));velocity.setValue(Types::VecDeriv(6));cable->addForce(&mp,force,*state->read(sofa::core::vec_id::read_access::position),velocity);
  Collector collector;sofa::core::behavior::StiffnessMatrix matrix;matrix.setMatrixAccumulator(&collector,state.get());cable->buildStiffnessMatrix(&matrix);
  if(snapshot.energy!=cable->getPotentialEnergy(&mp,*state->read(sofa::core::vec_id::read_access::position))||snapshot.jacobian.size()!=collector.entries.size()||originalRest!=cable->restLength)throw std::runtime_error("cable snapshot shape/energy/query purity");
  for(unsigned i=0;i<6;++i)for(unsigned j=0;j<6;++j)maximum=std::max(maximum,std::abs(snapshot.force[i][j]-force.getValue()[i][j]));
  for(unsigned i=0;i<collector.entries.size();++i){auto a=collector.entries[i],b=snapshot.jacobian[i];if(a.r!=b.r||a.c!=b.c)throw std::runtime_error("cable snapshot J ordering");maximum=std::max(maximum,std::abs(a.value-b.value));}
 }
 if(maximum!=0)throw std::runtime_error("snapshot differs from actual frozen SDK APIs");
 cable->stiffness.setValue(1);bool rejected=false;try{snapshotCableAssembly(cable.get(),x);}catch(const std::runtime_error&){rejected=true;}if(!rejected)throw std::runtime_error("elastic cable silently treated as active work");
 std::cout<<"PASS100 frozen tension-cable SDK API states,Force/J/energy exact,restLength unchanged;unsupported elastic mode rejected\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
