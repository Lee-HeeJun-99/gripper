#include "../models/closure_frame/FrameLayer.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_integrated;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
int main(){try{
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(6);auto localState=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();localState->resize(6);auto original=sofa::core::objectmodel::New<LayerNetwork>(localState.get());auto transformed=sofa::core::objectmodel::New<FrameLayerNetwork>(state.get());original->nodes.setValue(3);transformed->nodes.setValue(3);original->normalStiffness.setValue(.001);transformed->normalStiffness.setValue(.001);
 Inherit::VecCoord local(6);for(unsigned i=0;i<6;++i){local[i].getCenter()={50.*(i%3),0,i<3?-.2:.2};local[i].getOrientation()=sofa::type::Quat<double>(0,0,0,1);}local[4].getCenter()[0]+=.001;local[5].getOrientation()=sofa::type::Quat<double>(sofa::type::Vec3d(0,1,0),.0002);
 double error=0;
 for(auto q:{exp(V{0,2.0943951023931953,0}),exp(V{.2,-.3,.1})}){
  transformed->reference.setValue({q[0],q[1],q[2],q[3]});auto world=local;
  for(auto&p:world){auto a=EnergyField::pose(p);a.p=rotate(q,a.p);a.q=multiply(q,a.q);for(int j=0;j<3;++j)p.getCenter()[j]=a.p[j];p.getOrientation()={a.q[0],a.q[1],a.q[2],a.q[3]};}
  auto a=original->assemble(local),b=transformed->assemble(world);for(unsigned i=0;i<6;++i)for(unsigned offset:{0u,3u}){auto f=rotate(q,V{a.f[6*i+offset],a.f[6*i+offset+1],a.f[6*i+offset+2]});for(int j=0;j<3;++j)error=std::max(error,std::abs(f[j]-b.f[6*i+offset+j]));}require(std::abs(a.energy-b.energy)<1e-13,"frame layer energy invariant");
  // Change only valid local in-plane coordinates; world delta is R*dx.
  auto Rdx=rotate(q,V{1e-6,0,0});auto plus=world,minus=world;for(int j=0;j<3;++j){plus[4].getCenter()[j]+=Rdx[j];minus[4].getCenter()[j]-=Rdx[j];}auto bp=transformed->assemble(plus),bm=transformed->assemble(minus);double predicted[36]{};for(auto&t:b.J)if(t.c/6==4&&t.c%6<3)predicted[t.r]+=t.v*Rdx[t.c%6]/1e-6;for(int i=0;i<36;++i)require(std::abs((bp.f[i]-bm.f[i])/2e-6-predicted[i])<1e-7,"rotated stiffness derivative");
  original->mode.setValue(1);transformed->mode.setValue(1);original->pressure.setValue(1e-6);transformed->pressure.setValue(1e-6);original->plastic.assign(2,0);transformed->plastic.assign(2,0);original->dissipated=0;transformed->dissipated=0;localState->write(sofa::core::vec_id::write_access::position)->setValue(local);state->write(sofa::core::vec_id::write_access::position)->setValue(world);sofa::simulation::AnimateEndEvent event(.0005);original->handleEvent(&event);transformed->handleEvent(&event);for(unsigned j=0;j<2;++j)require(std::abs(original->plastic[j]-transformed->plastic[j])<1e-12,"pressure history in local frame");require(std::abs(original->dissipated-transformed->dissipated)<1e-12,"pressure dissipation invariant");original->mode.setValue(0);transformed->mode.setValue(0);
 }
 require(error<1e-12,"frame wrench covariance");std::cout<<std::setprecision(17)<<"PASS fixed-reference layer force/energy/Jacobian/history/dissipation; max_covariance="<<error<<'\n';
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
