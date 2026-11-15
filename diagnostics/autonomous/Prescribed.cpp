#ifdef REGRIP_OLD_HISTORY
#include "../../models/contact_birth/BirthAwareContact.cpp"
using Field=regrip_integrated::BirthAwareContact;
#else
#include "../../models/material_point_contact/MaterialPointContact.cpp"
using Field=regrip_integrated::MaterialPointContact;
#endif
#include <sofa/component/statecontainer/MechanicalObject.h>
using namespace regrip_integrated;
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("spacing steps common_rotation");
 double spacing=std::stod(argv[1]);int steps=std::stoi(argv[2]);double angle=std::stod(argv[3]);if(steps<2||steps>20000)throw std::invalid_argument("steps");auto rotation=exp(V{angle*.3,angle*.2,angle*.7});
 using State=sofa::component::statecontainer::MechanicalObject<Types>;auto state=sofa::core::objectmodel::New<State>();state->resize(3);Inherit::VecCoord x(3);
 auto configuration=[&](double t){auto q=x;double y=1.03-.04*std::pow(std::sin(3.14159265358979323846*t),2),shift=.3*t,z=.02*std::sin(6.2831853071795864769*t);for(int i=0;i<2;++i){auto p=rotate(rotation,V{(i?2.:-2.)+shift,y,z});for(int j=0;j<3;++j)q[i].getCenter()[j]=p[j];}for(auto&p:q)for(int j=0;j<4;++j)p.getOrientation()[j]=rotation[j];return q;};
 x=configuration(0);state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);auto field=sofa::core::objectmodel::New<Field>(state.get());field->segments.setValue({0,1});field->objectIndex.setValue(2);field->shape.setValue(0);field->radius.setValue(1.);field->pointRadius.setValue(.02);field->mu.setValue(.3);field->lineStiffness.setValue(1.);field->tangentLineStiffness.setValue(1.);field->historySpacing.setValue(spacing);field->prepare(x);
 double D=0,jump=0,absoluteJump=0,work=0,maxForce=0,maxMoment=0;
 for(int step=1;step<=steps;++step){auto next=configuration(double(step)/steps);auto r=field->computeValue(next);D+=r.D;V F{},M{};for(int i=0;i<3;++i){V f{},m{};for(int j=0;j<3;++j){f[j]=r.a.f[6*i+j];m[j]=r.a.f[6*i+j+3];work-=f[j]*(next[i].getCenter()[j]-x[i].getCenter()[j]);}F=add(F,f);M=add(M,add(m,cross(field->pose(next[i]).p,f)));}maxForce=std::max(maxForce,std::sqrt(dot(F,F)));maxMoment=std::max(maxMoment,std::sqrt(dot(M,M)));field->commit(next);auto after=field->computeValue(next);jump+=after.a.energy-r.a.energy;absoluteJump+=std::abs(after.a.energy-r.a.energy);x=next;}
 std::cout<<std::setprecision(17)<<"PRESCRIBED {\"spacing\":"<<spacing<<",\"steps\":"<<steps<<",\"angle\":"<<angle<<",\"query_return_D\":"<<D<<",\"detachment_inventory\":"<<field->released<<",\"commit_energy_jump\":"<<jump<<",\"absolute_commit_energy_jump\":"<<absoluteJump<<",\"imposed_external_work_endpoint\":"<<work<<",\"unexplained_work_minus_losses\":"<<work-D-field->released<<",\"maximum_force_defect\":"<<maxForce<<",\"maximum_moment_defect\":"<<maxMoment;
#ifndef REGRIP_OLD_HISTORY
 std::cout<<",\"actual_point_commit_D\":"<<field->committedPlastic;
#endif
 std::cout<<"}\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
