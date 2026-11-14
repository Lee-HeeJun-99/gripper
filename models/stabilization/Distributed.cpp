#include "Integrated.inc"
#include "ContactKernel.h"
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
namespace regrip_integrated {
class DistributedContact final:public EnergyField{
public:
 SOFA_CLASS(DistributedContact,EnergyField);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> segments;
 sofa::core::objectmodel::Data<unsigned> objectIndex,shape,samples;
 sofa::core::objectmodel::Data<double> radius,pointRadius,lineStiffness,mu,speed;
 mutable double normalForce=0,frictionPower=0;double dissipation=0;
 struct Both{Assembly a;std::vector<Triplet>B;explicit Both(size_t n):a(n){}};
 explicit DistributedContact(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),segments(initData(&segments,"segments","Endpoint pairs")),objectIndex(initData(&objectIndex,0u,"objectIndex","Free object")),shape(initData(&shape,0u,"shape","0 sphere/1 infinite cylinder/2 box")),samples(initData(&samples,8u,"samples","Trapezoidal intervals per segment")),radius(initData(&radius,5.,"radius","Shape radius/half dimension")),pointRadius(initData(&pointRadius,.1,"pointRadius","Centerline skin radius")),lineStiffness(initData(&lineStiffness,.001,"lineStiffness","F/mm^2; quadrature independent of sample count")),mu(initData(&mu,.3,"mu","Kinetic friction coefficient")),speed(initData(&speed,1e-5,"speed","Velocity regularization; no exact static friction")){f_listening.setValue(true);}
 Both compute(const VecCoord&x,const VecDeriv&v)const{
  if(!mstate||v.size()!=x.size()||objectIndex.getValue()>=x.size()||segments.getValue().empty()||segments.getValue().size()%2||!samples.getValue()||samples.getValue()>32||shape.getValue()>2||!std::isfinite(radius.getValue())||radius.getValue()<=0||!std::isfinite(pointRadius.getValue())||pointRadius.getValue()<0||!std::isfinite(mu.getValue())||mu.getValue()<0||!std::isfinite(speed.getValue())||speed.getValue()<=0||!std::isfinite(lineStiffness.getValue())||lineStiffness.getValue()<0)throw std::invalid_argument("distributed contact parameters");
  for(const auto&p:x)pose(p);
  for(const auto&velocity:v)for(int j=0;j<6;++j)if(!std::isfinite(velocity[j]))throw std::invalid_argument("nonfinite contact velocity");
  Both out(x.size());normalForce=0;frictionPower=0;unsigned obj=objectIndex.getValue();auto po=pose(x[obj]);const auto&rest=mstate->read(sofa::core::vec_id::read_access::restPosition)->getValue();if(rest.size()!=x.size())throw std::invalid_argument("contact rest-state size");
  for(size_t edge=0;edge<segments.getValue().size();edge+=2){unsigned a=segments.getValue()[edge],b=segments.getValue()[edge+1];if(a>=x.size()||b>=x.size()||a==b||a==obj||b==obj)throw std::invalid_argument("contact segment index");
   auto length=(rest[b].getCenter()-rest[a].getCenter()).norm();if(!std::isfinite(length)||length<=0)throw std::invalid_argument("contact rest length");
   for(unsigned sample=0;sample<=samples.getValue();++sample){double s=double(sample)/samples.getValue(),weight=length/samples.getValue()*((sample==0||sample==samples.getValue())?.5:1.);Pose point{};V vp{},vo{},w{};
    for(int j=0;j<3;++j){point.p[j]=(1-s)*x[a].getCenter()[j]+s*x[b].getCenter()[j];vp[j]=(1-s)*v[a][j]+s*v[b][j];vo[j]=v[obj][j];w[j]=v[obj][j+3];}
    // Cheap rejection before second-order AD for separated surfaces.
    auto local=rotate(Q{-po.q[0],-po.q[1],-po.q[2],po.q[3]},sub(point.p,po.p));double dist=0,r=radius.getValue();
    if(shape.getValue()==0)dist=std::sqrt(dot(local,local))-r;
    else if(shape.getValue()==1)dist=std::hypot(local[0],local[2])-r;
    else{V q{};double outside=0;for(int j=0;j<3;++j){q[j]=std::abs(local[j])-r;outside+=std::max(q[j],0.)*std::max(q[j],0.);}dist=std::sqrt(outside)+std::min(0.,std::max({q[0],q[1],q[2]}));}
    if(dist>=pointRadius.getValue())continue;
    double k=weight*lineStiffness.getValue();V dims{r,r,r};auto nr=energy_result(contact_energy(point,po,shape.getValue(),dims,V{},pointRadius.getValue(),k));auto fr=regrip_contact::friction(point,po,vp,vo,w,shape.getValue(),dims,pointRadius.getValue(),k,mu.getValue(),speed.getValue());auto br=regrip_contact::friction(point,po,vp,vo,w,shape.getValue(),dims,pointRadius.getValue(),k,mu.getValue(),speed.getValue(),true);
    double fn=k*(pointRadius.getValue()-dist);normalForce+=fn;out.a.contacts++;out.a.energy+=nr.energy;out.a.contactForce+=fn;
    auto relative=sub(sub(vp,vo),cross(w,sub(point.p,po.p)));for(int j=0;j<3;++j)frictionPower-=fr.force[j]*relative[j];
    auto map=[&](int i){std::vector<std::pair<unsigned,double>>m;if(i<3){m.push_back({6*a+unsigned(i),1-s});m.push_back({6*b+unsigned(i),s});}else if(i>=6)m.push_back({6*obj+unsigned(i-6),1});return m;};
    for(int i=0;i<12;++i)for(auto[row,wi]:map(i)){out.a.f[row]+=wi*(nr.force[i]+fr.force[i]);for(int j=0;j<12;++j)for(auto[col,wj]:map(j)){double J=wi*wj*(nr.jacobian[12*i+j]+fr.jacobian[12*i+j]),B=wi*wj*br.jacobian[12*i+j];if(J)out.a.J.push_back({row,col,J});if(B)out.B.push_back({row,col,B});}}
   }
  }return out;
 }
 Assembly assemble(const VecCoord&x)const override{return compute(x,mstate->read(sofa::core::vec_id::read_access::velocity)->getValue()).a;}
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&v)override{try{auto a=compute(x.getValue(),v.getValue()).a;check(a,x.getValue().size());auto*w=f.beginEdit();if(w->size()!=x.getValue().size()){f.endEdit();throw std::invalid_argument("contact force size");}for(size_t i=0;i<a.f.size();++i)(*w)[i/6][i%6]+=a.f[i];f.endEdit();}catch(const std::exception&e){fail(e.what());}}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{try{if(!p||!mstate||!std::isfinite(p->kFactor())||!std::isfinite(p->bFactor())||df.getValue().size()!=mstate->getSize()||dx.getValue().size()!=mstate->getSize())throw std::invalid_argument("contact differential parameters");for(const auto&d:dx.getValue())for(int j=0;j<6;++j)if(!std::isfinite(d[j]))throw std::invalid_argument("contact nonfinite differential");auto b=compute(mstate->read(sofa::core::vec_id::read_access::position)->getValue(),mstate->read(sofa::core::vec_id::read_access::velocity)->getValue());auto*w=df.beginEdit();for(auto&t:b.a.J)(*w)[t.r/6][t.r%6]+=p->kFactor()*t.v*dx.getValue()[t.c/6][t.c%6];for(auto&t:b.B)(*w)[t.r/6][t.r%6]+=p->bFactor()*t.v*dx.getValue()[t.c/6][t.c%6];df.endEdit();}catch(const std::exception&e){fail(e.what());}}
 void buildDampingMatrix(sofa::core::behavior::DampingMatrix*m)override{try{if(!m||!mstate)throw std::invalid_argument("contact damping matrix/state");auto b=compute(mstate->read(sofa::core::vec_id::read_access::position)->getValue(),mstate->read(sofa::core::vec_id::read_access::velocity)->getValue());auto acc=m->getForceDerivativeIn(mstate.get()).withRespectToVelocityIn(mstate.get());if(!acc)throw std::invalid_argument("contact damping accumulator");for(auto&t:b.B)acc(t.r,t.c)+=t.v;}catch(const std::exception&e){fail(e.what());}}
 void handleEvent(sofa::core::objectmodel::Event*e)override{if(dynamic_cast<sofa::simulation::AnimateEndEvent*>(e)&&mstate){assemble(mstate->read(sofa::core::vec_id::read_access::position)->getValue());dissipation+=std::max(0.,frictionPower)*getContext()->getDt();}}
};
class ContactHistory final:public sofa::core::objectmodel::BaseComponent{
public:
 SOFA_CLASS(ContactHistory,sofa::core::objectmodel::BaseComponent);
 sofa::core::objectmodel::Data<std::string> filename;sofa::core::objectmodel::Data<unsigned> stride;std::ofstream file;unsigned steps=0;
 ContactHistory():filename(initData(&filename,std::string("contact.csv"),"filename","Distributed force/dissipation record")),stride(initData(&stride,20u,"stride","Sampling stride")){f_listening.setValue(true);}
 void init()override{BaseComponent::init();std::ifstream old(filename.getValue());if(old||!stride.getValue()){msg_error()<<"Invalid contact history";return;}file.open(filename.getValue());file<<std::setprecision(17)<<"time,normal_force,friction_power,friction_dissipation,contacts,Fx,Fy,Fz,Mx,My,Mz\n";}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!file||!stride.getValue()||!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||++steps%stride.getValue())return;double normal=0,power=0,diss=0,count=0;double force[6]{};
  auto*state=dynamic_cast<sofa::core::behavior::MechanicalState<Types>*>(getContext()->getMechanicalState());if(!state)return;
  for(auto*ff:getContext()->getObjects<DistributedContact>(sofa::core::objectmodel::BaseContext::Local)){auto a=ff->assemble(state->read(sofa::core::vec_id::read_access::position)->getValue());normal+=ff->normalForce;power+=ff->frictionPower;diss+=ff->dissipation;count+=a.contacts;for(int j=0;j<6;++j)force[j]+=a.f[6*ff->objectIndex.getValue()+j];}
  file<<getContext()->getTime()<<','<<normal<<','<<power<<','<<diss<<','<<count;for(double v:force)file<<','<<v;file<<'\n';file.flush();}
};
}
extern "C" {
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripDistributed";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){registerIntegratedObjects(f);f->registerObjects(sofa::core::ObjectRegistrationData("Distributed surface penalty and dissipative regularized kinetic friction").add<regrip_integrated::DistributedContact>());f->registerObjects(sofa::core::ObjectRegistrationData("Contact history").add<regrip_integrated::ContactHistory>());}
}
