#ifdef HISTORY_KERNEL_ONLY
#include "../../models/contact_history/MaterialHistory.h"
#else
#include "../../models/contact_history/ContactFriction.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#endif
#include <iostream>
#include <iomanip>
#include "../../models/contact_birth/BirthIncrement.h"
using namespace regrip_integrated;
void require(bool value,const char*message){if(!value)throw std::runtime_error(message);}
int main(){try{
 std::cout<<std::setprecision(17);using namespace regrip_history;
 Pose object,point;point.p={0,.99,0};History h;h.active=true;h.local=point.p;h.normal={0,1,0};
 // Fixed normal, sublimit displacement, subsequent slip, no query mutation.
 point.p[2]=.001;auto stick=value(point,object,h,2,1,5,.02,1,1,.3);
 require(!stick.next.sliding&&std::abs(stick.next.elastic[2]-.001)<1e-15,"fixed patch stick");
 point.p[2]=.1;auto slip=value(point,object,stick.next,2,1,5,.02,1,1,.3);
 require(slip.next.sliding&&slip.plasticDissipation>0,"slip transition");
 require(std::abs(std::sqrt(dot(slip.next.elastic,slip.next.elastic))-slip.capacity)<1e-15,"friction limit");
 auto frictionless=value(point,object,h,2,1,5,.02,1,1,0);
 require(dot(frictionless.next.elastic,frictionless.next.elastic)==0,"mu zero");
 // Exact discrete spring identity on a fixed flat normal, fixed yield cap:
 // F_end . du = delta U + C |du_p| + .5 kt |delta e|^2.
 // The last term is DERIVED backward-Euler spring integration loss, not a
 // fitted residual or proof of the entire SOFA integrator's energy balance.
 point.p[2]=.1;auto single=value(point,object,h,2,1,5,.02,1,1,.3);
 double endpointWork=single.next.elastic[2]*.1;
 double algorithmic=.5*dot(single.next.elastic,single.next.elastic);
 double closure=endpointWork-single.elasticEnergy-single.plasticDissipation-algorithmic;
 require(std::abs(closure)<1e-15,"derived flat slider discrete work identity");
 std::cout<<"FLAT_SLIDER W="<<endpointWork<<" U="<<single.elasticEnergy<<" D_plastic="<<single.plasticDissipation<<" D_BE="<<algorithmic<<" residual="<<closure<<'\n';
 // Negative-control diagnosis: previous point (0,1.03,0), current
 // (0,1.01,.02), flat contact at y=1.02. Crossing occurs halfway; the
 // continuous constant-velocity in-contact tangent displacement is .01.
 // Current birth rule resets at END of the crossing step and drops it.
 Pose born;born.p={0,1.01,.02};auto newborn=value(born,object,History{},2,1,5,.02,1,1,100);
 require(newborn.next.elastic[2]==0,"record current birth reset limitation");
 std::cout<<"KNOWN_LIMITATION crossing_step expected_elastic_z=.01 actual="<<newborn.next.elastic[2]<<" missed_increment=.01\n";
 Vec<regrip_history::First> end=regrip_history::constantV<regrip_history::First>(born.p);for(int j=0;j<3;++j)end[j]=end[j]+regrip_history::First::variable(j);
 auto corrected=regrip_birth::firstContact({0,1.03,0},end,2,1,5,.02);
 require(std::abs(corrected.crossingFraction-.5)<1e-13&&std::abs(corrected.elastic[2].v-.01)<1e-13,"crossing-aware partial increment");
 double birthJ=0;for(int k=0;k<3;++k){auto p=end,m=end;p[k].v+=1e-7;m[k].v-=1e-7;auto ap=regrip_birth::firstContact({0,1.03,0},p,2,1,5,.02),am=regrip_birth::firstContact({0,1.03,0},m,2,1,5,.02);for(int j=0;j<3;++j)birthJ=std::max(birthJ,std::abs((ap.elastic[j].v-am.elastic[j].v)/2e-7-corrected.elastic[j].g[k]));}
 require(birthJ<1e-7,"birth implicit-root derivative");std::cout<<"EXPERIMENTAL_BIRTH alpha="<<corrected.crossingFraction<<" extension="<<corrected.elastic[2].v<<" J_error="<<birthJ<<" NOT_SOFA_INTEGRATED\n";
 // Entire observer frame rotation: object material history must be unchanged.
 Pose rotatedObject;double angle=.7;rotatedObject.q={0,0,std::sin(angle/2),std::cos(angle/2)};rotatedObject.p={2,3,4};Pose rotatedPoint;rotatedPoint.p=add(rotatedObject.p,rotate(rotatedObject.q,point.p));
 auto transformed=value(rotatedPoint,rotatedObject,h,2,1,5,.02,1,1,.3);
 double objectivity=0;for(int j=0;j<3;++j)objectivity=std::max(objectivity,std::abs(transformed.next.elastic[j]-slip.next.elastic[j]));
 // Compare the same previous state, not the preceding stick state.
 auto original=value(point,object,h,2,1,5,.02,1,1,.3);objectivity=0;
 for(int j=0;j<3;++j)objectivity=std::max(objectivity,std::abs(transformed.next.elastic[j]-original.next.elastic[j]));
 require(objectivity<1e-14,"global frame objectivity");std::cout<<"OBJECTIVITY "<<objectivity<<'\n';
 // Prescribed circular moving patch; no beam or ODE solver error. Exact
 // transported tangential extension is R*angle. Chord formula is second order.
 double last=1;for(int count:{8,16,32,64}){History state;state.active=true;state.local={.99,0,0};state.normal={1,0,0};
  for(int i=1;i<=count;++i){double a=.4*i/count;Pose p;p.p={.99*std::cos(a),.99*std::sin(a),0};auto r=value(p,object,state,0,1,5,.02,1,1,100);require(!r.next.sliding&&r.plasticDissipation==0,"elastic circular path");state=r.next;}
  double error=std::abs(std::sqrt(dot(state.elastic,state.elastic))-.99*.4);require(error<last/3.9,"second order moving patch refinement");last=error;std::cout<<"MOVING_PATCH steps="<<count<<" extension_error="<<error<<'\n';}
#ifndef HISTORY_KERNEL_ONLY
 // Assembled 18-DOF tangent: endpoints remain inside the active interval;
 // no nonsmooth active-set derivative is asserted at contact onset.
 typename sofa::component::statecontainer::MechanicalObject<Types>::SPtr mechanical=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();mechanical->resize(3);Inherit::VecCoord x(3);
 x[0].getCenter()={-.6,.99,0};x[1].getCenter()={.6,.99,0};for(auto&p:x)p.getOrientation()={0,0,0,1};
 mechanical->write(sofa::core::vec_id::write_access::position)->setValue(x);mechanical->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 MaterialHistoryContact::SPtr field=sofa::core::objectmodel::New<MaterialHistoryContact>(mechanical.get());field->segments.setValue({0,1});field->objectIndex.setValue(2);field->radius.setValue(2.);field->historySpacing.setValue(.02);field->prepare(x);
 x[0].getCenter()[2]=.001;x[1].getCenter()[2]=.001;auto assembled=field->assemble(x);double J[18][18]{};for(auto&e:assembled.J)J[e.r][e.c]+=e.v;
 double assembledError=0;for(int col=0;col<18;++col){auto plus=x,minus=x;auto p=EnergyField::pose(x[col/6]);auto pp=increment(p,col%6,1e-6),pm=increment(p,col%6,-1e-6);for(int j=0;j<3;++j){plus[col/6].getCenter()[j]=pp.p[j];minus[col/6].getCenter()[j]=pm.p[j];}for(int j=0;j<4;++j){plus[col/6].getOrientation()[j]=pp.q[j];minus[col/6].getOrientation()[j]=pm.q[j];}auto ap=field->assemble(plus),am=field->assemble(minus);for(int row=0;row<18;++row)assembledError=std::max(assembledError,std::abs((ap.f[row]-am.f[row])/2e-6-J[row][col]));}
 require(assembledError<1e-7,"assembled tangent finite difference");std::cout<<"ASSEMBLED_J "<<assembledError<<'\n';
#endif
 std::cout<<"PASS prescribed stick/slip/objectivity/moving-patch reference\n";
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
