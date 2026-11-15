#include <sofa/simpleapi/SimpleApi.h>
#include <sofa/simpleapi/init.h>
#include <sofa/simulation/graph/init.h>
#include <sofa/simulation/Node.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/helper/system/FileRepository.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/Mass.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/MechanicalParams.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <cmath>
#include <utility>
#ifdef REGRIP_NORMAL_AUDIT
#include "../contact_return_energy/Audit.h"
#endif
#ifdef REGRIP_FRAME_RETURN_AUDIT
#include "../contact_return_energy/FrameReturn.h"
#endif
using Types=sofa::defaulttype::Rigid3Types;using FF=sofa::core::behavior::ForceField<Types>;using State=sofa::core::behavior::MechanicalState<Types>;
struct Collector:sofa::core::behavior::StiffnessMatrixAccumulator{struct Entry{unsigned r,c;double value;};std::vector<Entry>entries;void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{if(v)entries.push_back({unsigned(r),unsigned(c),v});}void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}};
double inner(const Types::VecDeriv&a,const Types::VecDeriv&b){double v=0;for(unsigned i=0;i<a.size();++i)for(int j=0;j<6;++j)v+=a[i][j]*b[i][j];return v;}
class Journal:public sofa::core::objectmodel::BaseObject{
public:
 SOFA_CLASS(Journal,sofa::core::objectmodel::BaseObject);
 State*state=nullptr;sofa::simulation::Node*root=nullptr;std::vector<FF*>fields;std::vector<sofa::core::behavior::Mass<Types>*>masses;std::ofstream out;unsigned begins=0,ends=0,posts=0;Types::VecCoord x0;Types::VecDeriv external,actuator;double extWork=0,actWork=0,preContact=0,preLayer=0,maxCommitContact=0,maxCommitLayer=0;
 Journal(){f_listening.setValue(true);}
 Types::VecDeriv totalForce,v0,beamForce;Collector tangent,beamTangent;double beamEnergy0=0,beamQuadraticProjection=0,beamNonlinearRemainder=0;double initialK=0,alpha=2,beta=.1,kineticResidual=0,maxKineticResidual=0,massDamping=0,stiffnessDamping=0,velocityProjection=0;
 Types::VecDeriv layerForce;Collector layerTangent;double layerEnergy0=0,layerQuadraticProjection=0,layerNonlinearRemainder=0,normalQuadraticProjection=0,normalNonlinearRemainder=0;
 Collector actuatorTangent;double actuatorEulerWork=0,externalEulerWork=0;
 double contactPlastic=0,contactProjection=0,contactDetachment=0,materialSpringWork=0,maxReturnResidual=0;
 double frameReturnPlastic=0,frameReturnProjection=0,frameMaterialWork=0,maxFrameReturnResidual=0;
 double tangentBeginForceWork=0,tangentEulerJacobianWork=0,tangentMappedRemainder=0;
 double contactU0=0,groupedContactRemainder=0,groupedContactForceWork=0,groupedContactJacobianWork=0,normalEnergyChange=0;
 bool hasPostEnergy=false,returnEnergyReady=false;double cachedPostContact=0,preReturnPotential=0,maxEnergyReuseError=0;Types::VecCoord cachedPostX;unsigned energyReuseChecks=0;
 unsigned frameSnapshotChecks=0;double maxFrameSnapshotError=0;
 unsigned cableSnapshotChecks=0;double maxCableSnapshotError=0;
#ifdef REGRIP_CABLE_SNAPSHOT
 std::vector<std::pair<FF*,CableAssemblySnapshot>>cableSnapshots;
 const CableAssemblySnapshot&cableSnapshot(FF*f)const{for(const auto&x:cableSnapshots)if(x.first==f)return x.second;throw std::runtime_error("missing same-stage cable snapshot");}
#endif
#ifdef REGRIP_FRAME_SNAPSHOT
 std::vector<std::pair<FF*,FrameAssemblySnapshot>>frameSnapshots;
 std::vector<std::pair<FF*,double>>frameEndEnergies;
 const FrameAssemblySnapshot&frameSnapshot(FF*f)const{for(const auto&x:frameSnapshots)if(x.first==f)return x.second;throw std::runtime_error("missing same-stage frame snapshot");}
 double frameEndEnergy(FF*f)const{for(const auto&x:frameEndEnergies)if(x.first==f)return x.second;throw std::runtime_error("missing actual frame end energy");}
 void addSnapshot(FF::DataVecDeriv&f,Collector&matrix,const FrameAssemblySnapshot&s){auto*w=f.beginEdit();if(w->size()!=s.force.size())throw std::runtime_error("frame snapshot force size");for(unsigned i=0;i<w->size();++i)for(unsigned j=0;j<6;++j)(*w)[i][j]+=s.force[i][j];f.endEdit();for(const auto&t:s.jacobian)matrix.entries.push_back({t.r,t.c,t.value});}
#endif
 bool samePostPose(const Types::VecCoord&x)const{if(x.size()!=cachedPostX.size())return false;for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<7;++j)if(x[i][j]!=cachedPostX[i][j])return false;return true;}
