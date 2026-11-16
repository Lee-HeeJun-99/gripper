#include <sofa/core/Mapping.h>
#include <sofa/core/Mapping.inl>
#include <sofa/linearalgebra/EigenSparseMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <Eigen/Sparse>
namespace regrip_film {
// Independent third-order root derivative discretization, not a force fix.
// (-11u0+18u1-9u2+2u3)/(6dx)=0 and u0=0 =>u1=u2/2-u3/9.
// Exact for clamped cubic Euler-Bernoulli shapes. Old 3-point slope mapping
// remains unchanged. This maps displacement coordinates; row1 z is redundant.
class FilmCubicSlopeMapping final:public sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>{
public:
 using Base=sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(FilmCubicSlopeMapping,Base);
 sofa::core::objectmodel::Data<unsigned>ny;
 sofa::linearalgebra::EigenSparseMatrix<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>J;
 sofa::type::vector<sofa::linearalgebra::BaseMatrix*>Js;
 FilmCubicSlopeMapping():ny(initData(&ny,5u,"ny","Width nodes;third-order root derivative")){Js.push_back(&J);}
 bool isLinear()const override{return true;}
 const sofa::linearalgebra::BaseMatrix*getJ()override{return &J;}
 const sofa::type::vector<sofa::linearalgebra::BaseMatrix*>*getJs()override{return &Js;}
 void init()override{
  if(!this->fromModel||!this->toModel)throw std::invalid_argument("cubic slope needs two states");
  unsigned n=this->fromModel->getSize(),w=ny.getValue();if(w<3||n<4*w||n%w)throw std::invalid_argument("cubic slope grid");
  std::vector<Eigen::Triplet<double>>trip;
  for(unsigned i=0;i<n;++i)for(unsigned j=0;j<3;++j){unsigned row=3*i+j;if(i>=w&&i<2*w&&j==2){trip.emplace_back(row,3*(i+w)+2,.5);trip.emplace_back(row,3*(i+2*w)+2,-1./9);}else trip.emplace_back(row,row,1.);}
  J.compressedMatrix.resize(3*n,3*n);J.compressedMatrix.setFromTriplets(trip.begin(),trip.end());Base::init();
 }
 void apply(const sofa::core::MechanicalParams*,OutDataVecCoord&out,const InDataVecCoord&in)override{auto q=in.getValue();unsigned w=ny.getValue();if(q.size()<4*w)throw std::invalid_argument("cubic slope state size");for(unsigned j=0;j<w;++j)q[w+j][2]=.5*q[2*w+j][2]-q[3*w+j][2]/9;out.setValue(q);}
 void applyJ(const sofa::core::MechanicalParams*p,OutDataVecDeriv&out,const InDataVecDeriv&in)override{apply(p,out,in);}
 void applyJT(const sofa::core::MechanicalParams*,InDataVecDeriv&out,const OutDataVecDeriv&in)override{
  auto f=out.getValue();const auto&g=in.getValue();unsigned w=ny.getValue();if(f.size()!=g.size()||f.size()<4*w)throw std::invalid_argument("cubic slope force size");
  for(unsigned i=0;i<g.size();++i)for(unsigned j=0;j<3;++j)if(i>=w&&i<2*w&&j==2){f[i+w][2]+=.5*g[i][j];f[i+2*w][2]-=g[i][j]/9;}else f[i][j]+=g[i][j];out.setValue(f);
 }
 void applyJT(const sofa::core::ConstraintParams*,InDataMatrixDeriv&out,const OutDataMatrixDeriv&in)override{
  auto*target=out.beginEdit();unsigned w=ny.getValue();
  for(auto row=in.getValue().begin();row!=in.getValue().end();++row){auto line=target->writeLine(row.index());for(auto col=row.begin();col!=row.end();++col){auto v=col.val();unsigned i=col.index();if(i>=w&&i<2*w){auto extra=v;extra[0]=extra[1]=0;extra[2]=.5*v[2];line.addCol(i+w,extra);extra[2]=-v[2]/9;line.addCol(i+2*w,extra);v[2]=0;}line.addCol(i,v);}}out.endEdit();
 }
};
void registerFilmCubicSlopeMapping(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Independent cubic-exact root slope displacement mapping;not the original boundary discretization").add<FilmCubicSlopeMapping>());}
}
