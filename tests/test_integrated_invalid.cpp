#include "../models/integrated/Components.cpp"
#include <iostream>
using namespace regrip_integrated;
int main(int argc,char**argv){
 if(argc>1&&std::string(argv[1])=="stride"){
  auto recorder=sofa::core::objectmodel::New<IntegratedRecorder>();recorder->stride.setValue(0);
  sofa::simulation::AnimateEndEvent event(.001);recorder->handleEvent(&event);
  std::cout<<"PASS zero stride event is safe\n";return 0;
 }
 int rejected=0;
 for(int which=0;which<2;++which){try{V attachment{};double radius=.1;
  if(which==0)radius=std::numeric_limits<double>::quiet_NaN();else attachment[0]=std::numeric_limits<double>::quiet_NaN();
  contact_energy(Pose{{6,0,0},Q{0,0,0,1}},Pose{},0,V{5,5,5},attachment,radius,.01);
 }catch(const std::exception&){++rejected;}}
 auto layer=sofa::core::objectmodel::New<LayerNetwork>();layer->nodes.setValue(3);layer->layers.setValue(2);layer->mode.setValue(2);layer->normalStiffness.setValue(.1);
 Inherit::VecCoord x(6);for(int i=0;i<6;++i){x[i].getCenter()[0]=(i%3)*50.;x[i].getCenter()[2]=(i/3)*.4;x[i].getOrientation()=sofa::type::Quat<double>(0,0,0,1);}
 try{layer->assemble(x);}catch(const std::exception&){++rejected;}
 layer->mode.setValue(0);layer->normalStiffness.setValue(0);layer->connectors.setValue({2});x[1].getOrientation()=sofa::type::Quat<double>(.01,0,0,std::sqrt(1-.0001));
 try{layer->assemble(x);}catch(const std::exception&){++rejected;}
 std::cout<<"invalid contact/finite-confinement/unselected-node inputs rejected="<<rejected<<"/4\n";return rejected==4?0:1;
}
