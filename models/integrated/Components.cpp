#include "Kernels.h"
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <sofa/core/objectmodel/BaseContext.h>
#include <fstream>
#include <iomanip>
namespace regrip_integrated {
using Types=sofa::defaulttype::Rigid3Types;using Inherit=sofa::core::behavior::ForceField<Types>;
struct Triplet{unsigned r,c;double v;};
struct Assembly{std::vector<double>f;std::vector<Triplet>J;double energy=0,slip=0,cableLength=0,tension=0,contacts=0,contactForce=0;explicit Assembly(size_t nodes):f(6*nodes,0){}};
class EnergyField:public Inherit{
public:
 SOFA_CLASS(EnergyField,Inherit);
 explicit EnergyField(sofa::core::behavior::MechanicalState<Types>*s=nullptr):Inherit(s){if(s)mstate.set(s);}
 bool reported=false;
 void fail(const char*why){if(!reported){msg_error()<<why;reported=true;}d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);}
 static Pose pose(const Types::Coord&x){Pose p;for(int i=0;i<3;++i)p.p[i]=x.getCenter()[i];for(int i=0;i<4;++i)p.q[i]=x.getOrientation()[i];validate(p);return p;}
 virtual Assembly assemble(const VecCoord&x)const=0;
 void check(const Assembly&a,size_t nodes)const{if(a.f.size()!=6*nodes||!std::isfinite(a.energy))throw std::invalid_argument("assembly size/energy");for(double v:a.f)if(!std::isfinite(v))throw std::overflow_error("nonfinite force");for(auto&t:a.J)if(t.r>=a.f.size()||t.c>=a.f.size()||!std::isfinite(t.v))throw std::invalid_argument("invalid matrix entry");}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&)override{
  try{auto a=assemble(x.getValue());check(a,x.getValue().size());if(f.getValue().size()!=x.getValue().size())throw std::invalid_argument("force size");
   auto*w=f.beginEdit();for(size_t j=0;j<a.f.size();++j)(*w)[j/6][j%6]+=a.f[j];f.endEdit();}catch(const std::exception&e){fail(e.what());}}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{
  try{if(!p||!mstate||!std::isfinite(p->kFactor()))throw std::invalid_argument("missing mechanical parameters/state");const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();auto a=assemble(x);check(a,x.size());
   if(dx.getValue().size()!=x.size()||df.getValue().size()!=x.size())throw std::invalid_argument("dforce size");
   std::vector<double>v(a.f.size());for(auto&t:a.J)v[t.r]+=p->kFactor()*t.v*dx.getValue()[t.c/6][t.c%6];
   for(double z:v)if(!std::isfinite(z))throw std::invalid_argument("nonfinite differential input/output");
   auto*w=df.beginEdit();for(size_t j=0;j<v.size();++j)(*w)[j/6][j%6]+=v[j];df.endEdit();}catch(const std::exception&e){fail(e.what());}}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{
  try{if(!m||!mstate)throw std::invalid_argument("missing matrix/state");const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();auto a=assemble(x);check(a,x.size());auto acc=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());if(!acc)throw std::invalid_argument("missing accumulator");for(auto&t:a.J)acc(t.r,t.c)+=t.v;}catch(const std::exception&e){fail(e.what());}}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{try{return assemble(x.getValue()).energy;}catch(...){return std::numeric_limits<double>::quiet_NaN();}}
 void pair(Assembly&a,unsigned l,unsigned u,const Result&r)const{a.energy+=r.energy;for(int j=0;j<12;++j){unsigned row=6*(j<6?l:u)+j%6;a.f[row]+=r.force[j];for(int k=0;k<12;++k)if(r.jacobian[12*j+k]!=0)a.J.push_back({row,6*(k<6?l:u)+unsigned(k%6),r.jacobian[12*j+k]});}}
};
double schedule(double t,const sofa::type::vector<double>&times,const sofa::type::vector<double>&values,double fallback){
 if(times.empty()&&values.empty())return fallback;
 if(times.size()!=values.size())throw std::invalid_argument("schedule size");
 for(size_t i=0;i<times.size();++i)if(!std::isfinite(times[i])||!std::isfinite(values[i])||(i&&times[i]<=times[i-1]))throw std::invalid_argument("schedule values/order");
 double v=fallback;for(size_t i=0;i<times.size()&&t>=times[i]-1e-12;++i)v=values[i];return v;
}
class LayerNetwork final:public EnergyField{
public:
 SOFA_CLASS(LayerNetwork,EnergyField);
 sofa::core::objectmodel::Data<unsigned> nodes,layers,start,mode;
 sofa::core::objectmodel::Data<double> stiffness,height,normalStiffness,pressure,mu,width,length;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> connectors;
 sofa::core::objectmodel::Data<sofa::type::vector<double>> times,pressures;
 mutable std::vector<double>plastic;double dissipated=0;
 explicit LayerNetwork(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),
 nodes(initData(&nodes,11u,"nodesPerLayer","Nodes per beam")),layers(initData(&layers,2u,"layers","Layer count")),start(initData(&start,0u,"startIndex","First node")),mode(initData(&mode,0u,"mode","0 planar spring, 1 prescribed-pressure slider, 2 finite3D spring")),
 stiffness(initData(&stiffness,1.,"stiffness","Point shear stiffness")),height(initData(&height,.4,"height","Centroid separation")),normalStiffness(initData(&normalStiffness,0.,"normalStiffness","Optional linear normal confinement, independent of prescribed pressure")),
 pressure(initData(&pressure,0.,"pressure","Prescribed normal pressure; not solved vacuum")),mu(initData(&mu,.3,"mu","Equal static/kinetic research coefficient")),width(initData(&width,8.,"width","Assumed pressure tributary width")),length(initData(&length,100.,"length","Length mm")),
 connectors(initData(&connectors,"connectorIndices","Empty=all nonroot nodes")),times(initData(&times,"pressureTimes","Step schedule times")),pressures(initData(&pressures,"pressureValues","Step pressures")){f_listening.setValue(true);}
 std::vector<unsigned>ids()const{std::vector<unsigned>v(connectors.getValue().begin(),connectors.getValue().end());if(v.empty())for(unsigned i=1;i<nodes.getValue();++i)v.push_back(i);std::sort(v.begin(),v.end());for(size_t j=0;j<v.size();++j)if(v[j]==0||v[j]>=nodes.getValue()||(j&&v[j]==v[j-1]))throw std::invalid_argument("connector selection");return v;}
 double currentPressure()const{return schedule(getContext()?getContext()->getTime():0,times.getValue(),pressures.getValue(),pressure.getValue());}
 void init()override{EnergyField::init();try{if(!mstate||layers.getValue()<2||layers.getValue()>8)throw std::invalid_argument("missing state/invalid layer count");plastic.assign((layers.getValue()-1)*ids().size(),0);assemble(mstate->read(sofa::core::vec_id::read_access::position)->getValue());}catch(const std::exception&e){fail(e.what());}}
 Assembly assemble(const VecCoord&x)const override{
  const unsigned n=nodes.getValue(),L=layers.getValue(),offset=start.getValue();double k=stiffness.getValue(),h=height.getValue(),kn=normalStiffness.getValue(),p=currentPressure();
  if(n<3||L<2||L>8||n>41||offset+size_t(n)*L>x.size()||!std::isfinite(k)||k<0||!std::isfinite(h)||h<=0||!std::isfinite(kn)||kn<0||!std::isfinite(p)||p<0||!std::isfinite(mu.getValue())||mu.getValue()<0||!std::isfinite(width.getValue())||width.getValue()<=0||!std::isfinite(length.getValue())||length.getValue()<=0||mode.getValue()>2||(mode.getValue()==1&&k==0))throw std::invalid_argument("layer parameters");
  auto selected=ids();Assembly a(x.size());size_t count=0;
  if(mode.getValue()==1&&plastic.size()!=(L-1)*selected.size())throw std::invalid_argument("uninitialized friction history");
  for(unsigned layer=0;layer<L-1;++layer)for(size_t j=0;j<selected.size();++j){unsigned i=selected[j],l=offset+layer*n+i,u=l+n;Pose pl=pose(x[l]),pu=pose(x[u]);
   if(mode.getValue()==2){auto r=evaluate(pl,pu,k,h);pair(a,l,u,r);a.slip=std::max(a.slip,std::abs(r.slip));}
   else{
    for(auto&q:{pl.q,pu.q})if(std::abs(q[0])>1e-8||std::abs(q[2])>1e-8||q[3]<=0||2*std::atan2(std::abs(q[1]),q[3])>=.005)throw std::invalid_argument("outside small planar layer domain");
    double s=pu.p[0]-pl.p[0]-h*(std::atan2(pl.q[1],pl.q[3])+std::atan2(pu.q[1],pu.q[3]));double traction=k*s,tangent=k,energy=.5*k*s*s;
    if(mode.getValue()==1){double left=j==0?0.:.5*(selected[j-1]+i)*length.getValue()/(n-1);double right=j+1==selected.size()?length.getValue():.5*(i+selected[j+1])*length.getValue()/(n-1);auto r=slider(s,plastic[count],k,mu.getValue()*p*width.getValue()*(right-left));traction=r.traction;tangent=r.tangent;energy=r.energy;}
    unsigned rows[4]={6*l,6*l+4,6*u,6*u+4};double b[4]={-1,-h/2,1,-h/2};a.energy+=energy;a.slip=std::max(a.slip,std::abs(s));
    for(int r=0;r<4;++r){a.f[rows[r]]-=traction*b[r];for(int c=0;c<4;++c)a.J.push_back({rows[r],rows[c],-tangent*b[r]*b[c]});}
   }
   if(kn){double gap=pu.p[2]-pl.p[2]-h;a.f[6*l+2]+=kn*gap;a.f[6*u+2]-=kn*gap;a.energy+=.5*kn*gap*gap;for(int r=0;r<2;++r)for(int c=0;c<2;++c)a.J.push_back({6*(r?u:l)+2,6*(c?u:l)+2,r==c?-kn:kn});}
   ++count;
  }return a;
 }
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||mode.getValue()!=1||!mstate)return;
  try{const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();assemble(x);auto selected=ids();size_t c=0;unsigned n=nodes.getValue();double h=height.getValue();
   for(unsigned l=0;l<layers.getValue()-1;++l)for(size_t j=0;j<selected.size();++j){unsigned i=selected[j],a=start.getValue()+l*n+i,b=a+n;auto pa=pose(x[a]),pb=pose(x[b]);double slip=pb.p[0]-pa.p[0]-h*(std::atan2(pa.q[1],pa.q[3])+std::atan2(pb.q[1],pb.q[3]));
    double left=j? .5*(selected[j-1]+i)*length.getValue()/(n-1):0.,right=j+1==selected.size()?length.getValue():.5*(i+selected[j+1])*length.getValue()/(n-1);
    auto r=slider(slip,plastic[c],stiffness.getValue(),mu.getValue()*currentPressure()*width.getValue()*(right-left));plastic[c++]=r.plastic;dissipated+=r.dissipation;}
  }catch(const std::exception&e){fail(e.what());}
 }
};
class RoutedCable final:public EnergyField{
public:
 SOFA_CLASS(RoutedCable,EnergyField);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> route;
 sofa::core::objectmodel::Data<double> offset,stiffness,shortening,tension;
 sofa::core::objectmodel::Data<sofa::type::vector<double>> times,commands;
 double restLength=0;
 explicit RoutedCable(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),
 route(initData(&route,"route","Ordered rigid guide indices")),offset(initData(&offset,-.2,"offsetZ","Material guide offset")),stiffness(initData(&stiffness,0.,"stiffness","0 prescribed tension, >0 tension-only length spring")),
 shortening(initData(&shortening,0.,"shortening","Rest-length contraction mm")),tension(initData(&tension,0.,"tension","Prescribed tension when stiffness=0")),times(initData(&times,"commandTimes","Step schedule")),commands(initData(&commands,"commandValues","Tension or shortening schedule")){}
 void init()override{EnergyField::init();try{if(!mstate)throw std::invalid_argument("missing state");auto a=assemble(mstate->read(sofa::core::vec_id::read_access::position)->getValue());restLength=a.cableLength;}catch(const std::exception&e){fail(e.what());}}
 Assembly assemble(const VecCoord&x)const override{
  auto&ids=route.getValue();double kc=stiffness.getValue();if(ids.size()<2||ids.size()>41||!std::isfinite(kc)||kc<0||!std::isfinite(offset.getValue()))throw std::invalid_argument("cable parameters");
  for(size_t j=0;j<ids.size();++j)if(ids[j]>=x.size()||std::find(ids.begin(),ids.begin()+j,ids[j])!=ids.begin()+j)throw std::invalid_argument("cable route");
  Assembly a(x.size());std::vector<double>g(a.f.size());std::vector<Triplet>H;
  for(size_t j=1;j<ids.size();++j){unsigned l=ids[j-1],u=ids[j];auto v=cable_segment(pose(x[l]),pose(x[u]),V{0,0,offset.getValue()});a.cableLength+=v.v;
   for(int r=0;r<12;++r){unsigned row=6*(r<6?l:u)+r%6;g[row]+=v.g[r];for(int c=0;c<12;++c)if(v.h[12*r+c]!=0)H.push_back({row,6*(c<6?l:u)+unsigned(c%6),v.h[12*r+c]});}}
  double command=schedule(getContext()?getContext()->getTime():0,times.getValue(),commands.getValue(),kc?shortening.getValue():tension.getValue());
  if(command<0||!std::isfinite(command)||(kc&&restLength&&command>=restLength))throw std::invalid_argument("cable command");
  double stretch=restLength?a.cableLength-restLength+command:0,T=kc?kc*std::max(0.,stretch):command,tangent=kc&&stretch>0?kc:0.;a.tension=T;a.energy=kc?.5*kc*std::max(0.,stretch)*std::max(0.,stretch):T*a.cableLength;
  for(size_t i=0;i<g.size();++i)a.f[i]=-T*g[i];
  for(auto&t:H)a.J.push_back({t.r,t.c,-T*t.v});
  if(tangent)for(unsigned i=0;i<g.size();++i)if(g[i])for(unsigned j=0;j<g.size();++j)if(g[j])a.J.push_back({i,j,-tangent*g[i]*g[j]});
  for(unsigned i:ids){double tx=a.f[6*i+3],ty=a.f[6*i+4],tz=a.f[6*i+5],s[9]={0,-tz,ty,tz,0,-tx,-ty,tx,0};for(int r=0;r<3;++r)for(int c=0;c<3;++c)if(s[3*r+c])a.J.push_back({6*i+3+unsigned(r),6*i+3+unsigned(c),-.5*s[3*r+c]});}
  return a;
 }
};
class AnalyticContact final:public EnergyField{
public:
 SOFA_CLASS(AnalyticContact,EnergyField);
 sofa::core::objectmodel::Data<unsigned> objectIndex,shape;
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> points;
 sofa::core::objectmodel::Data<double> radius,halfX,halfY,halfZ,stiffness,pointRadius;
 explicit AnalyticContact(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),objectIndex(initData(&objectIndex,0u,"objectIndex","Object rigid node")),shape(initData(&shape,0u,"shape","0 sphere, 1 infinite cylinder local y, 2 box")),
 points(initData(&points,"pointIndices","Finger center samples")),radius(initData(&radius,5.,"radius","Sphere/cylinder radius")),halfX(initData(&halfX,5.,"halfX","Box half x")),halfY(initData(&halfY,5.,"halfY","Box half y")),halfZ(initData(&halfZ,5.,"halfZ","Box half z")),
 stiffness(initData(&stiffness,.001,"stiffness","Penalty model F/mm")),pointRadius(initData(&pointRadius,.1,"pointRadius","Research nodal collision radius")){}
 Assembly assemble(const VecCoord&x)const override{if(objectIndex.getValue()>=x.size())throw std::invalid_argument("contact object index");Assembly a(x.size());unsigned u=objectIndex.getValue();
  for(unsigned l:points.getValue()){if(l>=x.size()||l==u)throw std::invalid_argument("contact point index");auto e=contact_energy(pose(x[l]),pose(x[u]),shape.getValue(),shape.getValue()==2?V{halfX.getValue(),halfY.getValue(),halfZ.getValue()}:V{radius.getValue(),1,1},V{0,0,0},pointRadius.getValue(),stiffness.getValue());auto r=energy_result(e);pair(a,l,u,r);if(e.v>0){a.contacts++;a.contactForce+=std::sqrt(r.force[0]*r.force[0]+r.force[1]*r.force[1]+r.force[2]*r.force[2]);}}
  return a;
 }
};
class ScheduledLoad final:public EnergyField{
public:
 SOFA_CLASS(ScheduledLoad,EnergyField);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> indices;
 sofa::core::objectmodel::Data<sofa::type::vector<double>> times,values;
 sofa::core::objectmodel::Data<unsigned> axis;
 explicit ScheduledLoad(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),indices(initData(&indices,"indices","Share total load across nodes")),times(initData(&times,"times","Step times")),values(initData(&values,"values","Total signed model force/moment")),axis(initData(&axis,2u,"axis","0..2 force, 4 planar moment")){}
 Assembly assemble(const VecCoord&x)const override{
  Assembly a(x.size());if(indices.getValue().empty()||!(axis.getValue()<3||axis.getValue()==4))throw std::invalid_argument("load indices/axis");double v=schedule(getContext()?getContext()->getTime():0,times.getValue(),values.getValue(),0)/indices.getValue().size();
  for(unsigned i:indices.getValue()){if(i>=x.size())throw std::invalid_argument("load node index");auto p=pose(x[i]);a.f[6*i+axis.getValue()]+=v;a.energy-=v*(axis.getValue()<3?p.p[axis.getValue()]:2*std::atan2(p.q[1],p.q[3]));}return a;
 }
};
#include "Recorder.inc"
} // namespace
extern "C" {
__attribute__((visibility("default"))) void initExternalModule(){}
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripIntegrated";}
__attribute__((visibility("default"))) const char*getModuleVersion(){return "0.1.0-experimental";}
__attribute__((visibility("default"))) const char*getModuleLicense(){return "Research prototype";}
__attribute__((visibility("default"))) const char*getModuleDescription(){return "Independent multilayer, cable and analytic contact research components";}
__attribute__((visibility("default"))) const char*getModuleComponentList(){return "LayerNetwork RoutedCable AnalyticContact ScheduledLoad IntegratedRecorder";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){using namespace regrip_integrated;f->registerObjects(sofa::core::ObjectRegistrationData("Research layer network").add<LayerNetwork>());f->registerObjects(sofa::core::ObjectRegistrationData("Research material-guide cable").add<RoutedCable>());f->registerObjects(sofa::core::ObjectRegistrationData("Research analytic nodal contact").add<AnalyticContact>());f->registerObjects(sofa::core::ObjectRegistrationData("Auditable scheduled load").add<ScheduledLoad>());f->registerObjects(sofa::core::ObjectRegistrationData("Integrated state recorder").add<IntegratedRecorder>());}
}