#ifdef REGRIP_NORMAL_AUDIT
 FF*normalOwner=nullptr;NormalInventory normalBegin;
#endif
 void inventory(const char*stage){
  sofa::core::MechanicalParams mp;auto*x=state->read(sofa::core::vec_id::read_access::position);auto*v=state->read(sofa::core::vec_id::read_access::velocity);double beam=0,layer=0,contact=0,wire=0,K=0,layerPlastic=0;
  for(auto*f:fields)if(f->getClassName()=="FrameLayerNetwork"){auto*d=f->findData("dissipatedEnergy");if(!d)throw std::runtime_error("layer own dissipation Data absent");layerPlastic+=std::stod(d->getValueString());}
  for(auto*f:fields){auto name=f->getClassName();if(name=="ConservativeBeam")beam+=f->getPotentialEnergy(&mp,*x);else if(name=="FrameLayerNetwork"){
#ifdef REGRIP_FRAME_SNAPSHOT
   std::string stageName(stage);layer+=stageName=="begin"?frameSnapshot(f).energy:stageName=="pre_commit"?frameEndEnergy(f):f->getPotentialEnergy(&mp,*x);
#else
   layer+=f->getPotentialEnergy(&mp,*x);
#endif
  }else if(name=="CurvedMaterialContact"){
#ifdef REGRIP_VALUE_ENERGY
#ifdef REGRIP_REUSE_RETURN_ENERGY
   // Frozen one-owner contact has no time-varying parameters or Begin
   // mutators. Reuse ONLY at an identical post-commit pose and transaction,
   // or from the actual same-state return snapshot already queried below.
   double measured=0;bool reused=false;std::string stageName(stage);
   if(stageName=="begin"&&hasPostEnergy&&posts+1==begins&&samePostPose(x->getValue())){measured=cachedPostContact;reused=true;}
   else if(stageName=="pre_commit"&&returnEnergyReady){measured=preReturnPotential;reused=true;}
   else measured=curveReturnedEnergy(f);
   if(reused&&begins%1000==0){double actual=curveReturnedEnergy(f);maxEnergyReuseError=std::max(maxEnergyReuseError,std::abs(actual-measured));++energyReuseChecks;if(actual!=measured)throw std::runtime_error("same-state energy reuse is not bit-equivalent");}
   contact+=measured;
#else
   contact+=curveReturnedEnergy(f);
#endif
#else
   contact+=f->getPotentialEnergy(&mp,*x);
#endif
  }else if(name=="RoutedCable"){
#ifndef REGRIP_CABLE_SNAPSHOT
   wire+=f->getPotentialEnergy(&mp,*x);
#endif
  }else if(dynamic_cast<sofa::core::behavior::Mass<Types>*>(f)){if(root->getGravity().norm()!=0)throw std::runtime_error("nonzero gravity energy unsupported");}else if(name!="SpatialLoad")throw std::runtime_error("unidentified forcefield energy scope: "+std::string(name));}
  for(auto*m:masses)K+=m->getKineticEnergy(&mp,*v);for(double value:{beam,layer,contact,wire,K,extWork,actWork})if(!std::isfinite(value))throw std::runtime_error("nonfinite transaction inventory");
  if(std::string(stage)=="pre_commit"){preContact=contact;preLayer=layer;}
  if(std::string(stage)=="begin")contactU0=contact;
  if(std::string(stage)=="post_commit"){maxCommitContact=std::max(maxCommitContact,std::abs(contact-preContact));maxCommitLayer=std::max(maxCommitLayer,std::abs(layer-preLayer));}
#ifdef REGRIP_REUSE_RETURN_ENERGY
  if(std::string(stage)=="post_commit"){cachedPostContact=contact;cachedPostX=x->getValue();hasPostEnergy=true;}
#endif
#ifdef REGRIP_FRAME_RETURN_AUDIT
  if(std::string(stage)=="post_commit"&&std::abs(layerPlastic-frameReturnPlastic)>1e-18)throw std::runtime_error("frame return audit differs from actual committed loss");
#endif
  out<<root->getTime()<<','<<begins<<','<<stage<<','<<beam<<','<<layer<<','<<contact<<',';
#ifdef REGRIP_CABLE_SNAPSHOT
  out<<"null,"; // Optional T*L virtual gauge is not stored energy here.
#else
  out<<wire<<',';
#endif
  out<<K<<','<<extWork<<','<<actWork<<','<<massDamping<<','<<stiffnessDamping<<','<<velocityProjection<<','<<kineticResidual<<','<<beamQuadraticProjection<<','<<beamNonlinearRemainder<<','<<layerQuadraticProjection<<','<<layerNonlinearRemainder<<',';
#ifdef REGRIP_GROUPED_CONTACT
  out<<"null,null,"; // Intentionally not used in this algebraic grouping.
#else
  out<<normalQuadraticProjection<<','<<normalNonlinearRemainder<<',';
#endif
  out<<actuatorEulerWork<<','<<externalEulerWork<<','<<contactPlastic<<','<<contactProjection<<','<<contactDetachment<<','<<materialSpringWork<<','<<maxReturnResidual<<','<<layerPlastic<<','<<frameReturnPlastic<<','<<frameReturnProjection<<','<<frameMaterialWork<<','<<maxFrameReturnResidual<<',';
#ifdef REGRIP_GROUPED_CONTACT
  out<<"null,null,null,";
#else
  out<<tangentBeginForceWork<<','<<tangentEulerJacobianWork<<','<<tangentMappedRemainder<<',';
#endif
#ifdef REGRIP_GROUPED_CONTACT
  out<<groupedContactForceWork<<','<<groupedContactJacobianWork<<','<<normalEnergyChange<<','<<groupedContactRemainder<<',';
#else
  out<<"null,null,null,null,";
#endif
  out<<"null,null\n";
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){
   if(begins!=posts)throw std::runtime_error("duplicate/missing begin transaction");++begins;returnEnergyReady=false;auto*x=state->read(sofa::core::vec_id::read_access::position);auto*v=state->read(sofa::core::vec_id::read_access::velocity);x0=x->getValue();FF::DataVecDeriv a,e;a.setValue(Types::VecDeriv(x0.size()));e.setValue(Types::VecDeriv(x0.size()));sofa::core::MechanicalParams mp;
   FF::DataVecDeriv all;all.setValue(Types::VecDeriv(x0.size()));tangent.entries.clear();sofa::core::behavior::StiffnessMatrix matrix;matrix.setMatrixAccumulator(&tangent,state);
   beamTangent.entries.clear();sofa::core::behavior::StiffnessMatrix beamMatrix;beamMatrix.setMatrixAccumulator(&beamTangent,state);FF::DataVecDeriv bf;bf.setValue(Types::VecDeriv(x0.size()));beamEnergy0=0;
   layerTangent.entries.clear();sofa::core::behavior::StiffnessMatrix layerMatrix;layerMatrix.setMatrixAccumulator(&layerTangent,state);FF::DataVecDeriv lf;lf.setValue(Types::VecDeriv(x0.size()));layerEnergy0=0;
   actuatorTangent.entries.clear();sofa::core::behavior::StiffnessMatrix actuatorMatrix;actuatorMatrix.setMatrixAccumulator(&actuatorTangent,state);
#ifdef REGRIP_CABLE_SNAPSHOT
   cableSnapshots.clear();
#endif
   for(auto*f:fields)if(f->getClassName()=="RoutedCable"){
#ifdef REGRIP_CABLE_SNAPSHOT
    cableSnapshots.push_back({f,snapshotCableAssembly(f,x0)});const auto&s=cableSnapshots.back().second;addSnapshot(a,actuatorTangent,s);
    if(begins%1000==0){
     FF::DataVecDeriv actual;actual.setValue(Types::VecDeriv(x0.size()));Collector actualJ;sofa::core::behavior::StiffnessMatrix actualMatrix;actualMatrix.setMatrixAccumulator(&actualJ,state);f->addForce(&mp,actual,*x,*v);f->buildStiffnessMatrix(&actualMatrix);
     if(actualJ.entries.size()!=s.jacobian.size()||f->getPotentialEnergy(&mp,*x)!=s.energy)throw std::runtime_error("cable public snapshot energy/J shape mismatch");
     for(unsigned i=0;i<s.force.size();++i)for(unsigned j=0;j<6;++j)maxCableSnapshotError=std::max(maxCableSnapshotError,std::abs(actual.getValue()[i][j]-s.force[i][j]));
     for(unsigned i=0;i<s.jacobian.size();++i){auto u=actualJ.entries[i];auto w=s.jacobian[i];if(u.r!=w.r||u.c!=w.c)throw std::runtime_error("cable snapshot J ordering mismatch");maxCableSnapshotError=std::max(maxCableSnapshotError,std::abs(u.value-w.value));}
     ++cableSnapshotChecks;if(maxCableSnapshotError!=0)throw std::runtime_error("cable public snapshot differs from actual force/J APIs");
    }
#else
    f->buildStiffnessMatrix(&actuatorMatrix);
#endif
   }
#ifdef REGRIP_FRAME_SNAPSHOT
   frameSnapshots.clear();frameEndEnergies.clear();
#endif
   for(auto*f:fields)if(f->getClassName()=="FrameLayerNetwork"){
#ifdef REGRIP_FRAME_SNAPSHOT
    frameSnapshots.push_back({f,snapshotFrameAssembly(f,x0)});const auto&s=frameSnapshots.back().second;addSnapshot(lf,layerTangent,s);layerEnergy0+=s.energy;
    if(begins%1000==0){
     FF::DataVecDeriv actual;actual.setValue(Types::VecDeriv(x0.size()));Collector actualJ;sofa::core::behavior::StiffnessMatrix actualMatrix;actualMatrix.setMatrixAccumulator(&actualJ,state);f->addForce(&mp,actual,*x,*v);f->buildStiffnessMatrix(&actualMatrix);
     if(actualJ.entries.size()!=s.jacobian.size()||f->getPotentialEnergy(&mp,*x)!=s.energy)throw std::runtime_error("frame public snapshot energy/J shape mismatch");
     for(unsigned i=0;i<s.force.size();++i)for(unsigned j=0;j<6;++j)maxFrameSnapshotError=std::max(maxFrameSnapshotError,std::abs(actual.getValue()[i][j]-s.force[i][j]));
     for(unsigned i=0;i<s.jacobian.size();++i){auto a=actualJ.entries[i];auto b=s.jacobian[i];if(a.r!=b.r||a.c!=b.c)throw std::runtime_error("frame snapshot J ordering mismatch");maxFrameSnapshotError=std::max(maxFrameSnapshotError,std::abs(a.value-b.value));}
     ++frameSnapshotChecks;if(maxFrameSnapshotError!=0)throw std::runtime_error("frame public snapshot differs from actual ForceField APIs");
    }
#else
    f->addForce(&mp,lf,*x,*v);f->buildStiffnessMatrix(&layerMatrix);layerEnergy0+=f->getPotentialEnergy(&mp,*x);
#endif
   }layerForce=lf.getValue();
#ifdef REGRIP_NORMAL_AUDIT
   for(auto*f:fields)if(f->getClassName()=="CurvedMaterialContact")normalOwner=f;if(!normalOwner)throw std::runtime_error("normal potential scope");
#ifndef REGRIP_GROUPED_CONTACT
   normalBegin=curveNormalSnapshot(normalOwner);
#endif
#endif
   for(auto*f:fields){auto name=f->getClassName();if(name=="RoutedCable"){
#ifndef REGRIP_CABLE_SNAPSHOT
    f->addForce(&mp,a,*x,*v);
#endif
   }else if(name=="SpatialLoad")f->addForce(&mp,e,*x,*v);if(name=="ConservativeBeam"){f->addForce(&mp,bf,*x,*v);f->buildStiffnessMatrix(&beamMatrix);beamEnergy0+=f->getPotentialEnergy(&mp,*x);}
#ifdef REGRIP_FRAME_SNAPSHOT
    if(name=="FrameLayerNetwork")addSnapshot(all,tangent,frameSnapshot(f));else
#endif
#ifdef REGRIP_CABLE_SNAPSHOT
    if(name=="RoutedCable")addSnapshot(all,tangent,cableSnapshot(f));else
#endif
    {f->addForce(&mp,all,*x,*v);f->buildStiffnessMatrix(&matrix);}
   }beamForce=bf.getValue();external=e.getValue();actuator=a.getValue();totalForce=all.getValue();v0=v->getValue();initialK=0;for(auto*m:masses)initialK+=m->getKineticEnergy(&mp,*v);inventory("begin");
  }else if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)){
   if(ends+1!=begins)throw std::runtime_error("duplicate/missing end transaction");++ends;const auto&x=state->read(sofa::core::vec_id::read_access::position)->getValue();
   for(unsigned i=0;i<x.size();++i){auto translation=x[i].getCenter()-x0[i].getCenter();auto rotation=(x[i].getOrientation()*x0[i].getOrientation().inverse()).quatToRotationVector();for(int j=0;j<3;++j){extWork+=external[i][j]*translation[j]+external[i][j+3]*rotation[j];actWork+=actuator[i][j]*translation[j]+actuator[i][j+3]*rotation[j];}}
   auto*v=state->read(sofa::core::vec_id::read_access::velocity);const auto&v1=v->getValue();auto dv=v1;for(unsigned i=0;i<dv.size();++i)dv[i]-=v0[i];FF::DataVecDeriv velocity,difference,Mv,Mdv;velocity.setValue(v1);difference.setValue(dv);Mv.setValue(Types::VecDeriv(v1.size()));Mdv.setValue(Types::VecDeriv(v1.size()));sofa::core::MechanicalParams mp;double K1=0;for(auto*m:masses){m->addMDx(&mp,Mv,velocity,1);m->addMDx(&mp,Mdv,difference,1);K1+=m->getKineticEnergy(&mp,*v);}double vJv=0;for(const auto&t:tangent.entries)vJv+=v1[t.r/6][t.r%6]*t.value*v1[t.c/6][t.c%6];double h=root->getDt();double dm=h*alpha*inner(v1,Mv.getValue()),ds=-h*beta*vJv,dvLoss=.5*inner(dv,Mdv.getValue());massDamping+=dm;stiffnessDamping+=ds;velocityProjection+=dvLoss;
   double vJbeamv=0,beamEnergy1=0;for(const auto&t:beamTangent.entries)vJbeamv+=v1[t.r/6][t.r%6]*t.value*v1[t.c/6][t.c%6];for(auto*f:fields)if(f->getClassName()=="ConservativeBeam")beamEnergy1+=f->getPotentialEnergy(&mp,*state->read(sofa::core::vec_id::read_access::position));beamQuadraticProjection-=.5*h*h*vJbeamv;beamNonlinearRemainder+=beamEnergy1-beamEnergy0+h*inner(beamForce,v1)+.5*h*h*vJbeamv;
   double vJlayerv=0,layerEnergy1=0;for(const auto&t:layerTangent.entries)vJlayerv+=v1[t.r/6][t.r%6]*t.value*v1[t.c/6][t.c%6];for(auto*f:fields)if(f->getClassName()=="FrameLayerNetwork"){
    double measured=f->getPotentialEnergy(&mp,*state->read(sofa::core::vec_id::read_access::position));layerEnergy1+=measured;
#ifdef REGRIP_FRAME_SNAPSHOT
    frameEndEnergies.push_back({f,measured});
#endif
   }layerQuadraticProjection-=.5*h*h*vJlayerv;layerNonlinearRemainder+=layerEnergy1-layerEnergy0+h*inner(layerForce,v1)+.5*h*h*vJlayerv;
   double vJactuatorv=0;for(const auto&t:actuatorTangent.entries)vJactuatorv+=v1[t.r/6][t.r%6]*t.value*v1[t.c/6][t.c%6];actuatorEulerWork+=h*inner(actuator,v1)+h*h*vJactuatorv;externalEulerWork+=h*inner(external,v1);
#ifdef REGRIP_NORMAL_AUDIT
#ifndef REGRIP_GROUPED_CONTACT
   double vJnormalv=0;for(const auto&t:normalBegin.jacobian)vJnormalv+=v1[t.r/6][t.r%6]*t.value*v1[t.c/6][t.c%6];normalQuadraticProjection-=.5*h*h*vJnormalv;normalNonlinearRemainder+=curveNormalEnergy(normalOwner)-normalBegin.energy+h*inner(normalBegin.force,v1)+.5*h*h*vJnormalv;
#endif
   auto contactReturn=auditCurveReturn(normalOwner);contactPlastic+=contactReturn.plastic;contactProjection+=contactReturn.projection;contactDetachment+=contactReturn.detachment;materialSpringWork+=contactReturn.endpointWork;maxReturnResidual=std::max(maxReturnResidual,std::abs(contactReturn.residual));
   preReturnPotential=contactReturn.totalPotentialEnergy;returnEnergyReady=true;
#ifdef REGRIP_GROUPED_CONTACT
   // R_c=Delta U_normal+W_material+h*f_contact0.v+h^2*v.J_contact0.v.
   // This equals R_normal-P_normal+R_tangent in the split journal;it
   // avoids an EXTRA normal Jacobian query,not any production force/J.
   double normalDelta=(contactReturn.totalPotentialEnergy-contactReturn.newEnergy)-(contactU0-contactReturn.oldEnergy);
   double fcWork=h*(inner(totalForce,v1)-inner(beamForce,v1)-inner(layerForce,v1)-inner(actuator,v1)-inner(external,v1));
   double jcWork=h*h*(vJv-vJbeamv-vJlayerv-vJactuatorv);
   normalEnergyChange+=normalDelta;groupedContactForceWork+=fcWork;groupedContactJacobianWork+=jcWork;
   groupedContactRemainder+=normalDelta+contactReturn.endpointWork+fcWork+jcWork;
#else
   // Independently compare actual mapped BEGIN force/Jacobian work with
   // material endpoint spring work. This is a signed discretization/transport
   // remainder,NOT invented heat or a residual of the total energy ledger.
   double ftWork=h*(inner(totalForce,v1)-inner(beamForce,v1)-inner(layerForce,v1)-inner(actuator,v1)-inner(external,v1)-inner(normalBegin.force,v1));
   double jtWork=h*h*(vJv-vJbeamv-vJlayerv-vJactuatorv-vJnormalv);
   tangentBeginForceWork+=ftWork;tangentEulerJacobianWork+=jtWork;
   tangentMappedRemainder+=contactReturn.endpointWork+ftWork+jtWork;
#endif
#endif
#ifdef REGRIP_FRAME_RETURN_AUDIT
   for(auto*f:fields)if(f->getClassName()=="FrameLayerNetwork"){auto r=auditFrameReturn(f,x0);frameReturnPlastic+=r.plastic;frameReturnProjection+=r.projection;frameMaterialWork+=r.endpointWork;maxFrameReturnResidual=std::max(maxFrameReturnResidual,std::abs(r.residual));}
#endif
   kineticResidual=(K1-initialK)-h*inner(totalForce,v1)-h*h*vJv+dm+ds+dvLoss;maxKineticResidual=std::max(maxKineticResidual,std::abs(kineticResidual));inventory("pre_commit");
  }
 }
 void post(){if(posts+1!=ends)throw std::runtime_error("post-commit ordering");++posts;inventory("post_commit");out.flush();}
};
int main(int argc,char**argv){try{
 if(argc!=8&&argc!=9)throw std::invalid_argument("SDK SCENE STEPS OUTPUT FRAME BEAM CONTACT [after_structural_compensation]");if(argc==9&&std::string(argv[8])!="after_structural_compensation")throw std::invalid_argument("unknown observation stage");int steps=std::stoi(argv[3]);if(steps<1||steps>160000)throw std::invalid_argument("bounded transaction steps");std::ifstream exists(argv[4]);if(exists)throw std::runtime_error("refuse old journal");
 sofa::simulation::graph::init();sofa::simpleapi::init();sofa::helper::system::PluginRepository.addFirstPath(std::string(argv[1])+"/lib");sofa::simulation::Simulation::theSimulation=sofa::simpleapi::createSimulation("DAG");for(int i=5;i<8;++i)if(!sofa::simpleapi::importPlugin(argv[i]))throw std::runtime_error("plugin");auto root=sofa::simulation::node::load(argv[2]);if(!root)throw std::runtime_error("scene");sofa::simulation::node::initRoot(root.get());auto*body=root->getChild("Multilayer");if(!body)throw std::runtime_error("body");auto journal=sofa::core::objectmodel::New<Journal>();journal->root=root.get();journal->state=dynamic_cast<State*>(body->getMechanicalState());if(!journal->state)throw std::runtime_error("rigid state");auto*ctx=static_cast<sofa::core::objectmodel::BaseContext*>(body);
 for(auto*f:ctx->getObjects<FF>(sofa::core::objectmodel::BaseContext::Local))journal->fields.push_back(f);for(auto*m:ctx->getObjects<sofa::core::behavior::Mass<Types>>(sofa::core::objectmodel::BaseContext::Local))journal->masses.push_back(m);
#ifdef REGRIP_REUSE_RETURN_ENERGY
 unsigned contactOwners=0;for(auto*f:journal->fields)if(f->getClassName()=="CurvedMaterialContact")++contactOwners;if(contactOwners!=1)throw std::runtime_error("energy reuse supports exactly one frozen contact owner");
#endif
#ifndef REGRIP_NORMAL_AUDIT
 for(auto*f:journal->fields)if(f->getClassName()=="CurvedMaterialContact")throw std::runtime_error("v8 curved energy journal requires compiled normal/return audit;missing terms are not zero");
#endif
 bool odeFound=false;for(auto*object:ctx->getObjects<sofa::core::objectmodel::BaseObject>(sofa::core::objectmodel::BaseContext::SearchUp))if(object->getClassName()=="EulerImplicitSolver"){odeFound=true;for(auto name:{"firstOrder","trapezoidalScheme","solveConstraint","vdamping"}){auto*d=object->findData(name);if(!d||(d->getValueString()!="0"&&d->getValueString()!="false"))throw std::runtime_error("unsupported Euler option");}journal->alpha=std::stod(object->findData("rayleighMass")->getValueString());journal->beta=std::stod(object->findData("rayleighStiffness")->getValueString());}if(!odeFound)throw std::runtime_error("Euler scope");
 journal->out.open(argv[4]);if(!journal->out)throw std::runtime_error("journal output");journal->out<<std::setprecision(17)<<"time,step,stage,beam_U,layer_U,contact_U,wire_virtual_not_storage,K,external_begin_force_work,actuator_begin_force_work,Rayleigh_mass_work,Rayleigh_stiffness_work,derived_velocity_projection_loss,kinetic_algorithmic_step_residual,derived_beam_quadratic_projection,beam_nonlinear_remainder,layer_quadratic_projection,layer_nonlinear_or_return_remainder,normal_quadratic_projection,normal_nonlinear_remainder,derived_actuator_Euler_work,derived_external_Euler_work,contact_plastic,contact_endpoint_projection,contact_detachment,material_spring_endpoint_work,max_material_return_residual,layer_plastic,frame_return_plastic,frame_return_projection,frame_material_endpoint_work,max_frame_return_residual,tangent_begin_force_work,tangent_Euler_J_work,tangent_mapped_endpoint_remainder,grouped_contact_begin_work,grouped_contact_Euler_J_work,normal_energy_change,grouped_contact_mapped_remainder,unknown_pressure_work,unknown_total_closure\n";
 if(argc==9){
  sofa::core::objectmodel::BaseComponent::SPtr compensation;for(auto obj:body->object)if(obj->getClassName()=="CompensatedBeamTranslations"){if(compensation)throw std::runtime_error("multiple structural arithmetic owners");compensation=obj;}
  if(!compensation)throw std::runtime_error("structural arithmetic stage missing");
  // Public scene APIs only. Keep every forcefield in its original order.
  // Initialization is already complete;retain the same live helper instance.
  if(!body->removeObject(compensation)||!body->addObject(journal,sofa::core::objectmodel::TypeOfInsertion::AtBegin)||!body->addObject(compensation,sofa::core::objectmodel::TypeOfInsertion::AtBegin))throw std::runtime_error("public observer insertion failed");
  if(body->object[0].get()!=compensation.get()||body->object[1].get()!=journal.get())throw std::runtime_error("observer stage ordering");
 }else root->addObject(journal);
 for(int i=0;i<steps;++i){sofa::simulation::node::animate(root.get());journal->post();}
 std::cout<<std::setprecision(17)<<"TRANSACTIONS {\"begins\":"<<journal->begins<<",\"pre_commits\":"<<journal->ends<<",\"post_commits\":"<<journal->posts<<",\"max_contact_commit_energy_jump\":"<<journal->maxCommitContact<<",\"max_layer_commit_energy_jump\":"<<journal->maxCommitLayer<<",\"max_kinetic_algorithmic_residual\":"<<journal->maxKineticResidual<<",\"same_state_energy_reuse_checks\":"<<journal->energyReuseChecks<<",\"max_same_state_energy_reuse_error\":"<<journal->maxEnergyReuseError<<",\"frame_snapshot_equivalence_checks\":"<<journal->frameSnapshotChecks<<",\"max_frame_snapshot_error\":"<<journal->maxFrameSnapshotError<<",\"cable_snapshot_equivalence_checks\":"<<journal->cableSnapshotChecks<<",\"max_cable_snapshot_error\":"<<journal->maxCableSnapshotError<<"}\n";sofa::simulation::node::unload(root);journal.reset();root.reset();sofa::simulation::Simulation::theSimulation.reset();sofa::simpleapi::cleanup();sofa::simulation::graph::cleanup();return 0;
}catch(const std::exception&e){std::cerr<<"[ERROR] "<<e.what()<<'\n';return 1;}}
