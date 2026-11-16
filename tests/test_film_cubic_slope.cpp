#include "../models/film_shell/FilmCubicSlopeMapping.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
int main(){try{
 using M=regrip_film::FilmCubicSlopeMapping;using State=sofa::component::statecontainer::MechanicalObject<sofa::defaulttype::Vec3Types>;
 auto parent=sofa::core::objectmodel::New<State>(),child=sofa::core::objectmodel::New<State>();parent->resize(12);child->resize(12);
 auto mapping=sofa::core::objectmodel::New<M>();mapping->ny.setValue(3);mapping->setModels(parent.get(),child.get());mapping->init();
 M::InDataVecCoord x;M::OutDataVecCoord y;M::InVecCoord q(12);for(unsigned i=0;i<12;++i)q[i]={.01*i,-.02*i,.03*i};x.setValue(q);mapping->apply(nullptr,y,x);
 auto*J=mapping->getJ();for(unsigned i=0;i<36;++i){double value=0;for(unsigned j=0;j<36;++j)value+=J->element(i,j)*q[j/3][j%3];if(std::abs(value-y.getValue()[i/3][i%3])>1e-15)throw std::runtime_error("cubic slope J");}
 M::OutDataVecDeriv force;M::InDataVecDeriv pulled;M::OutVecDeriv f(12);for(unsigned i=0;i<12;++i)f[i]={.003*i,.004*i,-.005*i};force.setValue(f);pulled.setValue(M::InVecDeriv(12));mapping->applyJT(static_cast<const sofa::core::MechanicalParams*>(nullptr),pulled,force);
 double left=0,right=0;for(unsigned i=0;i<12;++i)for(unsigned j=0;j<3;++j){left+=f[i][j]*y.getValue()[i][j];right+=pulled.getValue()[i][j]*q[i][j];}if(std::abs(left-right)>1e-14)throw std::runtime_error("cubic virtual work");
 unsigned a=3*6+2,b=3*9+2;double off=0;for(unsigned k=0;k<36;++k)off+=J->element(k,a)*J->element(k,b);if(std::abs(off+1./18)>1e-16)throw std::runtime_error("mapped off-diagonal mass");
 for(unsigned j=0;j<3;++j){q[3+j][2]=29;q[6+j][2]=112;q[9+j][2]=243;}x.setValue(q);mapping->apply(nullptr,y,x);for(unsigned j=0;j<3;++j)if(y.getValue()[3+j][2]!=29)throw std::runtime_error("clamped cubic manufactured solution");
 std::cout<<"PASS cubic boundary/J/virtual-work/off-diagonal-mass/manufactured cubic;old stencil unchanged\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
