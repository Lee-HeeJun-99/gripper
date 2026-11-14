// V1.1.0 research prototype: SMALL-ROTATION, LOCAL X SHEAR ONLY.
// DOF order in SOFA Rigid3d derivative: [vx,vy,vz, wx,wy,wz].
// Each corresponding lower/upper pair has s = (xu-xl)-h/2*(theta_yu+theta_yl).
// theta_y ~= 2 * q_y near the identity orientation. This approximation is deliberate.
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/StiffnessMatrix.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/helper/accessor/WriteAccessor.h>
#include <sofa/helper/accessor/ReadAccessor.h>
#include <cmath>

namespace tangential_v110 {
using Types=sofa::defaulttype::Rigid3Types;
using Inherit=sofa::core::behavior::ForceField<Types>;
class TangentialRigidForceField final : public Inherit {
public:
    SOFA_CLASS(TangentialRigidForceField, Inherit);
    using DataVecDeriv = Inherit::DataVecDeriv;
    using DataVecCoord = Inherit::DataVecCoord;
    using VecDeriv = Inherit::VecDeriv;
    using VecCoord = Inherit::VecCoord;

    sofa::core::objectmodel::Data<double> d_stiffness;
    sofa::core::objectmodel::Data<double> d_layerThickness;
    sofa::core::objectmodel::Data<unsigned> d_nodesPerLayer;
    sofa::core::objectmodel::Data<bool> d_includeRoot;
    TangentialRigidForceField()
      : d_stiffness(initData(&d_stiffness,0.01,"stiffness","Per-pair tangential stiffness"))
      , d_layerThickness(initData(&d_layerThickness,0.4,"layerThickness","Layer centroid separation (mm)"))
      , d_nodesPerLayer(initData(&d_nodesPerLayer,11u,"nodesPerLayer","Number of rigid nodes in each beam"))
      , d_includeRoot(initData(&d_includeRoot,false,"includeRoot","Connect clamped root too")) {}

    // Force = - k * b^T * s. Four nonzero coordinates per pair.
    // b = [ lower_x:-1, lower_theta_y:-h/2, upper_x:+1, upper_theta_y:-h/2 ].
    static double b(int j, double h) {
        switch(j) {case 0:return -1.;case 1:return -0.5*h;
                   case 2:return  1.;default:return -0.5*h;}
    }
    unsigned index(unsigned i,int j,unsigned n) const {
        return j<2 ? i : n+i;
    }
    unsigned axis(int j) const {return (j%2==0)?0u:4u;}
    double shear(const VecCoord& x, unsigned i, unsigned n, double h) const {
        // V1.1.0 valid only for |theta| << 1 rad.
        auto thetaL = 2.0 * x[i].getOrientation()[1];
        auto thetaU = 2.0 * x[n+i].getOrientation()[1];
        return x[n+i].getCenter()[0]-x[i].getCenter()[0]
                 -0.5*h*(thetaU+thetaL);
    }
    void addForce(const sofa::core::MechanicalParams*,DataVecDeriv& force,
                  const DataVecCoord& position,const DataVecDeriv&) override {
        auto f=sofa::helper::getWriteAccessor(force);
        auto x=sofa::helper::getReadAccessor(position);
        const auto n=d_nodesPerLayer.getValue();
        if(n==0 || x.size()!=2*n || f.size()!=2*n) return;
        const double k=d_stiffness.getValue(),h=d_layerThickness.getValue();
        for(unsigned i=(d_includeRoot.getValue()?0u:1u);i<n;++i) {
            double s=shear(x.ref(),i,n,h); // x.ref() underlying VecCoord
            for(int a=0;a<4;++a) f[index(i,a,n)][axis(a)] += -k*b(a,h)*s;
        }
    }
    void addDForce(const sofa::core::MechanicalParams* mp,DataVecDeriv& dforce,
                   const DataVecDeriv& dx) override {
        auto df=sofa::helper::getWriteAccessor(dforce);
        auto u=sofa::helper::getReadAccessor(dx);
        const auto n=d_nodesPerLayer.getValue();
        if(n==0 || u.size()!=2*n || df.size()!=2*n) return;
        const double h=d_layerThickness.getValue(),factor=mp->kFactor(),k=d_stiffness.getValue();
        for(unsigned i=(d_includeRoot.getValue()?0u:1u);i<n;++i) {
            double ds=0.;
            for(int a=0;a<4;++a) ds+=b(a,h)*u[index(i,a,n)][axis(a)];
            for(int a=0;a<4;++a) df[index(i,a,n)][axis(a)] += -factor*k*b(a,h)*ds;
        }
    }
    void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix* matrix) override {
        const auto n=d_nodesPerLayer.getValue();
        const double h=d_layerThickness.getValue(),k=d_stiffness.getValue();
        auto dfdx=matrix->getForceDerivativeIn(this->mstate.get())
                         .withRespectToPositionsIn(this->mstate.get());
        for(unsigned i=(d_includeRoot.getValue()?0u:1u);i<n;++i)
           for(int a=0;a<4;++a)
             for(int c=0;c<4;++c) {
                 unsigned row=6*index(i,a,n)+axis(a);
                 unsigned col=6*index(i,c,n)+axis(c);
                 dfdx(row,col)+=-k*b(a,h)*b(c,h);
             }
    }
    sofa::SReal getPotentialEnergy(const sofa::core::MechanicalParams*,
                                  const DataVecCoord& position) const override {
        auto x=sofa::helper::getReadAccessor(position);
        const auto n=d_nodesPerLayer.getValue();
        if(n==0 || x.size()!=2*n) return 0.;
        const double k=d_stiffness.getValue(),h=d_layerThickness.getValue();
        double e=0.;
        for(unsigned i=(d_includeRoot.getValue()?0u:1u);i<n;++i) {
            auto tl=2.*x[i].getOrientation()[1], tu=2.*x[n+i].getOrientation()[1];
            double s=x[n+i].getCenter()[0]-x[i].getCenter()[0]-.5*h*(tl+tu);
            e+=.5*k*s*s;
        }
        return e;
    }
};

void registerTangentialRigidForceField(sofa::core::ObjectFactory* factory) {
    factory->registerObjects(sofa::core::ObjectRegistrationData(
        "Small-angle X-tangential shear coupling for bilayer Rigid3d beams; analytical Jacobian")
        .add<TangentialRigidForceField>());
}
} // namespace
