#include "../models/contact_history/ContactFriction.cpp"
#include "LegacyContact.inc"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
#include <iomanip>
#include <random>
using namespace regrip_integrated;
void require(bool b,const char*s){if(!b)throw std::runtime_error(s);}
template<class F>auto setup(unsigned q,double h){
 typename sofa::component::statecontainer::MechanicalObject<Types>::SPtr state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(3);Inherit::VecCoord x(3);x[0].getCenter()={-.6,.99,0};x[1].getCenter()={.6,.99,0};for(auto&v:x)v.getOrientation()={0,0,0,1};state->write(sofa::core::vec_id::write_access::position)->setValue(x);state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);
 typename F::SPtr f=sofa::core::objectmodel::New<F>(state.get());f->segments.setValue({0,1});f->objectIndex.setValue(2);f->radius.setValue(1);f->pointRadius.setValue(.02);f->samples.setValue(q);f->historySpacing.setValue(h);f->lineStiffness.setValue(1);f->tangentLineStiffness.setValue(1);f->prepare(x);
 for(unsigned i=0;i<=f->grids[0].count;++i){double s=double(i)/f->grids[0].count;auto p=f->point(x,0,s);auto g=regrip_stick::geometry(regrip_stick::constantV<regrip_stick::First>(p.p),0,1,5);auto&v=f->grids[0].state[i];v.active=g.distance.v<.02;v.local=p.p;for(int j=0;j<3;++j)v.normal[j]=g.normal[j].v;v.elastic={0,0,1e-4*std::max(0.,1-std::abs(1.2*s-.6)/.06)};}
 return std::make_pair(state,f);
}
int main(){try{
 std::cout<<std::setprecision(17);double angle=.2;V n{0,0,1},e{0,1,0},nl{0,-std::sin(angle),std::cos(angle)},nr{0,std::sin(angle),std::cos(angle)};auto el=regrip_history::transport(e,n,nl),er=regrip_history::transport(e,n,nr);auto legacy=add(regrip_history::scale(el,.5),regrip_history::scale(er,.5));legacy=sub(legacy,regrip_history::scale(n,dot(n,legacy)));auto consistent=add(regrip_history::scale(regrip_history::transport(el,nl,n),.5),regrip_history::scale(regrip_history::transport(er,nr,n),.5));require(std::abs(dot(consistent,consistent)-1)<1e-14,"objective nodal transport energy");std::cout<<"TRANSPORT legacy_energy_loss="<<1-dot(legacy,legacy)<<" new="<<1-dot(consistent,consistent)<<'\n';
 for(unsigned q:{8u,16u,32u}){auto a=setup<ActiveIntervalContact>(q,.02);auto b=setup<MaterialHistoryContact>(q,.02);auto old=a.second->compute(a.first->read(sofa::core::vec_id::read_access::position)->getValue());auto now=b.second->compute(b.first->read(sofa::core::vec_id::read_access::position)->getValue());double reference=6e-6;std::cout<<"QUADRATURE q="<<q<<" old="<<old.a.f[14]<<" new="<<now.a.f[14]<<" old_rel="<<std::abs(old.a.f[14]/reference-1)<<" new_rel="<<std::abs(now.a.f[14]/reference-1)<<'\n';require(std::abs(now.a.f[14]/reference-1)<1e-11,"cell partition exact linear reference");}
 double valueError=0,fdError=0,moment=0;std::mt19937 rng(2911);std::uniform_real_distribution<double>d(-.01,.01);
 for(int i=0;i<60;++i){Pose o,p;p.p={d(rng),.99,d(rng)};regrip_history::History h;h.active=true;h.normal={0,1,0};h.local={0,.99,0};h.elastic={d(rng)*.1,0,d(rng)*.1};auto a=regrip_history::evaluateContact(p,o,h,0,1,5,.02,1,1,.3);auto b=regrip_history::value(p,o,h,0,1,5,.02,1,1,.3);for(int j=0;j<3;++j)valueError=std::max(valueError,std::abs(a.next.elastic[j]-b.next.elastic[j]));require(a.plasticDissipation>=0,"nonnegative plastic dissipation");require(std::sqrt(dot(a.next.elastic,a.next.elastic))<=a.capacity+1e-14,"Coulomb limit");
  for(int k=0;k<12;++k){auto pp=p,pm=p,op=o,om=o;if(k<6){pp=increment(p,k,1e-6);pm=increment(p,k,-1e-6);}else{op=increment(o,k-6,1e-6);om=increment(o,k-6,-1e-6);}auto ap=regrip_history::evaluateContact(pp,op,h,0,1,5,.02,1,1,.3),am=regrip_history::evaluateContact(pm,om,h,0,1,5,.02,1,1,.3);for(int j=0;j<12;++j)fdError=std::max(fdError,std::abs((ap.wrench.force[j]-am.wrench.force[j])/2e-6-a.wrench.jacobian[12*j+k]));}
  auto m=add(add(V{a.wrench.force[3],a.wrench.force[4],a.wrench.force[5]},V{a.wrench.force[9],a.wrench.force[10],a.wrench.force[11]}),cross(sub(p.p,o.p),V{a.wrench.force[0],a.wrench.force[1],a.wrench.force[2]}));for(double x:m)moment=std::max(moment,std::abs(x));
 }
 require(valueError<1e-12&&fdError<1e-7&&moment<1e-12,"return map value/Jacobian/moment");bool guarded=false;try{regrip_history::transport(e,n,regrip_history::scale(n,-1.));}catch(const std::invalid_argument&){guarded=true;}require(guarded,"antipodal guard");std::cout<<"PASS60 value="<<valueError<<" J="<<fdError<<" moment="<<moment<<'\n';
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
