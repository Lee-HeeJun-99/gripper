// V110 intended linear-in-angle energy on its small planar-rotation domain.
// Recover theta_y=2*atan2(q_y,q_w); 2*q_y is not the angular coordinate.
// SOFA Rigid3d derivatives: [vx,vy,vz, wx,wy,wz].
#include <sofa/core/behavior/ForceField.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/helper/accessor/WriteAccessor.h>
#include <sofa/helper/accessor/ReadAccessor.h>
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>

namespace tangential_v110 {
using Types=sofa::defaulttype::Rigid3Types;
using Inherit=sofa::core::behavior::ForceField<Types>;

class TangentialRigidForceField final : public Inherit {
public:
    SOFA_CLASS(TangentialRigidForceField, Inherit);
    using DataVecDeriv=Inherit::DataVecDeriv;
    using DataVecCoord=Inherit::DataVecCoord;
    using VecDeriv=Inherit::VecDeriv;
    using VecCoord=Inherit::VecCoord;
    sofa::core::objectmodel::Data<double> d_stiffness,d_layerThickness;
    sofa::core::objectmodel::Data<unsigned> d_nodesPerLayer;
    sofa::core::objectmodel::Data<bool> d_includeRoot;
    sofa::core::objectmodel::Data<sofa::type::vector<unsigned>> d_connectorIndices;
    unsigned forceCalls=0,dforceCalls=0,matrixCalls=0;
    bool reportedError=false;

    explicit TangentialRigidForceField(sofa::core::behavior::MechanicalState<Types>* state=nullptr)
      : Inherit(state)
      , d_stiffness(initData(&d_stiffness,.01,"stiffness","Per-pair tangential stiffness"))
      , d_layerThickness(initData(&d_layerThickness,.4,"layerThickness","Centroid separation (mm)"))
      , d_nodesPerLayer(initData(&d_nodesPerLayer,11u,"nodesPerLayer","Rigid nodes per beam"))
      , d_includeRoot(initData(&d_includeRoot,false,"includeRoot","Connect clamped root"))
      , d_connectorIndices(initData(&d_connectorIndices,"connectorIndices","Selected indices; empty = all eligible nodes")) {
        if(state)this->mstate.set(state);
    }

