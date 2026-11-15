#include "Integrated.inc"
#include "StickSlip.h"
namespace regrip_integrated {
class StickSlipContact final:public EnergyField{
public:
 SOFA_CLASS(StickSlipContact,EnergyField);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>>segments;
 sofa::core::objectmodel::Data<unsigned>objectIndex,shape,samples,stride;
 sofa::core::objectmodel::Data<double>radius,halfHeight,pointRadius,lineStiffness,tangentLineStiffness,mu;
 sofa::core::objectmodel::Data<std::string>filename;
 std::vector<regrip_stick::History>history;double plasticDissipation=0,releaseDissipation=0;unsigned steps=0;std::ofstream file;
 struct Snapshot{Assembly a;std::vector<regrip_stick::History>next;double plastic=0,release=0,elastic=0,capacity=0,maxRatio=0,sticks=0,slips=0;explicit Snapshot(size_t n):a(n){}};
 explicit StickSlipContact(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),
 segments(initData(&segments,"segments","Beam endpoint pairs")),objectIndex(initData(&objectIndex,0u,"objectIndex","Unconstrained object")),shape(initData(&shape,0u,"shape","0 sphere/1 finite cylinder local y/2 cube")),samples(initData(&samples,8u,"samples","Intervals per segment")),stride(initData(&stride,20u,"stride","History output stride")),
 radius(initData(&radius,5.,"radius","Research radius/box half width")),halfHeight(initData(&halfHeight,5.,"halfHeight","Finite cylinder half height")),pointRadius(initData(&pointRadius,.1,"pointRadius","Line skin")),lineStiffness(initData(&lineStiffness,.001,"lineStiffness","Normal F/mm^2")),tangentLineStiffness(initData(&tangentLineStiffness,.001,"tangentLineStiffness","Elastic tangential F/mm^2")),mu(initData(&mu,.3,"mu","Equal static/kinetic Coulomb coefficient")),filename(initData(&filename,std::string("stick.csv"),"filename","Fresh contact history")){f_listening.setValue(true);}
 Snapshot compute(const VecCoord&x)const{
  if(!mstate||objectIndex.getValue()>=x.size()||segments.getValue().empty()||segments.getValue().size()%2||!samples.getValue()||samples.getValue()>32||!stride.getValue())throw std::invalid_argument("stick state/indices/sampling");
  for(double v:{radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue()})if(!std::isfinite(v)||v<0)throw std::invalid_argument("stick invalid runtime parameter");
  if(radius.getValue()==0||halfHeight.getValue()==0||tangentLineStiffness.getValue()==0||shape.getValue()>2)throw std::invalid_argument("stick dimensions/runtime shape");
  for(auto&p:x)pose(p);
  const auto&rest=mstate->read(sofa::core::vec_id::read_access::restPosition)->getValue();if(rest.size()!=x.size())throw std::invalid_argument("stick rest-state size");
  size_t count=segments.getValue().size()/2*(samples.getValue()+1);if(history.size()!=count)throw std::invalid_argument("stick history/topology changed");
  Snapshot out(x.size());out.next.reserve(count);unsigned obj=objectIndex.getValue();auto po=pose(x[obj]);size_t index=0;
  for(size_t edge=0;edge<segments.getValue().size();edge+=2){unsigned a=segments.getValue()[edge],b=segments.getValue()[edge+1];if(a>=x.size()||b>=x.size()||a==b||a==obj||b==obj)throw std::invalid_argument("stick segment index");double length=(rest[b].getCenter()-rest[a].getCenter()).norm();if(!std::isfinite(length)||length<=0)throw std::invalid_argument("stick rest length");
   for(unsigned j=0;j<=samples.getValue();++j,++index){double s=double(j)/samples.getValue(),weight=length/samples.getValue()*((j==0||j==samples.getValue())?.5:1.);Pose pp;for(int k=0;k<3;++k)pp.p[k]=(1-s)*x[a].getCenter()[k]+s*x[b].getCenter()[k];
    // Separated samples need no AD2/AD1 calculation; history is released once
    // by commit, never on residual/solver queries.
    auto local=rotate(Q{-po.q[0],-po.q[1],-po.q[2],po.q[3]},sub(pp.p,po.p));auto geo=regrip_stick::geometry(regrip_stick::constantV<regrip_stick::First>(local),shape.getValue(),radius.getValue(),halfHeight.getValue());
    if(geo.distance.v>=pointRadius.getValue()){out.next.emplace_back();out.release+=.5*weight*tangentLineStiffness.getValue()*dot(history[index].elastic,history[index].elastic);continue;}
    auto r=regrip_stick::evaluateContact(pp,po,history[index],shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),weight*lineStiffness.getValue(),weight*tangentLineStiffness.getValue(),mu.getValue());
    out.next.push_back(r.next);out.a.energy+=r.wrench.energy;out.a.contacts++;out.a.contactForce+=r.normalForce;out.plastic+=r.plasticDissipation;out.release+=r.releaseDissipation;out.elastic+=r.elasticEnergy;out.capacity+=r.capacity;if(r.next.sliding)out.slips++;else out.sticks++;
    double traction=weight*tangentLineStiffness.getValue()*std::sqrt(dot(r.next.elastic,r.next.elastic));if(r.capacity>0)out.maxRatio=std::max(out.maxRatio,traction/r.capacity);else if(traction>1e-20)throw std::runtime_error("nonzero traction at zero capacity");
    auto map=[&](int i){std::vector<std::pair<unsigned,double>>m;if(i<3){m.push_back({6*a+unsigned(i),1-s});m.push_back({6*b+unsigned(i),s});}else if(i>=6)m.push_back({6*obj+unsigned(i-6),1});return m;};
    for(int i=0;i<12;++i)for(auto[row,wi]:map(i)){out.a.f[row]+=wi*r.wrench.force[i];for(int k=0;k<12;++k)for(auto[col,wk]:map(k)){double J=wi*wk*r.wrench.jacobian[12*i+k];if(J)out.a.J.push_back({row,col,J});}}
   }
  }check(out.a,x.size());return out;
 }
 Assembly assemble(const VecCoord&x)const override{return compute(x).a;}
 void init()override{EnergyField::init();try{if(!mstate||segments.getValue().size()%2||!samples.getValue()||samples.getValue()>32||!stride.getValue())throw std::invalid_argument("stick init");
  for(double v:{radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue()})if(!std::isfinite(v)||v<0)throw std::invalid_argument("stick invalid parameter");
  if(radius.getValue()==0||halfHeight.getValue()==0||tangentLineStiffness.getValue()==0)throw std::invalid_argument("stick positive dimensions/stiffness");
  std::ifstream old(filename.getValue());if(old)throw std::invalid_argument("refusing existing stick output");
  history.assign(segments.getValue().size()/2*(samples.getValue()+1),{});auto snapshot=compute(mstate->read(sofa::core::vec_id::read_access::position)->getValue());history=snapshot.next;
  file.open(filename.getValue());if(!file)throw std::runtime_error("stick output open");file<<std::setprecision(17)<<"time,normal_force,friction_dissipation,release_dissipation,elastic_energy,contacts,stick,slip,capacity,max_ratio,Fx,Fy,Fz,Mx,My,Mz\n";
 }catch(const std::exception&e){fail(e.what());}}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!mstate||!file)return;
  try{auto r=compute(mstate->read(sofa::core::vec_id::read_access::position)->getValue());history=r.next;plasticDissipation+=r.plastic;releaseDissipation+=r.release;
   if(++steps%stride.getValue()==0){file<<getContext()->getTime()<<','<<r.a.contactForce<<','<<plasticDissipation<<','<<releaseDissipation<<','<<r.elastic<<','<<r.a.contacts<<','<<r.sticks<<','<<r.slips<<','<<r.capacity<<','<<r.maxRatio;for(int j=0;j<6;++j)file<<','<<r.a.f[6*objectIndex.getValue()+j];file<<'\n';file.flush();}
  }catch(const std::exception&e){fail(e.what());}
 }
};
}
extern "C" {
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripStickSlip";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){registerIntegratedObjects(f);f->registerObjects(sofa::core::ObjectRegistrationData("Objective elastic stick / Coulomb return mapping, equal mu_s=mu_k").add<regrip_integrated::StickSlipContact>());}
}
