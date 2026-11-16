#include "../models/film_shell/FilmSlopeMapping.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
int main(){try{
 using M=regrip_film::FilmSlopeMapping;using State=sofa::component::statecontainer::MechanicalObject<sofa::defaulttype::Vec3Types>;
 auto parent=sofa::core::objectmodel::New<State>(),child=sofa::core::objectmodel::New<State>();parent->resize(9);child->resize(9);
 auto mapping=sofa::core::objectmodel::New<M>();mapping->ny.setValue(3);mapping->setModels(parent.get(),child.get());mapping->init();
 M::InDataVecCoord x;M::OutDataVecCoord y;M::InVecCoord q(9);for(unsigned i=3;i<9;++i)q[i]={.01*i,-.02*i,.03*i};x.setValue(q);mapping->apply(nullptr,y,x);
 for(unsigned j=0;j<3;++j)if(y.getValue()[3+j][2]!=.25*q[6+j][2])throw std::runtime_error("root slope value");
 M::OutDataVecDeriv force;M::InDataVecDeriv pulled;M::OutVecDeriv f(9);for(unsigned i=0;i<9;++i)f[i]={.003*i,.004*i,-.005*i};force.setValue(f);pulled.setValue(M::InVecDeriv(9));mapping->applyJT(static_cast<const sofa::core::MechanicalParams*>(nullptr),pulled,force);
 double left=0,right=0;for(unsigned i=0;i<9;++i)for(unsigned j=0;j<3;++j){left+=f[i][j]*y.getValue()[i][j];right+=pulled.getValue()[i][j]*q[i][j];}if(std::abs(left-right)>1e-14)throw std::runtime_error("virtual work");
 auto*J=mapping->getJ();for(unsigned j=0;j<3;++j){unsigned unused=3*(3+j)+2,active=3*(6+j)+2;double massUnused=0,massActive=0;for(unsigned k=0;k<27;++k){massUnused+=J->element(k,unused)*J->element(k,unused);massActive+=J->element(k,active)*J->element(k,active);}if(massUnused!=0||massActive!=1.0625)throw std::runtime_error("mapped mass");}
 for(unsigned i=0;i<9;++i)for(unsigned j=0;j<3;++j)if(q[i][j]!=x.getValue()[i][j])throw std::runtime_error("parent mutated");
 std::cout<<"PASS hard slope / virtual work / J / mapped mass; distinct boundary,not grasp\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
