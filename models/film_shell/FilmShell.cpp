#include "Kernel.h"
#include "PlaneContact.h"
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/linearalgebra/BaseMatrix.h>
#include <sofa/linearalgebra/BaseVector.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateEndEvent.h>
#include <fstream>
#include <iomanip>
namespace regrip_film {
class FilmShell final:public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types>{
public:
 using Types=sofa::defaulttype::Vec3Types;using Base=sofa::core::behavior::ForceField<Types>;SOFA_CLASS(FilmShell,Base);
 sofa::core::objectmodel::Data<unsigned>nx,ny;
 sofa::core::objectmodel::Data<double>length,width,young,poisson,thickness;
 sofa::core::objectmodel::Data<std::string>filename;
 sofa::core::objectmodel::Data<double>plane,contactStiffness,observedTipForce,slopeFixture;
 sofa::core::objectmodel::Data<bool>displacementDofs,matrixProbe,slopeMapped;
 mutable std::vector<double>assemblyH;mutable bool assembled=false;bool exported=false;
 struct Element{std::vector<unsigned>ids;AD e;unsigned kind=0;};mutable std::vector<Element>cache;mutable VecCoord cachedX;mutable std::array<double,12>parameters{};mutable bool cached=false;mutable double contactArea=0,normalForce=0;std::ofstream journal;double last=-1;
 explicit FilmShell(sofa::core::behavior::MechanicalState<Types>*s=nullptr):Base(s),nx(initData(&nx,11u,"nx","Longitudinal nodes")),ny(initData(&ny,5u,"ny","Width nodes")),length(initData(&length,100.,"length","Reference length mm")),width(initData(&width,10.,"width","Reference width mm")),young(initData(&young,250.,"young","Assumed F/mm2")),poisson(initData(&poisson,.3,"poisson","Plane stress Poisson")),thickness(initData(&thickness,.1,"thickness","Single homogeneous film mm")),filename(initData(&filename,std::string(),"filename","Exclusive actual-state journal")),plane(initData(&plane,0.,"plane","Fixed world z stop, enabled only if contactStiffness>0")),contactStiffness(initData(&contactStiffness,0.,"contactStiffness","Plane penalty F/mm3;zero disables this contact")),observedTipForce(initData(&observedTipForce,0.,"observedTipForce","Observer-only external z load;MUST match scene ConstantForceField,does not apply force")),slopeFixture(initData(&slopeFixture,0.,"slopeFixture","Explicit world-z root slope fixture rigidity F per width;zero uses two fixed rows,not internal film stiffness")),displacementDofs(initData(&displacementDofs,false,"displacementDofs","Use displacement u DOFs;actual geometry=rest+u")),matrixProbe(initData(&matrixProbe,false,"matrixProbe","Diagnostic only:compare actual system matrix to same-stage analytical M/C/K")),slopeMapped(initData(&slopeMapped,false,"slopeMapped","Observer pullback for exact root slope mapping;not penalty fixture")){if(s)mstate.set(s);f_listening.setValue(true);}
 Film model()const{return Film(nx.getValue(),ny.getValue(),length.getValue(),width.getValue(),{young.getValue(),poisson.getValue(),thickness.getValue()});}
 static bool exactCoordinates(const VecCoord&a,const VecCoord&b){if(a.size()!=b.size())return false;for(unsigned i=0;i<a.size();++i)for(unsigned j=0;j<3;++j)if(a[i][j]!=b[i][j])return false;return true;}
 const std::vector<Element>&values(const VecCoord&x)const{auto m=model();std::array<double,12>p{double(m.nx),double(m.ny),m.L,m.W,m.material.E,m.material.nu,m.material.t,plane.getValue(),contactStiffness.getValue(),observedTipForce.getValue(),slopeFixture.getValue(),double(displacementDofs.getValue())};for(double v:p)if(!std::isfinite(v))throw std::invalid_argument("finite film parameters");if(contactStiffness.getValue()<0||slopeFixture.getValue()<0)throw std::invalid_argument("nonnegative film contact/fixture");if(cached&&p==parameters&&exactCoordinates(x,cachedX))return cache;std::vector<Point>q(x.size());for(unsigned i=0;i<x.size();++i)for(int j=0;j<3;++j)q[i][j]=x[i][j];cache.clear();m.elements(q,[&](const auto&ids,const AD&e,bool){cache.push_back({ids,e});},displacementDofs.getValue());contactArea=normalForce=0;
  if(slopeFixture.getValue()>0)for(unsigned j=0;j<m.ny;++j){std::vector<unsigned>ids{m.id(0,j),m.id(1,j),m.id(2,j)};AD slope;double coefficients[3]={-3,4,-1};for(int a=0;a<3;++a)slope=slope+AD(coefficients[a]*(m.nx-1)/(2*m.L))*AD::variable(q[ids[a]][2],3*a+2);double weight=m.W/(m.ny-1)*(j==0||j==m.ny-1?.5:1);cache.push_back({ids,AD(.5*slopeFixture.getValue()*weight)*slope*slope,1});}
  if(contactStiffness.getValue()>0)for(unsigned i=0;i<m.nx-1;++i)for(unsigned j=0;j<m.ny-1;++j)for(unsigned side=0;side<2;++side){std::vector<unsigned>ids=side?std::vector<unsigned>{m.id(i+1,j+1),m.id(i,j+1),m.id(i+1,j)}:std::vector<unsigned>{m.id(i,j),m.id(i+1,j),m.id(i,j+1)};std::array<AD,3>g;for(int a=0;a<3;++a)g[a]=AD::variable(q[ids[a]][2]-plane.getValue(),3*a+2);auto r=planeContact(g,.5*m.L*m.W/((m.nx-1)*(m.ny-1)),contactStiffness.getValue());cache.push_back({ids,r.energy,2});contactArea+=r.area.v;normalForce+=r.normalForce.v;}
  cachedX=x;parameters=p;cached=true;return cache;}
 void init()override{Base::init();if(!mstate)throw std::runtime_error("film missing state");values(mstate->read(sofa::core::vec_id::read_access::position)->getValue());if(!filename.getValue().empty()){std::ifstream previous(filename.getValue());if(previous)throw std::runtime_error("film journal already exists");journal.open(filename.getValue());journal<<std::setprecision(17)<<"time,U,max_speed,tip_z,free_force,contact_area,normal_force,x\n";}}
 unsigned traceCall=0;
 const DataVecCoord* forceStagePosition=nullptr;
 void traceForce(const VecCoord&x,const VecDeriv&v,const VecDeriv&internal){
  // Passive sampling at the actual force stage. RHS/solution belong to the
  // most recently solved linear system, NOT to this newly evaluated trial.
  if(!matrixProbe.getValue()||filename.getValue().empty())return;
  std::ofstream out(filename.getValue()+".stages.csv",std::ios::app);
  if(!traceCall)out<<"call,time,dt,scalar,x,v,internal,incoming_force,previous_rhs,previous_solution,constrained,film_force,fixture_force,contact_force\n";
  VecDeriv film(x.size()),fixture(x.size()),contact(x.size());
  for(const auto&e:cache)for(unsigned a=0;a<3*e.ids.size();++a){auto&target=e.kind==2?contact:(e.kind==1?fixture:film);target[e.ids[a/3]][a%3]-=e.e.g[a];}
  auto*system=getContext()->get<sofa::core::behavior::BaseMatrixLinearSystem>();
  auto*rhs=system?system->getSystemRHSBaseVector():nullptr;
  auto*solution=system?system->getSystemSolutionBaseVector():nullptr;
  auto*matrix=system?system->getSystemBaseMatrix():nullptr;
  if(assembled&&matrix&&matrix->rowSize()==int(3*x.size())){
   std::ofstream matrices(filename.getValue()+".stage_matrix.csv",std::ios::app);
   if(!traceMatrixCall++)matrices<<"call,time,relative_free_matrix_error,linear_residual_norm\n";
   double error=0,norm=0,linearResidual=0,dt=getContext()->getDt();unsigned size=3*x.size();
   unsigned skip=3*(slopeFixture.getValue()>0?1:2)*ny.getValue();
   for(unsigned i=skip;i<size;++i){double rowResidual=rhs&&solution? -rhs->element(i):0;for(unsigned j=skip;j<size;++j){
    double expected=dt*dt*assemblyH[i*size+j]+(i==j?1e-6/x.size()*(1+2*dt):0);
    double diff=matrix->element(i,j)-expected;error+=diff*diff;norm+=expected*expected;
    if(solution)rowResidual+=matrix->element(i,j)*solution->element(j);
   }linearResidual+=rowResidual*rowResidual;}
   matrices<<std::setprecision(17)<<traceCall<<','<<getContext()->getTime()<<','<<std::sqrt(error/norm)<<','<<std::sqrt(linearResidual)<<'\n';
  }
  out<<std::setprecision(17);
  for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j){unsigned k=3*i+j;
   out<<traceCall<<','<<getContext()->getTime()<<','<<getContext()->getDt()<<','<<k<<','<<x[i][j]<<','<<v[i][j]<<','<<internal[i][j]<<",null,";
   if(rhs&&k<unsigned(rhs->size()))out<<rhs->element(k);else out<<"null";
   out<<',';if(solution&&k<unsigned(solution->size()))out<<solution->element(k);else out<<"null";
   out<<','<<(i<(slopeFixture.getValue()>0?1:2)*ny.getValue())<<','<<film[i][j]<<','<<fixture[i][j]<<','<<contact[i][j]<<'\n';
  }++traceCall;
 }
 unsigned traceMatrixCall=0;
 void addForce(const sofa::core::MechanicalParams*,DataVecDeriv&f,const DataVecCoord&x,const DataVecDeriv&v)override{forceStagePosition=&x;auto out=f.getValue();VecDeriv internal(out.size());for(auto&e:values(x.getValue()))for(unsigned a=0;a<3*e.ids.size();++a){double force=-e.e.g[a];out[e.ids[a/3]][a%3]+=force;internal[e.ids[a/3]][a%3]+=force;}traceForce(x.getValue(),v.getValue(),internal);f.setValue(out);}
 void addDForce(const sofa::core::MechanicalParams*p,DataVecDeriv&df,const DataVecDeriv&dx)override{auto out=df.getValue();double factor=p->kFactorIncludingRayleighDamping(rayleighStiffness.getValue());for(auto&e:values(p->readX(mstate.get())->getValue()))for(unsigned a=0;a<3*e.ids.size();++a)for(unsigned b=0;b<3*e.ids.size();++b)out[e.ids[a/3]][a%3]-=factor*e.e.h[N*a+b]*dx.getValue()[e.ids[b/3]][b%3];df.setValue(out);}
 void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix*m)override{auto a=m->getForceDerivativeIn(mstate.get()).withRespectToPositionsIn(mstate.get());if(matrixProbe.getValue()){auto size=3*mstate->getSize();if(size>1000)throw std::invalid_argument("bounded diagnostic matrix");assemblyH.assign(size*size,0);assembled=true;}for(auto&e:values((forceStagePosition?forceStagePosition:mstate->read(sofa::core::vec_id::read_access::position))->getValue()))for(unsigned i=0;i<3*e.ids.size();++i)for(unsigned j=0;j<3*e.ids.size();++j)if(e.e.h[N*i+j]){auto row=3*e.ids[i/3]+i%3,col=3*e.ids[j/3]+j%3;a(row,col)+=-e.e.h[N*i+j];if(matrixProbe.getValue())assemblyH[row*(3*mstate->getSize())+col]+=e.e.h[N*i+j];}}
 SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord&x)const override{double u=0;for(auto&e:values(x.getValue()))u+=e.e.v;return u;}
 void handleEvent(sofa::core::objectmodel::Event*event)override{if(!dynamic_cast<sofa::simulation::AnimateEndEvent*>(event)||!journal)return;if(matrixProbe.getValue()&&assembled&&!exported){auto*system=getContext()->get<sofa::core::behavior::BaseMatrixLinearSystem>();auto*A=system?system->getSystemBaseMatrix():nullptr;if(A&&A->rowSize()==int(3*mstate->getSize())){unsigned size=A->rowSize(),skip=(slopeFixture.getValue()>0?1:2)*ny.getValue();double dt=getContext()->getDt(),error=0,norm=0;std::ofstream out(filename.getValue()+".matrix.csv");out<<std::setprecision(17)<<"row,col,actual,expected"<<std::endl;for(unsigned i=skip;i<size;++i)for(unsigned j=skip;j<size;++j){double expected=dt*dt*assemblyH[i*size+j]+(i==j?1e-6/mstate->getSize()*(1+2*dt):0),actual=A->element(i,j);error+=(expected-actual)*(expected-actual);norm+=expected*expected;if(expected||actual)out<<i<<','<<j<<','<<actual<<','<<expected<<std::endl;}msg_info()<<"FILM_MATRIX_RELATIVE "<<std::sqrt(error/norm);exported=true;}}double time=getContext()->getTime();if(time==last)return;last=time;auto&x=mstate->read(sofa::core::vec_id::read_access::position)->getValue();auto&v=mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();double speed=0,tip=0;for(auto&a:v)speed=std::max(speed,a.norm());for(unsigned j=0;j<ny.getValue();++j)tip+=x[x.size()-ny.getValue()+j][2]/ny.getValue();double U=0;for(auto&e:values(x))U+=e.e.v;
  std::vector<Point>force(x.size());for(auto&e:cache)for(unsigned a=0;a<3*e.ids.size();++a)force[e.ids[a/3]][a%3]-=e.e.g[a];for(unsigned j=0;j<ny.getValue();++j)force[x.size()-ny.getValue()+j][2]+=observedTipForce.getValue()/ny.getValue();if(slopeMapped.getValue())for(unsigned j=0;j<ny.getValue();++j){force[2*ny.getValue()+j][2]+=.25*force[ny.getValue()+j][2];force[ny.getValue()+j][2]=0;}double residual=0;for(unsigned i=(slopeFixture.getValue()>0||slopeMapped.getValue()?1:2)*ny.getValue();i<x.size();++i)residual+=dot(force[i],force[i]);
  journal<<time<<','<<U<<','<<speed<<','<<tip<<','<<std::sqrt(residual)<<','<<contactArea<<','<<normalForce<<",\"";auto rest=model().rest();for(unsigned i=0;i<x.size();++i)for(int j=0;j<3;++j)journal<<x[i][j]+(displacementDofs.getValue()?rest[i][j]:0)<<' ';journal<<"\"\n";journal.flush();}
};
}
namespace sofa::component::odesolver::backward { void registerReGripBDFSolver(sofa::core::ObjectFactory*); }
namespace regrip_film { void registerFilmSlopeMapping(sofa::core::ObjectFactory*); }
extern "C" {__attribute__((visibility("default")))void initExternalModule(){} __attribute__((visibility("default")))const char*getModuleName(){return "ReGripFilmShell";}__attribute__((visibility("default")))const char*getModuleVersion(){return "0.1-structured-film-ROM";}__attribute__((visibility("default")))void registerObjects(sofa::core::ObjectFactory*f){regrip_film::registerFilmSlopeMapping(f);sofa::component::odesolver::backward::registerReGripBDFSolver(f);f->registerObjects(sofa::core::ObjectRegistrationData("Independent flat-reference membrane plus nodal-curvature film ROM").add<regrip_film::FilmShell>());}}