    void fail(const char* why) {
        if(!reportedError) { msg_error()<<why;reportedError=true; }
        this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
    }
    bool parameters() {
        const double k=d_stiffness.getValue(),h=d_layerThickness.getValue();
        const auto n=d_nodesPerLayer.getValue();
        if(!std::isfinite(k)||k<0||!std::isfinite(h)||h<=0||!std::isfinite(k*h*h)||
           n==0||n>std::numeric_limits<unsigned>::max()/12) {
            fail("Invalid stiffness, thickness or node count");return false;
        }
        const auto& ids=d_connectorIndices.getValue();
        for(std::size_t j=0;j<ids.size();++j)
            if(ids[j]>=n||(!d_includeRoot.getValue()&&ids[j]==0)||
               std::find(ids.begin(),ids.begin()+j,ids[j])!=ids.begin()+j) {
                fail("Invalid or duplicate connector index");return false;
            }
        return true;
    }
    bool positions(const VecCoord& x) {
        if(!parameters()||x.size()!=2*std::size_t(d_nodesPerLayer.getValue())) {
            fail("Mechanical position size mismatch");return false;
        }
        for(const auto& p:x) {
            const auto& q=p.getOrientation();
            for(unsigned j=0;j<3;++j)if(!std::isfinite(p.getCenter()[j])) {
                fail("Nonfinite position");return false;
            }
            double norm=0;
            for(unsigned j=0;j<4;++j) {
                if(!std::isfinite(q[j])) {fail("Nonfinite quaternion");return false;}
                norm+=q[j]*q[j];
            }
            const double angle=2*std::atan2(std::sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]),q[3]);
            if(std::abs(norm-1)>1e-8||q[3]<=0||std::abs(q[0])>1e-8||std::abs(q[2])>1e-8||angle>=.005) {
                fail("Quaternion outside validated small planar rotation domain");return false;
            }
        }
        return true;
    }
    void init() override {
        Inherit::init();
        if(!this->mstate||!positions(this->mstate->read(sofa::core::vec_id::read_access::position)->getValue()))
            fail("Invalid initial mechanical state");
    }
    bool selected(unsigned i) const {
        const auto& ids=d_connectorIndices.getValue();
        return ids.empty()||std::find(ids.begin(),ids.end(),i)!=ids.end();
    }
    unsigned index(unsigned i,int j,unsigned n) const {return j<2?i:n+i;}
    unsigned axis(int j) const {return j%2==0?0u:4u;}
    double shear(const VecCoord& x,unsigned i,unsigned n,double h) const {
        const auto& lower=x[i].getOrientation();
        const auto& upper=x[n+i].getOrientation();
        return x[n+i].getCenter()[0]-x[i].getCenter()[0]
             -h*(std::atan2(lower[1],lower[3])+std::atan2(upper[1],upper[3]));
    }
    std::array<double,4> gradient(const VecCoord&,unsigned,unsigned) const {
        const double a=d_layerThickness.getValue()/2;
        return {-1.,-a,1.,-a};
    }
    double jacobian(const VecCoord& x,unsigned i,unsigned n,int a,int c) const {
        const double k=d_stiffness.getValue();
        const auto g=gradient(x,i,n);
        return -k*g[a]*g[c];
    }

    void addForce(const sofa::core::MechanicalParams*,DataVecDeriv& force,
                  const DataVecCoord& position,const DataVecDeriv&) override {
        const auto& x=position.getValue();
        if(!positions(x)||force.getValue().size()!=x.size()) {fail("Force size/input mismatch");return;}
        if(++forceCalls==1)std::cout<<"REGRIP_ADD_FORCE\n";
        auto f=sofa::helper::getWriteAccessor(force);
        const auto n=d_nodesPerLayer.getValue();
        for(unsigned i=d_includeRoot.getValue()?0u:1u;i<n;++i)if(selected(i)) {
            const auto g=gradient(x,i,n);
            const double s=shear(x,i,n,d_layerThickness.getValue());
            for(int a=0;a<4;++a) {
                const double value=-d_stiffness.getValue()*g[a]*s;
                if(!std::isfinite(value)) {fail("Force overflow");return;}
                f[index(i,a,n)][axis(a)]+=value;
            }
        }
    }
    void addDForce(const sofa::core::MechanicalParams* mp,DataVecDeriv& dforce,
                   const DataVecDeriv& dx) override {
        if(!mp||!this->mstate) {fail("Missing mechanical parameters/state");return;}
        const auto& x=this->mstate->read(sofa::core::vec_id::read_access::position)->getValue();
        if(!positions(x)||dx.getValue().size()!=x.size()||dforce.getValue().size()!=x.size()) {
            fail("Differential force size/input mismatch");return;
        }
        if(!std::isfinite(mp->kFactor())) {fail("Nonfinite kFactor");return;}
        if(++dforceCalls==1)std::cout<<"REGRIP_ADD_DFORCE\n";
        const auto n=d_nodesPerLayer.getValue();
        auto df=sofa::helper::getWriteAccessor(dforce);
        const auto& u=dx.getValue();
        for(unsigned i=d_includeRoot.getValue()?0u:1u;i<n;++i)if(selected(i))
            for(int a=0;a<4;++a) {
                double value=0;
                for(int c=0;c<4;++c)value+=jacobian(x,i,n,a,c)*u[index(i,c,n)][axis(c)];
                value*=mp->kFactor();
                if(!std::isfinite(value)) {fail("Differential force overflow");return;}
                df[index(i,a,n)][axis(a)]+=value;
            }
    }
    void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix* matrix) override {
        if(!matrix||!this->mstate) {fail("Missing stiffness matrix/state");return;}
        const auto& x=this->mstate->read(sofa::core::vec_id::read_access::position)->getValue();
        if(!positions(x))return;
        auto dfdx=matrix->getForceDerivativeIn(this->mstate.get()).withRespectToPositionsIn(this->mstate.get());
        if(!dfdx) {fail("Missing matrix accumulator");return;}
        if(++matrixCalls==1)std::cout<<"REGRIP_BUILD_STIFFNESS\n";
        const auto n=d_nodesPerLayer.getValue();
        for(unsigned i=d_includeRoot.getValue()?0u:1u;i<n;++i)if(selected(i))
            for(int a=0;a<4;++a)for(int c=0;c<4;++c) {
                const double value=jacobian(x,i,n,a,c);
                if(!std::isfinite(value)) {fail("Matrix overflow");return;}
                dfdx(6*index(i,a,n)+axis(a),6*index(i,c,n)+axis(c))+=value;
            }
    }
    SReal getPotentialEnergy(const sofa::core::MechanicalParams*,const DataVecCoord& position) const override {
        auto* self=const_cast<TangentialRigidForceField*>(this);
        const auto& x=position.getValue();
        if(!self->positions(x))return std::numeric_limits<double>::quiet_NaN();
        const auto n=d_nodesPerLayer.getValue();
        double energy=0;
        for(unsigned i=d_includeRoot.getValue()?0u:1u;i<n;++i)if(selected(i)) {
            const double s=shear(x,i,n,d_layerThickness.getValue());
            energy+=.5*d_stiffness.getValue()*s*s;
        }
        return energy;
    }
};
void registerTangentialRigidForceField(sofa::core::ObjectFactory* factory) {
    factory->registerObjects(sofa::core::ObjectRegistrationData(
        "Small planar tangential shear with a consistent energy gradient and tangent")
        .add<TangentialRigidForceField>());
}
} // namespace
