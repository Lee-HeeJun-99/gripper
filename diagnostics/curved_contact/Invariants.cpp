#include "../../models/curved_contact/CurvedContact.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
using namespace regrip_integrated;
using State=sofa::component::statecontainer::MechanicalObject<Types>;
void set(Inherit::Coord&x,const Pose&p){for(int j=0;j<3;++j)x.getCenter()[j]=p.p[j];for(int j=0;j<4;++j)x.getOrientation()[j]=p.q[j];}
int main(){try{
 double covariance=0,moment=0,force=0,jcov=0,queryCommit=0;
 for(int sample=0;sample<30;++sample){Inherit::VecCoord x(3);x[0].getCenter()={-.3,.95,.01};x[1].getCenter()={.3,.95,-.01};for(auto&p:x)p.getOrientation()={0,0,0,1};
  auto R=exp(V{.03*sample,-.04*sample,.07*sample});V translation{.7,-.2,.4};auto transform=[&](const Inherit::VecCoord&input){auto result=input;for(unsigned i=0;i<input.size();++i){auto p=EnergyField::pose(input[i]);p.p=add(rotate(R,p.p),translation);p.q=multiply(R,p.q);set(result[i],p);}return result;};
  auto y=transform(x);auto s0=sofa::core::objectmodel::New<State>(),s1=sofa::core::objectmodel::New<State>();s0->resize(3);s1->resize(3);s0->write(sofa::core::vec_id::write_access::restPosition)->setValue(x);s0->write(sofa::core::vec_id::write_access::position)->setValue(x);s1->write(sofa::core::vec_id::write_access::restPosition)->setValue(y);s1->write(sofa::core::vec_id::write_access::position)->setValue(y);
  auto f0=sofa::core::objectmodel::New<CurvedMaterialContact>(s0.get()),f1=sofa::core::objectmodel::New<CurvedMaterialContact>(s1.get());for(auto*f:{f0.get(),f1.get()}){f->segments.setValue({0,1});f->objectIndex.setValue(2);f->radius.setValue(1.);f->pointRadius.setValue(.1);f->lineStiffness.setValue(1.);f->tangentLineStiffness.setValue(1.);f->historySpacing.setValue(.02);}f0->prepare(x);f1->prepare(y);
  for(int step=0;step<3;++step){x[0].getCenter()[2]+=.002;x[1].getCenter()[2]+=.003;auto qa=exp(V{.003*step,.004*step,.002*step}),qb=exp(V{-.002*step,.003*step,-.002*step});for(int j=0;j<4;++j){x[0].getOrientation()[j]=qa[j];x[1].getOrientation()[j]=qb[j];}y=transform(x);auto a=f0->compute(x),b=f1->compute(y);double A[18][18]{},B[18][18]{};for(auto&t:a.a.J)A[t.r][t.c]+=t.v;for(auto&t:b.a.J)B[t.r][t.c]+=t.v;
   V total{},torque{};for(int i=0;i<3;++i){V p=EnergyField::pose(x[i]).p,f{a.a.f[6*i],a.a.f[6*i+1],a.a.f[6*i+2]},t{a.a.f[6*i+3],a.a.f[6*i+4],a.a.f[6*i+5]};total=add(total,f);torque=add(torque,add(t,cross(p,f)));}
   for(double v:total)force=std::max(force,std::abs(v));for(double v:torque)moment=std::max(moment,std::abs(v));covariance=std::max(covariance,std::abs(a.a.energy-b.a.energy));
   V axes[3]={rotate(R,V{1,0,0}),rotate(R,V{0,1,0}),rotate(R,V{0,0,1})};
   for(int block=0;block<6;++block){auto rotated=rotate(R,V{a.a.f[3*block],a.a.f[3*block+1],a.a.f[3*block+2]});for(int j=0;j<3;++j)covariance=std::max(covariance,std::abs(rotated[j]-b.a.f[3*block+j]));}
   for(int row=0;row<18;++row)for(int col=0;col<18;++col){double expected=0;for(int u=0;u<3;++u)for(int v=0;v<3;++v)expected+=axes[u][row%3]*A[3*(row/3)+u][3*(col/3)+v]*axes[v][col%3];jcov=std::max(jcov,std::abs(expected-B[row][col]));}
   double old=f0->committedPlastic;f0->commit(x);f1->commit(y);queryCommit=std::max(queryCommit,std::abs(f0->committedPlastic-old-a.D));
  }
 }
 std::cout<<std::setprecision(17)<<"CURVED_INVARIANTS {\"states\":90,\"covariance\":"<<covariance<<",\"force\":"<<force<<",\"moment\":"<<moment<<",\"jacobian_covariance\":"<<jcov<<",\"query_commit\":"<<queryCommit<<"}\n";
 if(covariance>1e-12||moment>1e-12||force>1e-12||jcov>1e-11||queryCommit>1e-15)throw std::runtime_error("actual field objectivity/action reaction failed");return 0;
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
