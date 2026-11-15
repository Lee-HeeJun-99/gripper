#define main prior_main
#include "../integrated/Driver.cpp"
#undef main
#include <sofa/component/solidmechanics/fem/elastic/BeamFEMForceField.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <iomanip>
using Types=sofa::defaulttype::Rigid3Types;
using Beam=sofa::component::solidmechanics::fem::elastic::BeamFEMForceField<Types>;
using FF=sofa::core::behavior::ForceField<Types>;
using State=sofa::core::behavior::MechanicalState<Types>;
double candidate(Beam*beam,State*state,const Types::VecCoord&x,sofa::core::topology::BaseMeshTopology*topology){
 const auto&rest=state->read(sofa::core::vec_id::read_access::restPosition)->getValue();const auto&data=beam->d_beamsData.getValue();double energy=0;const auto&edges=topology->getEdges();
 for(size_t i=0;i<edges.size();++i){unsigned a=edges[i][0],b=edges[i][1];Beam::Displacement d;d.clear();auto u=x[a].getOrientation().inverseRotate(x[b].getCenter()-x[a].getCenter())-rest[a].getOrientation().inverseRotate(rest[b].getCenter()-rest[a].getCenter());auto q0=rest[a].getOrientation().inverse()*rest[b].getOrientation();auto q=x[a].getOrientation().inverse()*x[b].getOrientation();auto diff=q0.inverse()*q;diff.normalize();if(diff[3]<0)for(int j=0;j<4;++j)diff[j]=-diff[j];auto rot=diff.quatToRotationVector();for(int j=0;j<3;++j){d[j+6]=u[j];d[j+9]=rot[j];}auto force=data[i]._k_loc*d;for(int j=0;j<12;++j)energy+=.5*d[j]*force[j];}
 return energy;
}
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("SOFA_ROOT SCENE PLUGIN");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");if(!sofa::simpleapi::importPlugin(argv[3]))throw std::runtime_error("plugin");
 auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene");sofa::simulation::node::initRoot(root.get());auto body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");auto*state=dynamic_cast<State*>(body->getMechanicalState());Beam*beam=nullptr;auto*context=static_cast<sofa::core::objectmodel::BaseContext*>(body);for(auto*ff:context->getObjects<FF>(sofa::core::objectmodel::BaseContext::Local))if(auto*b=dynamic_cast<Beam*>(ff))beam=b;if(!state||!beam)throw std::runtime_error("beam/state");const auto rest=state->read(sofa::core::vec_id::read_access::restPosition)->getValue();auto*topology=body->getMeshTopology();std::cout<<std::setprecision(17);
 for(double amplitude:{0.,.001,.01,.1,.4}){auto x=rest;for(size_t i=0;i<x.size();++i){double s=rest[i].getCenter()[0]/100.;x[i].getCenter()[2]+=amplitude*s*s;x[i].getOrientation()=sofa::type::Quat<double>(sofa::type::Vec3d(0,1,0),-2*amplitude*s/100.);}
  FF::DataVecCoord xd;xd.setValue(x);FF::DataVecDeriv force,velocity;force.setValue(Types::VecDeriv(x.size()));velocity.setValue(Types::VecDeriv(x.size()));sofa::core::MechanicalParams mp;beam->addForce(&mp,force,xd,velocity);double maxError=0,peak=0;for(size_t i=0;i<x.size();++i)for(int axis=0;axis<6;++axis){auto plus=x,minus=x;double step=1e-6;if(axis<3){plus[i].getCenter()[axis]+=step;minus[i].getCenter()[axis]-=step;}else{sofa::type::Vec3d dir;dir.clear();dir[axis-3]=1;plus[i].getOrientation()=sofa::type::Quat<double>(dir,step)*x[i].getOrientation();minus[i].getOrientation()=sofa::type::Quat<double>(dir,-step)*x[i].getOrientation();}double fd=-(candidate(beam,state,plus,topology)-candidate(beam,state,minus,topology))/(2*step);double actual=force.getValue()[i][axis];maxError=std::max(maxError,std::abs(fd-actual));peak=std::max(peak,std::abs(actual));}
  std::cout<<"ENERGY_CHECK {\"amplitude\":"<<amplitude<<",\"candidate_energy\":"<<candidate(beam,state,x,topology)<<",\"max_force_gradient_error\":"<<maxError<<",\"peak_force_or_torque\":"<<peak<<"}"<<std::endl;
 }
 sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
