#include "../models/grasp/StickSlip.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_integrated;
using regrip_stick::evaluateContact;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
template<class Parent>struct Acc:Parent{double a[18][18]{};void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{a[r][c]+=v;}void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}};
int main(){try{
 Pose p{{0,0,4.99}},o;regrip_stick::History h;auto eval=[&](Pose x,const regrip_stick::History&s,unsigned shape=0){return evaluateContact(x,o,s,shape,5,5,.1,.01,.02,.3);};
 auto initial=eval(p,h);h=initial.next;require(initial.next.active&&!initial.next.sliding,"stationary contact");
 Pose tiny=p;tiny.p[0]+=1e-13;auto frictionless=evaluateContact(tiny,o,h,0,5,5,.1,.01,.02,0);require(dot(frictionless.next.elastic,frictionless.next.elastic)==0&&frictionless.plasticDissipation==0,"mu0 / sub-ULP tangential increment has no norm singularity");
 Pose sep=p;sep.p[2]=6;require(!eval(sep,{}).next.active,"no contact");
 p.p[0]=.001;auto stick=eval(p,h);require(!stick.next.sliding&&std::abs(stick.wrench.force[0])>1e-7,"static traction at zero velocity");
 auto repeated=eval(p,h);require(repeated.wrench.force==stick.wrench.force&&h.elastic==initial.next.elastic,"query must not mutate history");
 h=stick.next;auto stationary=eval(p,h);require(std::abs(stationary.wrench.force[0]-stick.wrench.force[0])<1e-12,"stationary force persists without creep");
 p.p[0]=.1;auto slip=eval(p,h);require(slip.next.sliding&&slip.plasticDissipation>0,"yield/slip");
 require(std::abs(.02*std::sqrt(dot(slip.next.elastic,slip.next.elastic))-slip.capacity)<1e-14,"Coulomb limit");
 h=slip.next;p.p[0]+=.01;require(eval(p,h).next.sliding,"sustained slip");auto stop=eval(p,h);h=stop.next;p.p[0]-=.0001;require(!eval(p,h).next.sliding,"slip to stick on elastic unloading");
 auto released=eval(sep,h);require(!released.next.active&&released.releaseDissipation>=0,"release resets history");require(std::abs(eval(Pose{{0,0,4.99}},released.next).elasticEnergy)<1e-20,"reentry no old traction");
 double maxJ=0,maxMoment=0;
 for(unsigned shape=0;shape<3;++shape)for(bool sliding:{false,true}){
  Pose a{{.12,.17,4.98}},b;auto old=evaluateContact(a,b,{},shape,5,5,.1,.01,.02,.3).next;a.p[0]+=sliding?.1:.001;
  auto r=evaluateContact(a,b,old,shape,5,5,.1,.01,.02,.3);
  auto reference=evaluateContact(a,b,old,shape,5,5,.1,.01,.02,.3,true);for(int i=0;i<12;++i){require(std::abs(reference.wrench.force[i]-r.wrench.force[i])<1e-14,"AD1 normal vs AD2 energy force");for(int j=0;j<12;++j)require(std::abs(reference.wrench.jacobian[12*i+j]-r.wrench.jacobian[12*i+j])<1e-14,"AD1 normal vs AD2 energy spatial tangent");}
  for(int c=0;c<12;++c){auto ap=a,am=a,bp=b,bm=b;if(c<6){ap=increment(a,c,1e-6);am=increment(a,c,-1e-6);}else{bp=increment(b,c-6,1e-6);bm=increment(b,c-6,-1e-6);}
   auto plus=evaluateContact(ap,bp,old,shape,5,5,.1,.01,.02,.3),minus=evaluateContact(am,bm,old,shape,5,5,.1,.01,.02,.3);for(int row=0;row<12;++row)maxJ=std::max(maxJ,std::abs((plus.wrench.force[row]-minus.wrench.force[row])/2e-6-r.wrench.jacobian[12*row+c]));}
  V fa{r.wrench.force[0],r.wrench.force[1],r.wrench.force[2]},fb{r.wrench.force[6],r.wrench.force[7],r.wrench.force[8]},torque{r.wrench.force[9],r.wrench.force[10],r.wrench.force[11]};for(double v:add(fa,fb))require(std::abs(v)<1e-14,"action reaction");for(double v:add(cross(sub(a.p,b.p),fa),torque))maxMoment=std::max(maxMoment,std::abs(v));
  auto q=exp(V{.6,-.4,.3});auto ar=a,br=b;ar.p=add(rotate(q,a.p),V{1,2,3});ar.q=multiply(q,a.q);br.p=add(rotate(q,b.p),V{1,2,3});br.q=multiply(q,b.q);auto rr=evaluateContact(ar,br,old,shape,5,5,.1,.01,.02,.3);
  for(int offset:{0,6,9}){auto rf=rotate(q,V{r.wrench.force[offset],r.wrench.force[offset+1],r.wrench.force[offset+2]});for(int j=0;j<3;++j)require(std::abs(rf[j]-rr.wrench.force[offset+j])<1e-12,"objective material history/wrench");}
 }
 require(maxJ<1e-7&&maxMoment<1e-12,"FD/moment check");
 for(unsigned shape:{1u,2u}){
  auto cap=evaluateContact(Pose{{0,4.99,0}},o,{},shape,5,5,.1,.01,.02,.3);require(cap.wrench.force[1]>0&&std::abs(cap.wrench.force[0])+std::abs(cap.wrench.force[2])<1e-14,"finite cap/face center");
  auto corner=evaluateContact(Pose{{5.03,5.04,0}},o,{},shape,5,5,.1,.01,.02,.3);require(std::abs(corner.wrench.force[0]-.0003)<1e-12&&std::abs(corner.wrench.force[1]-.0004)<1e-12,"edge/corner SDF normal");
 }
 // Flat box contact: backward-Euler elastic/plastic work identity. The
 // nonnegative algorithmic term is not physical Coulomb dissipation.
 regrip_stick::History flat;Pose a{{0,0,4.99}};flat=evaluateContact(a,o,{},2,5,5,.1,.01,.02,.3).next;double work=0,D=0,algorithmic=0,oldE=0;
 for(int i=1;i<=100;++i){double oldX=a.p[0];a.p[0]=.001*i;auto r=evaluateContact(a,o,flat,2,5,5,.1,.01,.02,.3);double delta=.001,dp=r.next.elastic[0]-flat.elastic[0];work-=r.wrench.force[0]*(a.p[0]-oldX);D+=r.plasticDissipation;algorithmic+=.5*.02*dp*dp;flat=r.next;oldE=r.elasticEnergy;(void)delta;}
 require(std::abs(work-oldE-D-algorithmic)<1e-12,"flat discrete energy identity");
 // Actual component assembly + SOFA matrix/addDForce checks.
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(3);auto ff=sofa::core::objectmodel::New<StickSlipContact>(state.get());ff->segments.setValue({0,1});ff->objectIndex.setValue(2);ff->samples.setValue(2);
 Inherit::VecCoord x(3);for(auto&c:x)c.getOrientation()=sofa::type::Quat<double>(0,0,0,1);x[0].getCenter()=sofa::type::Vec3d(-.2,0,4.99);x[1].getCenter()=sofa::type::Vec3d(.2,0,4.99);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);ff->history.assign(3,{});ff->history=ff->compute(x).next;x[0].getCenter()[0]+=.001;x[1].getCenter()[0]+=.001;state->write(sofa::core::vec_id::write_access::position)->setValue(x);
 auto assembled=ff->compute(x).a;Inherit::DataVecDeriv dx,df;Inherit::VecDeriv v(3);for(auto&z:v)for(int j=0;j<6;++j)z[j]=.001*(j+1);dx.setValue(v);df.setValue(Inherit::VecDeriv(3));sofa::core::MechanicalParams mp;mp.setKFactor(2.5);ff->addDForce(&mp,df,dx);double expected[18]{};for(auto&t:assembled.J)expected[t.r]+=2.5*t.v*v[t.c/6][t.c%6];for(int j=0;j<18;++j)require(std::abs(expected[j]-df.getValue()[j/6][j%6])<1e-14,"SOFA addDForce kFactor");
 Acc<sofa::core::behavior::StiffnessMatrixAccumulator> acc;sofa::core::behavior::StiffnessMatrix matrix;matrix.setMatrixAccumulator(&acc,state.get());ff->buildStiffnessMatrix(&matrix);double J[18][18]{};for(auto&t:assembled.J)J[t.r][t.c]+=t.v;for(int i=0;i<18;++i)for(int j=0;j<18;++j)require(std::abs(J[i][j]-acc.a[i][j])<1e-14,"actual stiffness matrix assembly");
 for(unsigned c=0;c<18;++c){auto xp=x,xm=x;auto a=increment(EnergyField::pose(x[c/6]),c%6,1e-6),b=increment(EnergyField::pose(x[c/6]),c%6,-1e-6);for(int j=0;j<3;++j){xp[c/6].getCenter()[j]=a.p[j];xm[c/6].getCenter()[j]=b.p[j];}xp[c/6].getOrientation()=sofa::type::Quat<double>(a.q[0],a.q[1],a.q[2],a.q[3]);xm[c/6].getOrientation()=sofa::type::Quat<double>(b.q[0],b.q[1],b.q[2],b.q[3]);auto plus=ff->compute(xp).a,minus=ff->compute(xm).a;for(int row=0;row<18;++row)maxJ=std::max(maxJ,std::abs((plus.f[row]-minus.f[row])/2e-6-J[row][c]));}
 require(maxJ<1e-7,"full18DOF component tangent");
 ff->mu.setValue(-1);bool rejected=false;try{ff->compute(x);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"negative runtime mu rejected");ff->mu.setValue(.3);
 std::cout<<"PASS stick/slip/no-contact/release/reentry/objectivity/FD/action-reaction/torque/energy/query-purity/API; maxJ="<<maxJ<<" maxMoment="<<maxMoment<<" work="<<work<<" D="<<D<<" algorithmic="<<algorithmic<<'\n';
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
