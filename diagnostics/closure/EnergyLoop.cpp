#include "BeamProbe.inc"
int main(int argc,char**argv){try{
 if(argc!=4)throw std::invalid_argument("SDK SCENE STRUCTURAL_PLUGIN");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");if(!sofa::simpleapi::importPlugin(argv[3]))throw std::runtime_error("plugin");auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("load");sofa::simulation::node::initRoot(root.get());auto body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");auto*state=dynamic_cast<State*>(body->getMechanicalState());Beam*beam=nullptr;for(auto*ff:static_cast<sofa::core::objectmodel::BaseContext*>(body)->getObjects<FF>(sofa::core::objectmodel::BaseContext::Local))if(auto*b=dynamic_cast<Beam*>(ff))beam=b;if(!state||!beam)throw std::runtime_error("beam/state");auto rest=state->read(sofa::core::vec_id::read_access::restPosition)->getValue();unsigned tip=10;std::cout<<std::setprecision(17);
 unsigned rotationNode=tip;
 auto response=[&](double z,double angle){auto x=rest;x[tip].getCenter()[2]+=z;x[rotationNode].getOrientation()=sofa::type::Quat<double>(sofa::type::Vec3d(0,1,0),angle)*rest[rotationNode].getOrientation();FF::DataVecCoord xd;xd.setValue(x);FF::DataVecDeriv f,v;f.setValue(Types::VecDeriv(x.size()));v.setValue(Types::VecDeriv(x.size()));sofa::core::MechanicalParams mp;beam->addForce(&mp,f,xd,v);return std::pair<double,double>{f.getValue()[tip][2],f.getValue()[rotationNode][4]};};
 for(bool proximal:{false,true})for(double amplitude:{.001,.01,.1,1.,5.})for(unsigned pieces:{64u,256u}){
  rotationNode=proximal?tip-1:tip;
  double width=amplitude,height=amplitude*.02,work=0,absoluteWork=0;double points[5][2]={{0,0},{width,0},{width,height},{0,height},{0,0}};
  for(int side=0;side<4;++side){double dz=(points[side+1][0]-points[side][0])/pieces,da=(points[side+1][1]-points[side][1])/pieces;for(unsigned i=0;i<pieces;++i){auto f=response(points[side][0]+(i+.5)*dz,points[side][1]+(i+.5)*da);double dw=f.first*dz+f.second*da;work+=dw;absoluteWork+=std::abs(dw);}}
  double z=width/2,angle=height/2,eps=1e-6;auto ap=response(z,angle+eps),am=response(z,angle-eps),up=response(z+eps,angle),um=response(z-eps,angle);double curl=(ap.first-am.first-up.second+um.second)/(2*eps);
  std::cout<<"CLOSED_WORK {\"proximal_frame_rotation\":"<<proximal<<",\"amplitude\":"<<amplitude<<",\"pieces\":"<<pieces<<",\"work\":"<<work<<",\"absolute_work\":"<<absoluteWork<<",\"normalized_work\":"<<(absoluteWork?work/absoluteWork:0)<<",\"cross_derivative_curl\":"<<curl<<"}"<<std::endl;
 }
 sofa::simulation::node::unload(root);root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
