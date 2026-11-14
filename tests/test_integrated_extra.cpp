#include "../models/integrated/Components.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_integrated;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
int main(){try{
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(3);
 auto cable=sofa::core::objectmodel::New<RoutedCable>(state.get());cable->route.setValue({0,1,2});cable->offset.setValue(-.2);cable->restLength=99.9;
 Inherit::VecCoord x(3);for(int i=0;i<3;++i){x[i].getCenter()[0]=i*50.;x[i].getCenter()[1]=.1*i;x[i].getCenter()[2]=.05*i*i;auto q=exp(V{.03*i,-.02*i,.01*i});x[i].getOrientation()=sofa::type::Quat<double>(q[0],q[1],q[2],q[3]);}
 double maxE=0,maxJ=0;
 for(bool lengthControl:{false,true}){
  cable->stiffness.setValue(lengthControl?.01:0);cable->tension.setValue(.001);cable->shortening.setValue(.001);
  auto a=cable->assemble(x);double J[18][18]{};for(auto&t:a.J)J[t.r][t.c]+=t.v;
  for(int i=0;i<18;++i){auto p=x,m=x;auto pp=increment(EnergyField::pose(x[i/6]),i%6,1e-6),pm=increment(EnergyField::pose(x[i/6]),i%6,-1e-6);
   for(int c=0;c<3;++c){p[i/6].getCenter()[c]=pp.p[c];m[i/6].getCenter()[c]=pm.p[c];}p[i/6].getOrientation()=sofa::type::Quat<double>(pp.q[0],pp.q[1],pp.q[2],pp.q[3]);m[i/6].getOrientation()=sofa::type::Quat<double>(pm.q[0],pm.q[1],pm.q[2],pm.q[3]);
   auto ap=cable->assemble(p),am=cable->assemble(m);maxE=std::max(maxE,std::abs((ap.energy-am.energy)/2e-6+a.f[i]));for(int j=0;j<18;++j)maxJ=std::max(maxJ,std::abs((ap.f[j]-am.f[j])/2e-6-J[j][i]));
  }
 }
 require(maxE<1e-8,"routed whole-cable energy FD");require(maxJ<1e-7,"routed whole-cable tangent FD");
 state->resize(6);auto layer=sofa::core::objectmodel::New<LayerNetwork>(state.get());layer->nodes.setValue(3);layer->layers.setValue(2);layer->mode.setValue(1);layer->pressure.setValue(1e-9);layer->plastic.assign(2,0);
 x.resize(6);for(int l=0;l<2;++l)for(int i=0;i<3;++i){x[3*l+i].getCenter()[0]=i*50.;x[3*l+i].getCenter()[1]=0;x[3*l+i].getCenter()[2]=(l-.5)*.4;x[3*l+i].getOrientation()=sofa::type::Quat<double>(0,0,0,1);}x[5].getCenter()[0]+=.001;state->write(sofa::core::vec_id::write_access::position)->setValue(x);
 auto before=layer->plastic;auto first=layer->assemble(x),second=layer->assemble(x);require(first.f==second.f&&layer->plastic==before&&layer->dissipated==0,"history changed during force/tangent evaluation");
 sofa::simulation::AnimateEndEvent event(.0005);layer->handleEvent(&event);require(layer->plastic[1]>0&&layer->dissipated>0,"friction history not committed at step end");auto third=layer->assemble(x);require(std::abs(third.f[30]-first.f[30])<1e-14,"return mapping traction consistency");
 auto diss=layer->dissipated;layer->pressure.setValue(0);layer->handleEvent(&event);auto off=layer->assemble(x);require(off.f[30]==0&&layer->dissipated>=diss,"pressure OFF and nonnegative dissipation");
 for(int shape=0;shape<3;++shape){auto e=contact_energy(Pose{{6,0,0},Q{0,0,0,1}},Pose{},shape,V{5,5,5},V{},.1,.01);require(e.v==0,"contact detection false positive");auto r=energy_result(contact_energy(Pose{{4.9,0,0},Q{0,0,0,1}},Pose{},shape,V{5,5,5},V{},.1,.01));require(r.force[0]>0&&r.force[6]<0,"contact response/action reaction");}
 std::cout<<"PASS actual full routed-cable energy/tangent FD; max_energy="<<maxE<<" max_J="<<maxJ<<"; friction no-Newton-side-effects/commit/ON-OFF; separate collision detection and response\n";return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
