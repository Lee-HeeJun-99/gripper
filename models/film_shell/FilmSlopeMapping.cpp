#include <sofa/core/Mapping.h>
#include <sofa/core/Mapping.inl>
#include <sofa/linearalgebra/EigenSparseMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <Eigen/Sparse>

namespace regrip_film {
// Displacement-coordinate hard root slope: u_z(row1)=u_z(row2)/4,
// with row0 fixed. Parent row1 z is a redundant coordinate and MUST be fixed.
// This is a distinct boundary model, not a disguised change to penalty K.
class FilmSlopeMapping final:public sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>{
public:
 using Base=sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>;
 SOFA_CLASS(FilmSlopeMapping,Base);
 sofa::core::objectmodel::Data<unsigned>ny;
 sofa::linearalgebra::EigenSparseMatrix<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>J;
 sofa::type::vector<sofa::linearalgebra::BaseMatrix*>Js;
 FilmSlopeMapping():ny(initData(&ny,5u,"ny","Width nodes;displacement mapping only")){Js.push_back(&J);}
 bool isLinear()const override{return true;}
 const sofa::linearalgebra::BaseMatrix*getJ()override{return &J;}
 const sofa::type::vector<sofa::linearalgebra::BaseMatrix*>*getJs()override{return &Js;}
 void init()override{
  Base::init();unsigned n=this->fromModel->getSize(),w=ny.getValue();
  if(w<3||n<3*w||n%w)throw std::invalid_argument("film slope mapping grid");
  std::vector<Eigen::Triplet<double>>trip;
  for(unsigned i=0;i<n;++i)for(unsigned j=0;j<3;++j){unsigned row=3*i+j;trip.emplace_back(row,(i>=w&&i<2*w&&j==2)?3*(i+w)+2:row,(i>=w&&i<2*w&&j==2)?.25:1.);}
  J.compressedMatrix.resize(3*n,3*n);J.compressedMatrix.setFromTriplets(trip.begin(),trip.end());
 }
 void apply(const sofa::core::MechanicalParams*,OutDataVecCoord&out,const InDataVecCoord&in)override{auto q=in.getValue();unsigned w=ny.getValue();for(unsigned j=0;j<w;++j)q[w+j][2]=.25*q[2*w+j][2];out.setValue(q);}
 void applyJ(const sofa::core::MechanicalParams*p,OutDataVecDeriv&out,const InDataVecDeriv&in)override{apply(p,out,in);}
 void applyJT(const sofa::core::MechanicalParams*,InDataVecDeriv&out,const OutDataVecDeriv&in)override{
  auto f=out.getValue();const auto&g=in.getValue();unsigned w=ny.getValue();
  for(unsigned i=0;i<g.size();++i)for(unsigned j=0;j<3;++j)if(i>=w&&i<2*w&&j==2)f[i+w][2]+=.25*g[i][j];else f[i][j]+=g[i][j];out.setValue(f);
 }
 void applyJT(const sofa::core::ConstraintParams*,InDataMatrixDeriv&out,const OutDataMatrixDeriv&in)override{
  auto*target=out.beginEdit();unsigned w=ny.getValue();
  for(auto row=in.getValue().begin();row!=in.getValue().end();++row){auto line=target->writeLine(row.index());for(auto col=row.begin();col!=row.end();++col){auto v=col.val();unsigned i=col.index();if(i>=w&&i<2*w){auto extra=v;extra[0]=extra[1]=0;extra[2]*=.25;v[2]=0;line.addCol(i+w,extra);}line.addCol(i,v);}}
  out.endEdit();
 }
};
void registerFilmSlopeMapping(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Exact displacement root slope mapping;distinct hard-clamp boundary model").add<FilmSlopeMapping>());}
}
