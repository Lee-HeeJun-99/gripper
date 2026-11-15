#include "AdaptiveBase.inc"
namespace regrip_integrated {
#include "FrameLayerBase.inc"
class FrameLayerNetwork final:public FrameLayerBase{
public:
 SOFA_CLASS(FrameLayerNetwork,FrameLayerBase);
 sofa::core::objectmodel::Data<sofa::type::Quat<double>>reference;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<unsigned>stride;
 sofa::core::objectmodel::Data<double>dissipatedEnergy;
 std::ofstream file;unsigned steps=0;
 explicit FrameLayerNetwork(sofa::core::behavior::MechanicalState<Types>*s=nullptr):FrameLayerBase(s),reference(initData(&reference,sofa::type::Quat<double>(0,0,0,1),"referenceOrientation","Fixed material reference frame; NOT a pose correction")),filename(initData(&filename,std::string(""),"filename","Optional new layer energy log")),stride(initData(&stride,20u,"stride","Output interval")),dissipatedEnergy(initData(&dissipatedEnergy,0.,"dissipatedEnergy","Own pressure-slider dissipation; original recorder cannot dynamic-cast this new class")){}
 Q frame()const{auto q=reference.getValue();Q r{q[0],q[1],q[2],q[3]};validate(Pose{{0,0,0},r});return r;}
 VecCoord local(const VecCoord&world)const{auto q=frame();Q inverse{-q[0],-q[1],-q[2],q[3]};auto x=world;for(auto&p:x){auto a=pose(p);a.p=rotate(inverse,a.p);a.q=multiply(inverse,a.q);for(int j=0;j<3;++j)p.getCenter()[j]=a.p[j];p.getOrientation()={a.q[0],a.q[1],a.q[2],a.q[3]};}return x;}
 Assembly assemble(const VecCoord&world)const override{
  auto a=FrameLayerBase::assemble(local(world));auto q=frame();double R[3][3]{};for(int c=0;c<3;++c){V e{};e[c]=1;auto v=rotate(q,e);for(int r=0;r<3;++r)R[r][c]=v[r];}
  for(unsigned offset=0;offset<a.f.size();offset+=3){auto f=rotate(q,V{a.f[offset],a.f[offset+1],a.f[offset+2]});for(int j=0;j<3;++j)a.f[offset+j]=f[j];}
  auto entries=std::move(a.J);a.J.clear();for(const auto&t:entries){unsigned row=t.r/3*3,col=t.c/3*3;for(unsigned i=0;i<3;++i)for(unsigned j=0;j<3;++j){double value=R[i][t.r%3]*t.v*R[j][t.c%3];if(value)a.J.push_back({row+i,col+j,value});}}
  check(a,world.size());return a;
 }
 void init()override{FrameLayerBase::init();try{if(!stride.getValue())throw std::invalid_argument("frame log stride");frame();if(!filename.getValue().empty()){std::ifstream existing(filename.getValue());if(existing)throw std::invalid_argument("refusing old frame log");file.open(filename.getValue());if(!file)throw std::runtime_error("frame layer output");file<<std::setprecision(17)<<"time,pressure,dissipated,max_slip\n";}}catch(const std::exception&e){fail(e.what());}}
 void handleEvent(sofa::core::objectmodel::Event*event)override{
  if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||mode.getValue()!=1||!mstate)return;
  try{auto x=local(mstate->read(sofa::core::vec_id::read_access::position)->getValue());auto a=FrameLayerBase::assemble(x);auto selected=ids();size_t c=0;unsigned n=nodes.getValue();double h=height.getValue();
   for(unsigned l=0;l<layers.getValue()-1;++l)for(size_t j=0;j<selected.size();++j){unsigned i=selected[j],u=start.getValue()+l*n+i,v=u+n;auto pa=pose(x[u]),pb=pose(x[v]);double s=pb.p[0]-pa.p[0]-h*(std::atan2(pa.q[1],pa.q[3])+std::atan2(pb.q[1],pb.q[3]));double left=j?.5*(selected[j-1]+i)*length.getValue()/(n-1):0,right=j+1==selected.size()?length.getValue():.5*(i+selected[j+1])*length.getValue()/(n-1);auto r=slider(s,plastic[c],stiffness.getValue(),mu.getValue()*currentPressure()*width.getValue()*(right-left));plastic[c++]=r.plastic;dissipated+=r.dissipation;}
   dissipatedEnergy.setValue(dissipated);if(++steps%stride.getValue()==0&&file){file<<getContext()->getTime()<<','<<currentPressure()<<','<<dissipated<<','<<a.slip<<'\n';file.flush();}
  }catch(const std::exception&e){fail(e.what());}
 }
};
}
extern "C" {
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripFrameClosure";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){registerClosureBaseObjects(f);f->registerObjects(sofa::core::ObjectRegistrationData("Unchanged planar layer law in a fixed material reference frame").add<regrip_integrated::FrameLayerNetwork>());}
}
