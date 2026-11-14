#include "../models/stabilization/Distributed.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_integrated;
void require(bool b,const char*message){if(!b)throw std::runtime_error(message);}
template<class Parent>struct Acc:Parent{double a[18][18]{};void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{a[r][c]+=v;}void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}};
int main(){try{
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(3);
 auto ff=sofa::core::objectmodel::New<DistributedContact>(state.get());ff->segments.setValue({0,1});ff->objectIndex.setValue(2);ff->samples.setValue(4);ff->speed.setValue(.001);
 Inherit::VecCoord x(3);Inherit::VecDeriv v(3);for(int i=0;i<3;++i)x[i].getOrientation()=sofa::type::Quat<double>(0,0,0,1);
 x[0].getCenter()=sofa::type::Vec3d(-.2,.1,4.98);x[1].getCenter()=sofa::type::Vec3d(.2,.1,4.98);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 v[0][0]=.02;v[0][1]=.01;v[1][0]=.015;v[1][1]=-.01;v[2][0]=-.01;v[2][4]=.003;
 double maxX=0,maxV=0,maxMoment=0;
 for(unsigned shape=0;shape<3;++shape){ff->shape.setValue(shape);auto b=ff->compute(x,v);double J[18][18]{},B[18][18]{};for(auto&t:b.a.J)J[t.r][t.c]+=t.v;for(auto&t:b.B)B[t.r][t.c]+=t.v;
  state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::velocity)->setValue(v);
  Acc<sofa::core::behavior::StiffnessMatrixAccumulator> ka;sofa::core::behavior::StiffnessMatrix km;km.setMatrixAccumulator(&ka,state.get());ff->buildStiffnessMatrix(&km);
  Acc<sofa::core::behavior::DampingMatrixAccumulator> ba;sofa::core::behavior::DampingMatrix bm;bm.setMatrixAccumulator(&ba,state.get());ff->buildDampingMatrix(&bm);
  for(int i=0;i<18;++i)for(int j=0;j<18;++j)require(std::abs(ka.a[i][j]-J[i][j])<1e-14&&std::abs(ba.a[i][j]-B[i][j])<1e-14,"actual SOFA stiffness/damping API");
  Inherit::DataVecDeriv dx,df;Inherit::VecDeriv delta(3);for(int i=0;i<18;++i)delta[i/6][i%6]=.01*(i+1);dx.setValue(delta);df.setValue(Inherit::VecDeriv(3));sofa::core::MechanicalParams mp;mp.setKFactor(2.5);mp.setBFactor(.7);ff->addDForce(&mp,df,dx);
  for(int i=0;i<18;++i){double expected=0;for(int j=0;j<18;++j)expected+=(2.5*J[i][j]+.7*B[i][j])*delta[j/6][j%6];require(std::abs(expected-df.getValue()[i/6][i%6])<1e-14,"actual kFactor/bFactor");}
  require(ff->frictionPower>=0,"negative friction dissipation");
  for(int i=0;i<18;++i){auto xp=x,xm=x;auto p=increment(EnergyField::pose(x[i/6]),i%6,1e-6),m=increment(EnergyField::pose(x[i/6]),i%6,-1e-6);
   for(int j=0;j<3;++j){xp[i/6].getCenter()[j]=p.p[j];xm[i/6].getCenter()[j]=m.p[j];}xp[i/6].getOrientation()=sofa::type::Quat<double>(p.q[0],p.q[1],p.q[2],p.q[3]);xm[i/6].getOrientation()=sofa::type::Quat<double>(m.q[0],m.q[1],m.q[2],m.q[3]);
   auto ap=ff->compute(xp,v),am=ff->compute(xm,v);for(int j=0;j<18;++j)maxX=std::max(maxX,std::abs((ap.a.f[j]-am.a.f[j])/2e-6-J[j][i]));
   auto vp=v,vm=v;vp[i/6][i%6]+=1e-6;vm[i/6][i%6]-=1e-6;ap=ff->compute(x,vp);am=ff->compute(x,vm);for(int j=0;j<18;++j)maxV=std::max(maxV,std::abs((ap.a.f[j]-am.a.f[j])/2e-6-B[j][i]));
  }
  V force{},moment{};for(int i=0;i<3;++i){V f{b.a.f[6*i],b.a.f[6*i+1],b.a.f[6*i+2]},t{b.a.f[6*i+3],b.a.f[6*i+4],b.a.f[6*i+5]};force=add(force,f);moment=add(moment,add(t,cross(EnergyField::pose(x[i]).p,f)));}for(double z:force)require(std::abs(z)<1e-12,"net contact force");for(double z:moment)maxMoment=std::max(maxMoment,std::abs(z));
  auto q=exp(V{.4,-.3,.2});auto xr=x;auto vr=v;for(int i=0;i<3;++i){auto p=EnergyField::pose(x[i]);p.p=add(rotate(q,p.p),V{1,2,-3});p.q=multiply(q,p.q);for(int j=0;j<3;++j)xr[i].getCenter()[j]=p.p[j];xr[i].getOrientation()=sofa::type::Quat<double>(p.q[0],p.q[1],p.q[2],p.q[3]);for(int offset:{0,3}){auto vel=rotate(q,V{v[i][offset],v[i][offset+1],v[i][offset+2]});for(int j=0;j<3;++j)vr[i][offset+j]=vel[j];}}
  auto rotated=ff->compute(xr,vr);for(int i=0;i<3;++i)for(int offset:{0,3}){auto forceR=rotate(q,V{b.a.f[6*i+offset],b.a.f[6*i+offset+1],b.a.f[6*i+offset+2]});for(int j=0;j<3;++j)require(std::abs(forceR[j]-rotated.a.f[6*i+offset+j])<1e-12,"distributed contact objectivity");}
 }
 require(maxX<1e-7&&maxV<1e-7&&maxMoment<1e-12,"distributed full-component derivative/moment consistency");
 ff->speed.setValue(1e-5);auto tiny=v;for(auto&d:tiny)for(int j=0;j<6;++j)d[j]*=1e-4;auto actual=ff->compute(x,tiny);double actualB[18][18]{};for(auto&t:actual.B)actualB[t.r][t.c]+=t.v;
 for(int i=0;i<18;++i){auto vp=tiny,vm=tiny;vp[i/6][i%6]+=1e-10;vm[i/6][i%6]-=1e-10;auto p=ff->compute(x,vp),m=ff->compute(x,vm);for(int j=0;j<18;++j)maxV=std::max(maxV,std::abs((p.a.f[j]-m.a.f[j])/2e-10-actualB[j][i]));}
 require(maxV<1e-7,"velocity derivative at actual1e-5 regularization and creep-scale velocities");
 Inherit::DataVecDeriv invalidF,invalidX;ff->buildDampingMatrix(nullptr);ff->addDForce(nullptr,invalidF,invalidX);
 std::cout<<"PASS distributed contact full18DOF Jx="<<maxX<<" Jv="<<maxV<<" net_moment="<<maxMoment<<" dissipation>=0; 3 shapes; SOFA K/B, kFactor/bFactor, objectivity, invalid null APIs\n";
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}return 0;}
