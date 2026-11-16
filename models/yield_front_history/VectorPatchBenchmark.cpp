#include "VectorField.h"
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
#include <memory>
#include <optional>

// FIXED-PATCH ISOLATION BENCHMARK,not a 3D collision/grasp replacement.
// One Vec3 material displacement couples to an externally supported planar
// interface. Fixed normal z,capacity C(1-x*x),uniform displacement over x.
// No normal compliance,birth/death,rotations or hidden position correction.
class VectorPatchBenchmark final:public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types>{
public:
 using Types=sofa::defaulttype::Vec3Types;using Base=sofa::core::behavior::ForceField<Types>;
 SOFA_CLASS(VectorPatchBenchmark,Base);
 sofa::core::objectmodel::Data<double>halfLength,stiffness,capacity;
 sofa::core::objectmodel::Data<bool>velocityDirectedTangent;
 sofa::core::objectmodel::Data<std::string>filename;
 std::unique_ptr<regrip_vector_history::VectorField>field;
 std::array<double,3>frozen{},previous{};std::ofstream journal;
 unsigned begins=0,ends=0;long double cumulativeLoss=0;
 mutable std::optional<regrip_vector_history::VectorField::Trial>cached;
 mutable std::array<double,3>cachedX{};mutable std::size_t cachedEpoch=0;
 mutable std::array<double,3>cachedV{};bool frozenDirected=false;
 std::array<double,3>beginX{},beginV{};
 std::array<long double,17>beginMeasures{};
 explicit VectorPatchBenchmark(sofa::core::behavior::MechanicalState<Types>*s=nullptr):Base(s),
 halfLength(initData(&halfLength,.3192,"halfLength","Fixed material patch half length mm")),
 stiffness(initData(&stiffness,.001,"stiffness","Tangential line stiffness F/mm2")),
 capacity(initData(&capacity,3e-6,"capacity","Prescribed peak Coulomb capacity F/mm")),
 velocityDirectedTangent(initData(&velocityDirectedTangent,false,"velocityDirectedTangent","Explicit velocity-sided generalized derivative at positive yield")),
 filename(initData(&filename,std::string(""),"filename","Exclusive reference Commit journal")){
  if(s)mstate.set(s);
  f_listening.setValue(true);
 }
 std::array<double,3>parameters()const{return {halfLength.getValue(),stiffness.getValue(),capacity.getValue()};}
 void prepare(const VecCoord&x){
  if(x.size()!=1)throw std::invalid_argument("fixed-patch reference requires one Vec3 displacement");
  frozen=parameters();field=std::make_unique<regrip_vector_history::VectorField>(frozen[0],frozen[1]);
  frozenDirected=velocityDirectedTangent.getValue();
  cached.reset();
  regrip_vector_history::radialReturn({}, {},{0,0,1},frozen[1],frozen[2]);
  for(int j=0;j<3;++j){if(!std::isfinite(x[0][j]))throw std::invalid_argument("patch reference position");previous[j]=x[0][j];}
 }
 void init()override{
  Base::init();if(!mstate)throw std::runtime_error("patch reference missing state");
  prepare(mstate->read(sofa::core::vec_id::read_access::position)->getValue());
  if(filename.getValue().empty()||std::ifstream(filename.getValue()).good())throw std::runtime_error("refuse empty/existing patch journal");
  journal.open(filename.getValue());if(!journal)throw std::runtime_error("patch journal open");
  journal<<std::setprecision(18)<<"time,commit,x,y,fx,fy,old_energy,energy,loss,cumulative_loss,endpoint_projection,endpoint_work,energy_residual,evaluations,nonunique_samples,z,vx,vy,vz,begin_x,begin_y,begin_z,begin_vx,begin_vy,begin_vz,begin_fx,begin_fy,begin_fz";
  for(int i=0;i<9;++i)journal<<",begin_J"<<i;
  journal<<'\n';
 }
 regrip_vector_history::VectorField::Trial uncachedTrial(const VecCoord&x)const{
  if(!field||parameters()!=frozen||x.size()!=1)throw std::invalid_argument("patch reference changed topology/parameters");
  for(int j=0;j<3;++j)if(!std::isfinite(x[0][j]))throw std::invalid_argument("patch reference nonfinite position");
  // z is a normal-free DOF,not a hidden projective constraint. It is simply
  // excluded from a prescribed tangential-only benchmark's spring work.
  regrip_vector_history::Step step;step.capacity=frozen[2];step.increment[0]={x[0][0]-previous[0],x[0][1]-previous[1],0};
  regrip_vector_history::V direction{};
  if(frozenDirected){const auto&v=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();direction={v[0][0],v[0][1],0};}
  return field->evaluate(step,1e-7L,1e-30L,100000,direction);
 }
 regrip_vector_history::VectorField::Trial trial(const VecCoord&x)const{
  if(!field||parameters()!=frozen||x.size()!=1||velocityDirectedTangent.getValue()!=frozenDirected)throw std::invalid_argument("patch cache scope changed");
  std::array<double,3>position{x[0][0],x[0][1],x[0][2]};
  std::array<double,3>velocity{};if(frozenDirected){const auto&v=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();for(int j=0;j<3;++j)velocity[j]=v[0][j];}
  if(cached&&cachedEpoch==field->epoch()&&cachedX==position&&cachedV==velocity)return *cached;
  auto t=uncachedTrial(x);cached=t;cachedEpoch=field->epoch();cachedX=position;cachedV=velocity;return t;
 }
 void commit(const VecCoord&x){auto t=trial(x);const auto&v=t.integral.v;field->commit(t);cumulativeLoss+=v[2];
  cached.reset();
  for(int j=0;j<3;++j)previous[j]=x[0][j];
  if(journal){journal<<getContext()->getTime()<<','<<field->epoch()<<','<<previous[0]<<','<<previous[1]<<','<<-v[5]<<','<<-v[6]<<','<<v[0]<<','<<v[1]<<','<<v[2]<<','<<cumulativeLoss<<','<<v[3]<<','<<v[4]<<','<<v[1]-v[0]-v[4]+v[2]+v[3]<<','<<t.integral.evaluations<<','<<t.integral.nonuniqueSamples<<','<<previous[2];
   const auto&velocity=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
   for(int j=0;j<3;++j)journal<<','<<velocity[0][j];
   for(double z:beginX)journal<<','<<z;
   for(double z:beginV)journal<<','<<z;
   for(int j=0;j<3;++j)journal<<','<<-beginMeasures[5+j];
   for(int j=0;j<9;++j)journal<<','<<-beginMeasures[8+j];
   journal<<'\n';journal.flush();
  }
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(dynamic_cast<sofa::simulation::AnimateBeginEvent*>(event)){
   if(begins!=ends)throw std::runtime_error("duplicate begin");
   ++begins;
   const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();
   const auto&velocity=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
   for(int j=0;j<3;++j){beginX[j]=x[0][j];beginV[j]=velocity[0][j];}
   beginMeasures=trial(x).integral.v;
  }
  else if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)){if(ends+1!=begins)throw std::runtime_error("missing/duplicate end");commit(mstate->read(sofa::core::vec_id::read_access::position)->getValue());++ends;}
 }
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{
  auto t=trial(x.getValue());auto v=f.getValue();if(v.size()!=1)throw std::invalid_argument("patch force size");for(int j=0;j<3;++j)v[0][j]-=double(t.integral.v[5+j]);f.setValue(v);
 }
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{
  if(!p||df.getValue().size()!=1||dx.getValue().size()!=1)throw std::invalid_argument("patch dforce size/params");
  auto t=trial(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto v=df.getValue();double factor=p->kFactorIncludingRayleighDamping(rayleighStiffness.getValue());
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)v[0][i]-=factor*double(t.integral.v[8+3*i+j])*dx.getValue()[0][j];
  df.setValue(v);
 }
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{
  if(!m)throw std::invalid_argument("patch matrix");
  auto t=trial(mstate->read(sofa::core::vec_id::read_access::position)->getValue());
  auto a=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());if(!a)throw std::invalid_argument("patch accumulator");
  for(int i=0;i<3;++i)for(int j=0;j<3;++j)a(i,j)+=-double(t.integral.v[8+3*i+j]);
 }
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{
  // Stored elastic inventory only,NOT the incremental potential U+D.
  // Friction is history-dependent;generic conservative-energy claims invalid.
  return double(trial(x.getValue()).integral.v[1]);
 }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripVectorPatchReference";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Independent fixed-normal function-history benchmark,NOT collision/grasp").add<VectorPatchBenchmark>());}
}
