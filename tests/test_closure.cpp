#include "../models/closure/AdaptiveContact.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
using namespace regrip_integrated;
void require(bool p,const char*m){if(!p)throw std::runtime_error(m);}
int main(){try{
 for(unsigned n:{8u,16u,32u}){double sum=0,moment=0;for(auto[x,w]:regrip_closure::gauss(n)){sum+=w;moment+=w*std::pow(x,6);}require(std::abs(sum-2)<1e-13&&std::abs(moment-2./7)<1e-13,"Gauss polynomial exactness");}
 auto interval=regrip_closure::activeInterval(V{-5,0,5.099},V{5,0,5.099},0,5,5,.1);double exact=2*std::sqrt(5.1*5.1-5.099*5.099);require(std::abs((interval.hi-interval.lo)*10-exact)<1e-12,"subsample sphere active interval");
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(3);auto ff=sofa::core::objectmodel::New<ActiveIntervalContact>(state.get());ff->segments.setValue({0,1});ff->objectIndex.setValue(2);ff->historySpacing.setValue(.005);ff->samples.setValue(16);
 Inherit::VecCoord x(3);for(auto&v:x)v.getOrientation()=sofa::type::Quat<double>(0,0,0,1);x[0].getCenter()={-5,0,5.099};x[1].getCenter()={5,0,5.099};state->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);ff->prepare(x);auto a=ff->compute(x).a;double J[18][18]{};for(auto&t:a.J)J[t.r][t.c]+=t.v;double maxJ=0;
 for(unsigned c=0;c<18;++c){auto plus=x,minus=x;auto p=increment(EnergyField::pose(x[c/6]),c%6,1e-6),m=increment(EnergyField::pose(x[c/6]),c%6,-1e-6);for(int j=0;j<3;++j){plus[c/6].getCenter()[j]=p.p[j];minus[c/6].getCenter()[j]=m.p[j];}plus[c/6].getOrientation()={p.q[0],p.q[1],p.q[2],p.q[3]};minus[c/6].getOrientation()={m.q[0],m.q[1],m.q[2],m.q[3]};auto ap=ff->compute(plus).a,am=ff->compute(minus).a;for(int row=0;row<18;++row)maxJ=std::max(maxJ,std::abs((ap.f[row]-am.f[row])/2e-6-J[row][c]));}
 require(maxJ<1e-7,"moving active-boundary integrated tangent");
 auto before=ff->compute(x);auto after=ff->compute(x);require(before.a.f==after.a.f,"query pure");double net[3]{};for(int i=0;i<3;++i)for(int j=0;j<3;++j)net[j]+=a.f[6*i+j];for(double v:net)require(std::abs(v)<1e-14,"action reaction");
 auto moved=x;moved[0].getCenter()[0]+=.00001;moved[1].getCenter()[0]+=.00001;ff->commit(moved);auto hold=ff->compute(moved);for(int i=0;i<100;++i)ff->commit(moved);auto repeated=ff->compute(moved);double creep=0;for(unsigned i=0;i<hold.a.f.size();++i)creep=std::max(creep,std::abs(hold.a.f[i]-repeated.a.f[i]));require(creep<1e-12,"stationary history no artificial creep");
 std::cout<<std::setprecision(17)<<"PASS integrated active interval / Gauss /18DOF FD / action-reaction / query/history; maxJ="<<maxJ<<" creep="<<creep<<" active_length="<<before.length<<" normal="<<before.a.contactForce<<'\n';
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
