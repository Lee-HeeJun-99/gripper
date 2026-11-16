#include <sofa/component/linearsystem/MatrixLinearSystem.h>
#include <sofa/component/linearsystem/MappedMassMatrixObserver.h>
#include <sofa/linearalgebra/CompressedRowSparseMatrix.h>
#include <sofa/linearalgebra/FullVector.h>
#include <sofa/core/ObjectFactory.h>
namespace regrip_film {
using FilmMatrix=sofa::linearalgebra::CompressedRowSparseMatrix<SReal>;
using FilmVector=sofa::linearalgebra::FullVector<SReal>;
using FilmSystemBase=sofa::component::linearsystem::MatrixLinearSystem<FilmMatrix,FilmVector>;
// Independent SDK adapter; installed engine is untouched. In this matching
// SDK, invariant projected mapped mass includes the current MBK factor but
// its observer tracks only component state, not changes in that factor.
// Refresh that cache using the SDK's protected assembly interface. No force,
// mass, boundary, Newton tolerance or time-integration equation is changed.
class ReGripMatrixLinearSystem final:public FilmSystemBase {
public:
 SOFA_CLASS(ReGripMatrixLinearSystem,FilmSystemBase);
protected:
 void assembleSystem(const sofa::core::MechanicalParams*p) override {
  for(const auto&observer:m_mappedMassMatrixObservers)
   if(observer->m_invariantMassMatrix)recomputeMappedMassMatrix(p,observer->getObservableMass());
  FilmSystemBase::assembleSystem(p);
 }
};
void registerReGripMatrixLinearSystem(sofa::core::ObjectFactory*f){f->registerObjects(sofa::core::ObjectRegistrationData("Matching-SDK independent mapped-mass factor refresh;not a force correction").add<ReGripMatrixLinearSystem>());}
}
