#include "Kernel.h"
#include <sofa/core/Mapping.h>
#include <sofa/core/Mapping.inl>
#include <sofa/linearalgebra/EigenSparseMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/VecTypes.h>
#include <Eigen/Sparse>
namespace regrip_film_rail {
class FilmAssemblyRootMapping final:public sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>{
public:
 using Base=sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>;SOFA_CLASS(FilmAssemblyRootMapping,Base);
 sofa::core::objectmodel::Data<unsigned>nx;
 sofa::linearalgebra::EigenSparseMatrix<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>J;sofa::type::vector<sofa::linearalgebra::BaseMatrix*>Js;
 FilmAssemblyRootMapping():nx(initData(&nx,21u,"nx","Nodes of three independent strips")){Js.push_back(&J);}
 bool isLinear()const override{return true;}const sofa::linearalgebra::BaseMatrix*getJ()override{return &J;}const sofa::type::vector<sofa::linearalgebra::BaseMatrix*>*getJs()override{return &Js;}
 std::pair<unsigned,double>map(unsigned i,unsigned j)const{unsigned n=nx.getValue();for(auto [offset,width]:std::array<std::pair<unsigned,unsigned>,3>{{{0,5},{5*n,3},{8*n,3}}})if(i>=offset+width&&i<offset+2*width&&j==2)return {i+width,.25};return {i,1};}
 void init()override{Assembly m(nx.getValue());if(!this->fromModel||!this->toModel||this->fromModel->getSize()!=m.size())throw std::invalid_argument("assembly root mapping size");std::vector<Eigen::Triplet<double>>trip;for(unsigned i=0;i<m.size();++i)for(unsigned j=0;j<3;++j){auto [node,w]=map(i,j);trip.emplace_back(3*i+j,3*node+j,w);}J.compressedMatrix.resize(3*m.size(),3*m.size());J.compressedMatrix.setFromTriplets(trip.begin(),trip.end());Base::init();}
 void apply(const sofa::core::MechanicalParams*,OutDataVecCoord&out,const InDataVecCoord&in)override{const auto&x=in.getValue();auto y=x;if(x.size()!=Assembly(nx.getValue()).size())throw std::invalid_argument("assembly map input");for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j){auto [node,w]=map(i,j);y[i][j]=w*x[node][j];}out.setValue(y);}
 void applyJ(const sofa::core::MechanicalParams*p,OutDataVecDeriv&o,const InDataVecDeriv&i)override{apply(p,o,i);}
 void applyJT(const sofa::core::MechanicalParams*,InDataVecDeriv&out,const OutDataVecDeriv&in)override{auto y=out.getValue();const auto&x=in.getValue();if(y.size()!=x.size())throw std::invalid_argument("assembly force map");for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j){auto [node,w]=map(i,j);y[node][j]+=w*x[i][j];}out.setValue(y);}
 void applyJT(const sofa::core::ConstraintParams*,InDataMatrixDeriv&out,const OutDataMatrixDeriv&in)override{auto*target=out.beginEdit();for(auto r=in.getValue().begin();r!=in.getValue().end();++r){auto line=target->writeLine(r.index());for(auto c=r.begin();c!=r.end();++c)for(unsigned j=0;j<3;++j){auto[node,w]=map(c.index(),j);auto value=c.val();for(unsigned k=0;k<3;++k)value[k]=k==j?w*value[k]:0;line.addCol(node,value);}}out.endEdit();}
};
void registerFilmAssemblyRootMapping(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Independent block root-slope mapping for skin and both flexible rails").add<FilmAssemblyRootMapping>());}
class FilmAssemblyWorldMapping final:public sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>{
public:
 using Base=sofa::core::Mapping<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>;SOFA_CLASS(FilmAssemblyWorldMapping,Base);
 sofa::core::objectmodel::Data<unsigned>nx;sofa::linearalgebra::EigenSparseMatrix<sofa::defaulttype::Vec3Types,sofa::defaulttype::Vec3Types>J;sofa::type::vector<sofa::linearalgebra::BaseMatrix*>Js;
 FilmAssemblyWorldMapping():nx(initData(&nx,21u,"nx","Actual world geometry=declared rest+displacement")){Js.push_back(&J);}
 bool isLinear()const override{return true;}const sofa::linearalgebra::BaseMatrix*getJ()override{return &J;}const sofa::type::vector<sofa::linearalgebra::BaseMatrix*>*getJs()override{return &Js;}
 void init()override{unsigned n=Assembly(nx.getValue()).size();if(!this->fromModel||this->fromModel->getSize()!=n)throw std::invalid_argument("assembly world map size");J.compressedMatrix.resize(3*n,3*n);J.compressedMatrix.setIdentity();Base::init();}
 void apply(const sofa::core::MechanicalParams*,OutDataVecCoord&out,const InDataVecCoord&in)override{auto x=in.getValue();auto rest=Assembly(nx.getValue()).rest();if(x.size()!=rest.size())throw std::invalid_argument("world map input");for(unsigned i=0;i<x.size();++i)for(unsigned j=0;j<3;++j)x[i][j]+=rest[i][j];out.setValue(x);}
 void applyJ(const sofa::core::MechanicalParams*,OutDataVecDeriv&out,const InDataVecDeriv&in)override{out.setValue(in.getValue());}
 void applyJT(const sofa::core::MechanicalParams*,InDataVecDeriv&out,const OutDataVecDeriv&in)override{auto x=out.getValue();const auto&f=in.getValue();if(x.size()!=f.size())throw std::invalid_argument("world force map");for(unsigned i=0;i<x.size();++i)x[i]+=f[i];out.setValue(x);}
 void applyJT(const sofa::core::ConstraintParams*,InDataMatrixDeriv&out,const OutDataMatrixDeriv&in)override{auto*x=out.beginEdit();for(auto r=in.getValue().begin();r!=in.getValue().end();++r){auto row=x->writeLine(r.index());for(auto c=r.begin();c!=r.end();++c)row.addCol(c.index(),c.val());}out.endEdit();}
};
void registerFilmAssemblyWorldMapping(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Explicit rest+u actual-coordinate mapping with identity virtual-work pullback").add<FilmAssemblyWorldMapping>());}
}
