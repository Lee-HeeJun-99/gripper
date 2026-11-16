#include "../models/film_rail_tendon/RootMapping.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_film_rail;
int main(){try{
 using State=sofa::component::statecontainer::MechanicalObject<sofa::defaulttype::Vec3Types>;using R=FilmAssemblyRootMapping;using W=FilmAssemblyWorldMapping;
 Assembly model(5);auto parent=sofa::core::objectmodel::New<State>(),middle=sofa::core::objectmodel::New<State>(),world=sofa::core::objectmodel::New<State>();for(auto*s:{parent.get(),middle.get(),world.get()})s->resize(model.size());
 auto root=sofa::core::objectmodel::New<R>();root->nx.setValue(5);root->setModels(parent.get(),middle.get());root->init();auto map=sofa::core::objectmodel::New<W>();map->nx.setValue(5);map->setModels(middle.get(),world.get());map->init();
 R::InVecCoord q(model.size());for(unsigned i=0;i<q.size();++i)q[i]={.01*i,-.02*i,.03*i};R::InDataVecCoord input;R::OutDataVecCoord mapped;W::OutDataVecCoord actual;input.setValue(q);root->apply(nullptr,mapped,input);map->apply(nullptr,actual,mapped);auto rest=model.rest();auto*J=root->getJ();
 for(unsigned i=0;i<q.size();++i)for(unsigned j=0;j<3;++j){double expected=0;for(unsigned k=0;k<3*q.size();++k)expected+=J->element(3*i+j,k)*q[k/3][k%3];if(std::abs(mapped.getValue()[i][j]-expected)>1e-15||actual.getValue()[i][j]!=rest[i][j]+mapped.getValue()[i][j])throw std::runtime_error("root/world coordinate Jacobian");}
 R::OutVecDeriv f(q.size());for(unsigned i=0;i<f.size();++i)f[i]={.002*i,.003*i,-.004*i};R::OutDataVecDeriv force;R::InDataVecDeriv pulled;force.setValue(f);pulled.setValue(R::InVecDeriv(q.size()));root->applyJT(static_cast<const sofa::core::MechanicalParams*>(nullptr),pulled,force);double left=0,right=0;for(unsigned i=0;i<q.size();++i)for(unsigned j=0;j<3;++j){left+=f[i][j]*mapped.getValue()[i][j];right+=pulled.getValue()[i][j]*q[i][j];}if(std::abs(left-right)>1e-12)throw std::runtime_error("global virtual work");
 for(unsigned i=0;i<q.size();++i)for(unsigned j=0;j<3;++j)if(input.getValue()[i][j]!=q[i][j])throw std::runtime_error("mapping query purity");
 // Falsify tolerance-based state suppression: Data::setValue and both maps
 // must preserve changes far below Vec's approximate operator== threshold.
 q.assign(q.size(),{});q[11][2]=1e-10;input.setValue(q);root->apply(nullptr,mapped,input);map->apply(nullptr,actual,mapped);
 q[11][2]=2e-10;input.setValue(q);root->apply(nullptr,mapped,input);map->apply(nullptr,actual,mapped);
 if(input.getValue()[11][2]!=2e-10||mapped.getValue()[11][2]!=2e-10||mapped.getValue()[6][2]!=.25*2e-10||actual.getValue()[11][2]!=2e-10)throw std::runtime_error("sub-tolerance mapped increment was suppressed");
 std::cout<<"PASS three-part root/J/virtual-work,sub-1e-6 increments and actual rest+u geometry mapping\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
