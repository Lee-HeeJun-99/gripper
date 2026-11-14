// Diagnostic probe deliberately exercises inputs omitted by the historical tests.
#include "../plugin/src/TangentialRigidForceField.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <iostream>
#include <limits>

int main(int argc,char** argv) {
    using F=tangential_v110::TangentialRigidForceField;
    if(argc!=2)return 2;
    auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<tangential_v110::Types>>();
    state->resize(4);
    auto field=sofa::core::objectmodel::New<F>(state.get());
    field->d_nodesPerLayer.setValue(2);
    F::VecCoord x(4);
    for(auto& p:x)p.getOrientation()=sofa::type::Quat<double>(0,0,0,1);
    F::DataVecCoord pos;F::DataVecDeriv force,vel;
    force.setValue(F::VecDeriv(4));vel.setValue(F::VecDeriv(4));
    std::string mode=argv[1];
    if(mode=="null_matrix") {field->buildStiffnessMatrix(nullptr);return 0;}
    if(mode=="nan_stiffness") {
        field->d_stiffness.setValue(std::numeric_limits<double>::quiet_NaN());
        x[3].getCenter()[0]=.001;pos.setValue(x);
        field->addForce(nullptr,force,pos,vel);
        for(const auto& f:force.getValue())for(int a=0;a<6;++a)if(!std::isfinite(f[a]))return 1;
        return 0;
    }
    if(mode=="negative_stiffness")field->d_stiffness.setValue(-1);
    if(mode=="zero_nodes")field->d_nodesPerLayer.setValue(0);
    if(mode=="bad_index")field->d_connectorIndices.setValue({9});
    if(mode=="duplicate_index")field->d_connectorIndices.setValue({1,1});
    if(mode=="bad_quaternion")x[1].getOrientation()=sofa::type::Quat<double>(1,0,0,1);
    if(mode=="outside_domain")x[1].getOrientation()=sofa::type::Quat<double>(0,std::sin(.01/2),0,std::cos(.01/2));
    if(mode=="null_mparams") {
        field->addDForce(nullptr,force,vel);
        return field->d_componentState.getValue()==sofa::core::objectmodel::ComponentState::Invalid?0:1;
    }
    if(mode=="high_k_energy") {
        field->d_stiffness.setValue(100.);
        const double theta=.0049,eps=1e-7;
        auto energy=[&](double angle) {
            x[1].getOrientation()=sofa::type::Quat<double>(0,std::sin(angle/2),0,std::cos(angle/2));
            x[3].getCenter()[0]=.001;pos.setValue(x);
            return field->getPotentialEnergy(nullptr,pos);
        };
        double fd=(energy(theta+eps)-energy(theta-eps))/(2*eps);energy(theta);
        field->addForce(nullptr,force,pos,vel);
        double error=std::abs(fd+force.getValue()[1][4]);
        std::cout<<"energy_gradient_error="<<error<<" threshold=1e-9\n";
        return error<1e-9 ? 0:1;
    }
    if(mode=="negative_stiffness"||mode=="zero_nodes"||mode=="bad_index"||mode=="duplicate_index"||mode=="bad_quaternion"||mode=="outside_domain") {
        pos.setValue(x);field->addForce(nullptr,force,pos,vel);
        return field->d_componentState.getValue()==sofa::core::objectmodel::ComponentState::Invalid?0:1;
    }
    return 2;
}
