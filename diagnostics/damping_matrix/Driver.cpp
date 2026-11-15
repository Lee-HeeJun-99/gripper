#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/helper/system/FileRepository.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/behavior/Mass.h>
#include <sofa/core/behavior/LinearSolver.h>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/linearalgebra/BaseMatrix.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>
#include <stdexcept>
#include <string>
using Types=sofa::defaulttype::Rigid3Types;
using FF=sofa::core::behavior::ForceField<Types>;
using State=sofa::core::behavior::MechanicalState<Types>;
// Read the ACTUAL solved public MBK matrix,not a second force/Jacobian query.
// Projected mass must be constant in the restricted planar/Sphere scope;the
// offline assessment verifies this against the first captured mass matrix.
class Probe:public sofa::core::objectmodel::BaseObject{
public:
 SOFA_CLASS(Probe,sofa::core::objectmodel::BaseObject);
 State*state=nullptr;sofa::simulation::Node*root=nullptr;
 sofa::core::behavior::LinearSolver*solver=nullptr;
 std::vector<sofa::core::behavior::Mass<Types>*>masses;
 std::string prefix;double alpha=0,beta=0,beginTime=0;size_t next=0;
 std::vector<double>times{0,.5,.75,3,6,6.01,6.1,14,14.01,15,16,16.01,16.1,17};
 Probe(){f_listening.setValue(true);}
 void capture(){
  const unsigned nodes=state->getSize(),d=6*nodes;
  if(nodes>250||!solver->getLinearSystem())throw std::runtime_error("bounded public matrix scope");
  auto*A=solver->getLinearSystem()->getSystemBaseMatrix();
  if(!A||A->rowSize()!=int(d)||A->colSize()!=int(d))throw std::runtime_error("one-state matrix ordering/size assumption failed");
  std::vector<double>M(size_t(d)*d);sofa::core::MechanicalParams mp;Types::VecDeriv basis(nodes);
  for(unsigned c=0;c<d;++c){
   if(c)basis[(c-1)/6][(c-1)%6]=0;
   basis[c/6][c%6]=1;FF::DataVecDeriv input,output;
   input.setValue(basis);output.setValue(Types::VecDeriv(nodes));
   for(auto*m:masses)m->addMDx(&mp,output,input,1);
   const auto&v=output.getValue();
   for(unsigned r=0;r<d;++r)M[size_t(r)*d+c]=v[r/6][r%6];
  }
  std::string name=prefix+"_"+std::to_string(next)+".csv";
  std::ifstream old(name);if(old)throw std::runtime_error("refuse old damping matrix");
  std::ofstream out(name);if(!out)throw std::runtime_error("matrix output");
  out<<std::setprecision(17)<<"meta,"<<d<<','<<beginTime<<','<<root->getTime()<<','<<root->getDt()<<','<<alpha<<','<<beta<<'\n';
  for(unsigned r=0;r<d;++r)for(unsigned c=0;c<d;++c){
   double m=M[size_t(r)*d+c],a=A->element(r,c);
   if(!std::isfinite(m)||!std::isfinite(a))throw std::runtime_error("nonfinite actual MBK/mass");
   if(m)out<<"M,"<<r<<','<<c<<','<<m<<'\n';
   if(a)out<<"A,"<<r<<','<<c<<','<<a<<'\n';
  }
  if(!out)throw std::runtime_error("matrix write failure");
  std::cout<<"DAMPING_SNAPSHOT "<<next<<" actual_begin="<<std::setprecision(17)<<beginTime<<'\n';
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){beginTime=root->getTime();return;}
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||next>=times.size())return;
  double target=times[next],resolution=64*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(target));
  if(beginTime>=target-resolution){
   if(std::abs(beginTime-target)>.25*root->getDt())throw std::runtime_error("probe missed intended BEGIN epoch");
   capture();++next;
  }
 }
};
int main(int argc,char**argv){try{
 if(argc!=8)throw std::invalid_argument("SDK SCENE STEPS PREFIX FRAME BEAM CONTACT");
 int steps=std::stoi(argv[3]);if(steps<1||steps>96000)throw std::invalid_argument("bounded steps");
 sofa::simulation::graph::init();sofa::simpleapi::init();
 sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");
 sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");
 for(int i=5;i<8;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin");
 auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene");
 sofa::simulation::node::initRoot(root.get());if(root->getGravity().norm()!=0)throw std::runtime_error("zero gravity scope");
 auto*body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");
 auto probe=sofa::core::objectmodel::New<Probe>();probe->root=root.get();probe->prefix=argv[4];
 probe->state=dynamic_cast<State*>(body->getMechanicalState());if(!probe->state)throw std::runtime_error("rigid state");
 auto*context=static_cast<sofa::core::objectmodel::BaseContext*>(body);
 for(auto*m:context->getObjects<sofa::core::behavior::Mass<Types>>(sofa::core::objectmodel::BaseContext::Local))probe->masses.push_back(m);
 for(auto*f:context->getObjects<FF>(sofa::core::objectmodel::BaseContext::Local)){
  auto*r=f->findData("rayleighStiffness");if(r&&std::stod(r->getValueString())!=0)throw std::runtime_error("field-specific Rayleigh unsupported");
 }
 bool found=false;
 for(auto*o:context->getObjects<sofa::core::objectmodel::BaseObject>(sofa::core::objectmodel::BaseContext::SearchUp))if(o->getClassName()=="EulerImplicitSolver"){
  found=true;probe->alpha=std::stod(o->findData("rayleighMass")->getValueString());probe->beta=std::stod(o->findData("rayleighStiffness")->getValueString());
  for(auto key:{"firstOrder","trapezoidalScheme","solveConstraint","vdamping"}){auto s=o->findData(key)->getValueString();if(s!="0"&&s!="false")throw std::runtime_error("unsupported Euler matrix factors");}
 }
 for(auto*s:context->getObjects<sofa::core::behavior::LinearSolver>(sofa::core::objectmodel::BaseContext::SearchUp)){
  if(probe->solver)throw std::runtime_error("multiple systems");
  probe->solver=s;
 }
 if(!found||!probe->solver||probe->beta<=0)throw std::runtime_error("ODE/system coefficients absent");
 root->addObject(probe);
 for(int i=0;i<steps;++i)sofa::simulation::node::animate(root.get());
 std::cout<<"DAMPING_AUDIT steps="<<steps<<" snapshots="<<probe->next<<'\n';
 std::ofstream summary(std::string(argv[4])+"_summary.json");
 summary<<"{\"actual_steps\":"<<steps<<",\"actual_snapshots\":"<<probe->next<<"}\n";
 if(!summary)throw std::runtime_error("summary output");
 sofa::simulation::node::unload(root);probe.reset();root.reset();sofa::simulation::Simulation::theSimulation.reset();
 sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
 }catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
