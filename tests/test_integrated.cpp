#include "../models/integrated/Components.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
#include <random>
using namespace regrip_integrated;
void check(bool b,const char*m){if(!b)throw std::runtime_error(m);}
struct Acc:sofa::core::behavior::StiffnessMatrixAccumulator{
 double data[96][96]{};void add(sofa::SignedIndex r,sofa::SignedIndex c,double v)override{data[r][c]+=v;}void add(sofa::SignedIndex r,sofa::SignedIndex c,float v)override{add(r,c,double(v));}
};
template<class Function>void difference(Function fun,Pose a,Pose b,double&eg,double&jg){auto r=energy_result(fun(a,b));for(int i=0;i<12;++i){Pose ap=a,am=a,bp=b,bm=b;double step=1e-6;if(i<6){ap=increment(a,i,step);am=increment(a,i,-step);}else{bp=increment(b,i-6,step);bm=increment(b,i-6,-step);}auto p=energy_result(fun(ap,bp)),m=energy_result(fun(am,bm));eg=std::max(eg,std::abs((p.energy-m.energy)/(2*step)+r.force[i]));for(int j=0;j<12;++j)jg=std::max(jg,std::abs((p.force[j]-m.force[j])/(2*step)-r.jacobian[12*j+i]));}}
int main(){try{
 std::mt19937 rng(118);std::uniform_real_distribution<double>d(-.6,.6);double eg=0,jg=0;
 for(int i=0;i<60;++i){Pose a{{3+d(rng),.1+d(rng),.1+d(rng)},exp(V{d(rng),d(rng),d(rng)})},b{{0,0,0},exp(V{d(rng),d(rng),d(rng)})};
  difference([](auto&l,auto&u){auto length=cable_segment(l,u,V{0,0,-.2});return Jet(.05)*length*length;},a,b,eg,jg);
 }
 // Smooth contact locations deliberately away from shape seams/corners.
 for(int shape=0;shape<3;++shape)for(int i=0;i<20;++i){Pose a{{4.7,.2,.1},exp(V{d(rng),d(rng),d(rng)})},b{{0,0,0},{0,0,0,1}};
  difference([&](auto&p,auto&o){return contact_energy(p,o,shape,V{5,4,3},V{0,0,0},.1,.01);},a,b,eg,jg);
  auto f=[&](const Pose&p,const Pose&o){return contact_energy(p,o,shape,V{5,4,3},V{0,0,0},.1,.01).v;};auto q=exp(V{.4,-.3,.2});V t{1,2,-1};Pose ar{add(rotate(q,a.p),t),multiply(q,a.q)},br{add(rotate(q,b.p),t),multiply(q,b.q)};check(std::abs(f(a,b)-f(ar,br))<1e-13,"contact objectivity");
 }
 check(eg<1e-8,"kernel energy finite difference");check(jg<1e-7,"kernel spatial Jacobian finite difference");
 double z=0,D=0,E=0,W=0,prevS=0,prevT=0;for(int i=0;i<=80;++i){double s=i<=20?i*.01:(i<=60?(40-i)*.01:(i-80)*.01);auto r=slider(s,z,10,1);D+=r.dissipation;W+=.5*(prevT+r.traction)*(s-prevS);E=r.energy;z=r.plastic;prevS=s;prevT=r.traction;}check(std::abs(W-E-D)<1e-12,"slider work balance");
 auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<Types>>();state->resize(12);auto layer=sofa::core::objectmodel::New<LayerNetwork>(state.get());layer->nodes.setValue(3);layer->layers.setValue(4);layer->stiffness.setValue(2.);
 Inherit::VecCoord x(12);for(int l=0;l<4;++l)for(int n=0;n<3;++n){auto&i=x[3*l+n];i.getCenter()[0]=n*50.;i.getCenter()[2]=(l-1.5)*.4;i.getOrientation()=sofa::type::Quat<double>(0,0,0,1);}x[11].getCenter()[0]+=.001;state->write(sofa::core::vec_id::write_access::position)->setValue(x);
 auto assembly=layer->assemble(x);check(std::abs(assembly.f[6*11]+.002)<1e-14,"multilayer force");
 Acc acc;sofa::core::behavior::StiffnessMatrix m;m.setMatrixAccumulator(&acc,state.get());layer->buildStiffnessMatrix(&m);double expected[96][96]{};for(auto&t:assembly.J)expected[t.r][t.c]+=t.v;
 for(int i=0;i<72;++i)for(int j=0;j<72;++j)check(std::abs(acc.data[i][j]-expected[i][j])<1e-14,"multilayer API matrix");
 Inherit::DataVecDeriv dx,df;Inherit::VecDeriv delta(12);delta[11][0]=.01;dx.setValue(delta);df.setValue(Inherit::VecDeriv(12));sofa::core::MechanicalParams mp;mp.setKFactor(2.5);layer->addDForce(&mp,df,dx);check(std::abs(df.getValue()[11][0]+.05)<1e-14,"multilayer kFactor");
 auto cable=sofa::core::objectmodel::New<RoutedCable>(state.get());cable->route.setValue({0,1,2});cable->tension.setValue(.001);auto c=cable->assemble(x);check(std::abs(c.cableLength-100)<1e-12,"cable rest geometry");check(c.f[6*2]<0&&c.f[6*2+4]>0,"cable bending direction");
 bool rejected=false;try{slider(0,0,0,1);}catch(const std::invalid_argument&){rejected=true;}check(rejected,"invalid slider input");
 std::cout<<"PASS cable/contact 120 states; energy_fd="<<eg<<" spatial_jacobian_fd="<<jg<<" slider_work_balance="<<std::abs(W-E-D)<<"; multilayer actual API/6DOF/kFactor\n";return 0;
 }catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}}
