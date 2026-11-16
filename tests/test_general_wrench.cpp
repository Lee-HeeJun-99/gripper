#include "../models/general_vector_history/GeneralCurvedContact.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
using namespace regrip_integrated;
int main(){try{
 using State=sofa::component::statecontainer::MechanicalObject<Types>;
 auto state=sofa::core::objectmodel::New<State>();state->resize(3);
 Inherit::VecCoord x(3);x[0].getCenter()={-.1,.99,.01};x[1].getCenter()={.1,.99,.01};
 for(auto&p:x)p.getOrientation()={0,0,0,1};
 state->write(sofa::core::vec_id::write_access::position)->setValue(x);
 state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 auto field=sofa::core::objectmodel::New<GeneralVectorCurvedContact>(state.get());
 field->segments.setValue({0,1});field->objectIndex.setValue(2);field->radius.setValue(1);field->pointRadius.setValue(.02);field->historySpacing.setValue(.02);field->prepare(x);
 for(int step=1;step<=4;++step){x[0].getCenter()[2]=x[1].getCenter()[2]=.01+step*.0001;field->commit(x);}
 x[0].getCenter()[2]+=.0001;x[1].getCenter()[2]+=.0001;
 auto a=field->assemble(x);V F{},M{};
 for(unsigned i=0;i<x.size();++i){V f{},torque{},p{};for(int j=0;j<3;++j){f[j]=a.f[6*i+j];torque[j]=a.f[6*i+j+3];p[j]=x[i].getCenter()[j];}F=add(F,f);M=add(M,add(torque,cross(p,f)));}
 double balance=std::max(std::sqrt(dot(F,F)),std::sqrt(dot(M,M))),fd=0;
 for(int k=0;k<18;++k){auto plus=x,minus=x;auto p=increment(field->pose(x[k/6]),k%6,1e-7),m=increment(field->pose(x[k/6]),k%6,-1e-7);
  for(int j=0;j<3;++j){plus[k/6].getCenter()[j]=p.p[j];minus[k/6].getCenter()[j]=m.p[j];}
  for(int j=0;j<4;++j){plus[k/6].getOrientation()[j]=p.q[j];minus[k/6].getOrientation()[j]=m.q[j];}
  auto ap=field->assemble(plus),am=field->assemble(minus);double J[18]{};
  for(auto&t:a.J)if(t.c==unsigned(k))J[t.r]+=t.v;
  for(int j=0;j<18;++j)fd=std::max(fd,std::abs((ap.f[j]-am.f[j])/2e-7-J[j]));
 }
 if(balance>1e-12||fd>1e-7)throw std::runtime_error("sphere global wrench/force FD");
 std::cout<<"PASS sphere moving-history global_wrench="<<balance<<" FD="<<fd<<'\n';return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
