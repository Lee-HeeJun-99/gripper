#include "../models/contact_birth/BirthAwareContact.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
#include <random>
using namespace regrip_integrated;
void require(bool value,const char*label){if(!value)throw std::runtime_error(label);}
int main(){try{
 std::cout<<std::setprecision(17);Pose object,point;point.p={0,1.01,.02};V before{0,1.03,0};auto a=regrip_birthlaw::evaluate(point,object,{},before,2,1,5,.02,1,1,100);
 require(std::abs(a.next.elastic[2]-.01)<1e-13,"partial first-contact displacement");std::cout<<"BIRTH_EXTENSION "<<a.next.elastic[2]<<'\n';double fd=0,valueError=0,momentError=0;
 for(unsigned shape:{0u,1u,2u})for(double mu:{.1,100.})for(int i=0;i<10;++i){point.p=shape==2?V{.01,1.01,.02+i*.0001}:V{1.01,.01,.02+i*.0001};before=shape==2?V{0,1.04,0}:V{1.04,0,0};auto result=regrip_birthlaw::evaluate(point,object,{},before,shape,1,5,.02,1,1,mu),value=regrip_birthlaw::value(point,object,{},before,shape,1,5,.02,1,1,mu);
  for(int j=0;j<3;++j)valueError=std::max(valueError,std::abs(value.next.elastic[j]-result.next.elastic[j]));
  require(result.plasticDissipation>=0,"nonnegative return loss");require(std::sqrt(dot(result.next.elastic,result.next.elastic))<=result.capacity+1e-12,"Coulomb cap");
  for(int k=0;k<12;++k){auto pp=point,pm=point,op=object,om=object;if(k<6){pp=increment(point,k,1e-7);pm=increment(point,k,-1e-7);}else{op=increment(object,k-6,1e-7);om=increment(object,k-6,-1e-7);}auto ap=regrip_birthlaw::evaluate(pp,op,{},before,shape,1,5,.02,1,1,mu),am=regrip_birthlaw::evaluate(pm,om,{},before,shape,1,5,.02,1,1,mu);for(int j=0;j<12;++j)fd=std::max(fd,std::abs((ap.wrench.force[j]-am.wrench.force[j])/2e-7-result.wrench.jacobian[12*j+k]));}
  auto moment=add(add(V{result.wrench.force[3],result.wrench.force[4],result.wrench.force[5]},V{result.wrench.force[9],result.wrench.force[10],result.wrench.force[11]}),cross(sub(point.p,object.p),V{result.wrench.force[0],result.wrench.force[1],result.wrench.force[2]}));for(double v:moment)momentError=std::max(momentError,std::abs(v));
 }
 require(fd<1e-7&&valueError<1e-13&&momentError<1e-12,"birth force/Jacobian/value/moment");std::cout<<"PASS60 birth_J="<<fd<<" value="<<valueError<<" moment="<<momentError<<'\n';
 bool rejected=false;try{point.p={2,0,0};regrip_birthlaw::evaluate(point,object,{},V{-2,0,0},0,1,5,.02,1,1,.3);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"inside-through-outside chord rejected");
 using State=sofa::component::statecontainer::MechanicalObject<Types>;State::SPtr state=sofa::core::objectmodel::New<State>();state->resize(3);Inherit::VecCoord x(3);x[0].getCenter()={-.5,1.03,0};x[1].getCenter()={.5,1.03,0};for(auto&p:x)p.getOrientation()={0,0,0,1};state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 BirthAwareContact::SPtr field=sofa::core::objectmodel::New<BirthAwareContact>(state.get());field->segments.setValue({0,1});field->objectIndex.setValue(2);field->shape.setValue(2);field->radius.setValue(1.);field->pointRadius.setValue(.02);field->mu.setValue(100.);field->lineStiffness.setValue(1.);field->tangentLineStiffness.setValue(1.);field->historySpacing.setValue(.02);field->prepare(x);
 x[0].getCenter()[1]=x[1].getCenter()[1]=1.01;x[0].getCenter()[2]=x[1].getCenter()[2]=.02;auto assembled=field->assemble(x);auto repeated=field->assemble(x);require(assembled.f==repeated.f&&field->plastic==0&&field->steps==0,"pure queries");auto predicted=field->commitValue(x,0,.5).next;field->commit(x);require(std::abs(field->grids[0].state[field->grids[0].count/2].elastic[2]-predicted.elastic[2])<1e-13,"nodal AD commit transition");
 // Exact active boundary on material node: no division-by-zero/NaN.
 x[0].getCenter()={-2,0,0};x[1].getCenter()={2,0,0};field->previous=x;field->shape.setValue(0);field->frozenParameters=field->signature();field->grids[0].count=200;field->grids[0].state.resize(201);auto range=field->interval(x,0);for(double s:{range.lo,range.hi,std::nextafter(range.lo,range.hi),std::nextafter(range.hi,range.lo)}){auto h=field->old(0,s);for(double v:h.elastic)require(std::isfinite(v),"grid boundary finite");}
 std::cout<<"PASS birth/query/commit/multiple-event/grid-boundary guards\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
