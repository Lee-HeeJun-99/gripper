#include "StickBase.inc"
#include "Quadrature.h"
#include <map>
namespace regrip_integrated {
using regrip_stick::scale;
class ActiveIntervalContact final:public EnergyField{
public:
 SOFA_CLASS(ActiveIntervalContact,EnergyField);
 sofa::core::objectmodel::Data<sofa::type::vector<unsigned>>segments;
 sofa::core::objectmodel::Data<unsigned>objectIndex,shape,samples,stride;
 sofa::core::objectmodel::Data<double>radius,halfHeight,pointRadius,lineStiffness,tangentLineStiffness,mu,historySpacing;
 sofa::core::objectmodel::Data<std::string>filename;
 struct Grid{unsigned count=0;double length=0;std::vector<regrip_stick::History>state;std::vector<unsigned>active;};
 std::vector<Grid>grids;VecCoord previous;std::vector<std::pair<double,double>>rule;
 double plastic=0,released=0;unsigned steps=0;std::ofstream file,patch;
 struct Point{unsigned edge;double s,weight;Pose p;regrip_stick::ContactResult r;};
 struct Snapshot{Assembly a;std::vector<Point>points;double D=0,release=0,elastic=0,capacity=0,ratio=0,sticks=0,slips=0,length=0;explicit Snapshot(size_t n):a(n){}};
 explicit ActiveIntervalContact(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),
 segments(initData(&segments,"segments","Reference-material beam endpoint pairs")),objectIndex(initData(&objectIndex,0u,"objectIndex","Free object")),shape(initData(&shape,0u,"shape","sphere/capped cylinder/box")),samples(initData(&samples,8u,"samples","Gauss order per active interval")),stride(initData(&stride,20u,"stride","Output stride")),
 radius(initData(&radius,5.,"radius","Research dimension")),halfHeight(initData(&halfHeight,5.,"halfHeight","Cylinder")),pointRadius(initData(&pointRadius,.1,"pointRadius","Unchanged line skin")),lineStiffness(initData(&lineStiffness,.001,"lineStiffness","Normal F/mm2")),tangentLineStiffness(initData(&tangentLineStiffness,.001,"tangentLineStiffness","Tangent F/mm2")),mu(initData(&mu,.3,"mu","Equal static/kinetic coefficient")),historySpacing(initData(&historySpacing,.01,"historySpacing","Independent material history grid maximum mm")),filename(initData(&filename,std::string("contact.csv"),"filename","New output only")){f_listening.setValue(true);}
 void validateInput(const VecCoord&x)const{
  if(!mstate||objectIndex.getValue()>=x.size()||shape.getValue()>2||segments.getValue().empty()||segments.getValue().size()%2||samples.getValue()<2||samples.getValue()>32||!stride.getValue())throw std::invalid_argument("adaptive contact state/parameters");
  for(double v:{radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue(),historySpacing.getValue()})if(!std::isfinite(v)||v<0)throw std::invalid_argument("adaptive nonfinite/negative input");
  if(radius.getValue()==0||halfHeight.getValue()==0||tangentLineStiffness.getValue()==0||historySpacing.getValue()<.001||historySpacing.getValue()>1)throw std::invalid_argument("adaptive dimension/history bounds");
  if(grids.size()!=segments.getValue().size()/2||previous.size()!=x.size()||rule.size()!=samples.getValue())throw std::invalid_argument("adaptive history/topology/order changed");
  for(unsigned i=0;i<segments.getValue().size();i+=2){unsigned a=segments.getValue()[i],b=segments.getValue()[i+1];if(a>=x.size()||b>=x.size()||a==b||a==objectIndex.getValue()||b==objectIndex.getValue())throw std::invalid_argument("adaptive runtime segment indices");}
  for(auto&p:x)pose(p);
 }
 Pose point(const VecCoord&x,unsigned edge,double s)const{Pose p;unsigned a=segments.getValue()[2*edge],b=segments.getValue()[2*edge+1];p.p=add(scale(pose(x[a]).p,1-s),scale(pose(x[b]).p,s));return p;}
 regrip_stick::History old(unsigned edge,double s)const{
  const auto&g=grids[edge];double t=s*g.count;unsigned a=std::min(unsigned(t),g.count-1);double alpha=t-a;auto p=point(previous,edge,s),o=pose(previous[objectIndex.getValue()]);auto local=rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));regrip_stick::History h;
  if(regrip_closure::sdf(local,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue())return h;
  auto geometry=regrip_stick::geometry(regrip_stick::constantV<regrip_stick::First>(local),shape.getValue(),radius.getValue(),halfHeight.getValue());h.active=true;h.local=local;
  for(int j=0;j<3;++j){h.normal[j]=geometry.normal[j].v;h.elastic[j]=(1-alpha)*g.state[a].elastic[j]+alpha*g.state[a+1].elastic[j];}
  h.elastic=sub(h.elastic,scale(h.normal,dot(h.normal,h.elastic)));return h;
 }
 regrip_closure::Interval interval(const VecCoord&x,unsigned edge)const{auto o=pose(x[objectIndex.getValue()]);auto a=point(x,edge,0),b=point(x,edge,1);return regrip_closure::activeInterval(regrip_closure::localPoint(a,b,o,0),regrip_closure::localPoint(a,b,o,1),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue());}
 Snapshot compute(const VecCoord&x)const{
  validateInput(x);Snapshot out(x.size());unsigned obj=objectIndex.getValue();auto po=pose(x[obj]);
  for(unsigned edge=0;edge<grids.size();++edge){auto range=interval(x,edge);if(!range.active())continue;out.length+=(range.hi-range.lo)*grids[edge].length;
   unsigned a=segments.getValue()[2*edge],b=segments.getValue()[2*edge+1];
   for(auto[node,w]:rule){double s=(range.lo+range.hi)/2+(range.hi-range.lo)/2*node,weight=grids[edge].length*(range.hi-range.lo)/2*w;auto pp=point(x,edge,s);
    auto r=regrip_stick::evaluateContact(pp,po,old(edge,s),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue());
    out.points.push_back({edge,s,weight,pp,r});out.a.energy+=weight*r.wrench.energy;out.a.contactForce+=weight*r.normalForce;out.a.contacts++;out.D+=weight*r.plasticDissipation;out.elastic+=weight*r.elasticEnergy;out.capacity+=weight*r.capacity;if(r.next.sliding)out.slips++;else out.sticks++;
    double traction=tangentLineStiffness.getValue()*std::sqrt(dot(r.next.elastic,r.next.elastic));if(r.capacity>0)out.ratio=std::max(out.ratio,traction/r.capacity);
    auto map=[&](int i){std::vector<std::pair<unsigned,double>>m;if(i<3){m.push_back({6*a+unsigned(i),1-s});m.push_back({6*b+unsigned(i),s});}else if(i>=6)m.push_back({6*obj+unsigned(i-6),1});return m;};
    for(int i=0;i<12;++i)for(auto[row,wi]:map(i)){out.a.f[row]+=weight*wi*r.wrench.force[i];for(int k=0;k<12;++k)for(auto[col,wk]:map(k)){double J=weight*wi*wk*r.wrench.jacobian[12*i+k];if(J)out.a.J.push_back({row,col,J});}}
   }
  }check(out.a,x.size());return out;
 }
 Assembly assemble(const VecCoord&x)const override{return compute(x).a;}
 void prepare(const VecCoord&x){
  if(!mstate||segments.getValue().empty()||segments.getValue().size()%2||!std::isfinite(historySpacing.getValue())||historySpacing.getValue()<.001||historySpacing.getValue()>1)throw std::invalid_argument("adaptive prepare");
  const auto&rest=mstate->read(sofa::core::vec_id::read_access::restPosition)->getValue();grids.clear();size_t total=0;
  for(unsigned i=0;i<segments.getValue().size();i+=2){unsigned a=segments.getValue()[i],b=segments.getValue()[i+1];if(a>=x.size()||b>=x.size()||a==b||a==objectIndex.getValue()||b==objectIndex.getValue()||rest.size()!=x.size())throw std::invalid_argument("adaptive segment index");double L=(rest[b].getCenter()-rest[a].getCenter()).norm();if(!std::isfinite(L)||L<1e-12)throw std::invalid_argument("adaptive reference length");Grid g;g.length=L;g.count=unsigned(std::ceil(L/historySpacing.getValue()));total+=g.count+1;if(total>1000000)throw std::invalid_argument("bounded history memory");g.state.resize(g.count+1);grids.push_back(std::move(g));}
  previous=x;rule=regrip_closure::gauss(samples.getValue());validateInput(x);commit(x);
 }
 void commit(const VecCoord&x){
  validateInput(x);std::vector<std::vector<std::pair<unsigned,regrip_stick::History>>>next(grids.size());
  for(unsigned e=0;e<grids.size();++e){auto range=interval(x,e);if(!range.active())continue;const auto&g=grids[e];unsigned lo=unsigned(std::ceil(range.lo*g.count)),hi=std::min(g.count,unsigned(std::floor(range.hi*g.count)));
   for(unsigned i=lo;i<=hi;++i){double s=double(i)/g.count;auto r=regrip_stick::evaluateContact(point(x,e,s),pose(x[objectIndex.getValue()]),old(e,s),shape.getValue(),radius.getValue(),halfHeight.getValue(),pointRadius.getValue(),lineStiffness.getValue(),tangentLineStiffness.getValue(),mu.getValue());next[e].push_back({i,r.next});}
  }
  // Release estimate on fixed material history cells, separate from plastic D.
  for(unsigned e=0;e<grids.size();++e){auto&g=grids[e];for(auto i:g.active){auto p=point(x,e,double(i)/g.count),o=pose(x[objectIndex.getValue()]);auto local=rotate(Q{-o.q[0],-o.q[1],-o.q[2],o.q[3]},sub(p.p,o.p));if(regrip_closure::sdf(local,shape.getValue(),radius.getValue(),halfHeight.getValue())>=pointRadius.getValue())released+=.5*tangentLineStiffness.getValue()*dot(g.state[i].elastic,g.state[i].elastic)*g.length/g.count;g.state[i]={};}g.active.clear();for(auto&item:next[e]){g.state[item.first]=item.second;g.active.push_back(item.first);}}
  previous=x;
 }
 void init()override{EnergyField::init();try{if(!mstate)throw std::invalid_argument("adaptive state");prepare(mstate->read(sofa::core::vec_id::read_access::position)->getValue());std::ifstream exists(filename.getValue()),p(filename.getValue()+".patch.csv");if(exists||p)throw std::invalid_argument("refusing old adaptive output");file.open(filename.getValue());patch.open(filename.getValue()+".patch.csv");if(!file||!patch)throw std::runtime_error("adaptive output open");file<<std::setprecision(17)<<"time,normal_force,friction_dissipation,release_dissipation,elastic_energy,contacts,stick,slip,capacity,max_ratio,Fx,Fy,Fz,Mx,My,Mz,active_length\n";patch<<std::setprecision(17)<<"time,edge,s,weight,px,py,pz,nx,ny,nz,Fn,Fx,Fy,Fz,Mx,My,Mz,sliding\n";}catch(const std::exception&e){fail(e.what());}}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!mstate||!file)return;try{const auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();auto r=compute(x);plastic+=r.D;commit(x);if(++steps%stride.getValue())return;file<<getContext()->getTime()<<','<<r.a.contactForce<<','<<plastic<<','<<released<<','<<r.elastic<<','<<r.a.contacts<<','<<r.sticks<<','<<r.slips<<','<<r.capacity<<','<<r.ratio;for(int j=0;j<6;++j)file<<','<<r.a.f[6*objectIndex.getValue()+j];file<<','<<r.length<<'\n';file.flush();
  auto po=pose(x[objectIndex.getValue()]);for(auto&p:r.points){auto local=regrip_closure::localPoint(p.p,p.p,po,0);auto g=regrip_stick::geometry(regrip_stick::constantV<regrip_stick::First>(local),shape.getValue(),radius.getValue(),halfHeight.getValue());V n{};for(int j=0;j<3;++j)n[j]=g.normal[j].v;n=rotate(po.q,n);patch<<getContext()->getTime()<<','<<p.edge<<','<<p.s<<','<<p.weight;for(double v:p.p.p)patch<<','<<v;for(double v:n)patch<<','<<v;patch<<','<<p.weight*p.r.normalForce;for(int j=6;j<12;++j)patch<<','<<p.weight*p.r.wrench.force[j];patch<<','<<p.r.next.sliding<<'\n';}patch.flush();
 }catch(const std::exception&e){fail(e.what());}}
};
class SpatialLoad final:public EnergyField{
public:
 SOFA_CLASS(SpatialLoad,EnergyField);
 sofa::core::objectmodel::Data<unsigned>index,axis;
 sofa::core::objectmodel::Data<sofa::type::vector<double>>times,values;
 explicit SpatialLoad(sofa::core::behavior::MechanicalState<Types>*s=nullptr):EnergyField(s),index(initData(&index,0u,"index","Free object")),axis(initData(&axis,0u,"axis","0..2 spatial force,3..5 spatial torque")),times(initData(&times,"times","Step schedule")),values(initData(&values,"values","Physical model wrench component")){}
 Assembly assemble(const VecCoord&x)const override{if(index.getValue()>=x.size()||axis.getValue()>5)throw std::invalid_argument("spatial load");Assembly a(x.size());a.f[6*index.getValue()+axis.getValue()]=schedule(getContext()?getContext()->getTime():0,times.getValue(),values.getValue(),0);return a;}
 // EnergyField assembly E excludes EXTERNAL actuator work. No global potential
 // is claimed for a constant spatial moment at finite SO(3) rotation.
};
}
extern "C" {
__attribute__((visibility("default"))) const char*getModuleName(){return "ReGripClosure";}
__attribute__((visibility("default"))) void registerObjects(sofa::core::ObjectFactory*f){registerStickObjects(f);f->registerObjects(sofa::core::ObjectRegistrationData("Active-interval Gauss contact, independent material history").add<regrip_integrated::ActiveIntervalContact>());f->registerObjects(sofa::core::ObjectRegistrationData("Spatial research external wrench").add<regrip_integrated::SpatialLoad>());}
}
