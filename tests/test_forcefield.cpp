// Execute the actual implementation, rather than a Python copy of its formula.
#include "../plugin/src/TangentialRigidForceField.cpp"
#include <sofa/component/statecontainer/MechanicalObject.h>
#include <random>
#include <iostream>
#include <stdexcept>

using FF=tangential_v110::TangentialRigidForceField;
struct Accumulator : sofa::core::behavior::StiffnessMatrixAccumulator {
    double a[132][132]{};
    void add(sofa::SignedIndex r,sofa::SignedIndex c,double v) override { a[r][c]+=v; }
    void add(sofa::SignedIndex r,sofa::SignedIndex c,float v) override { add(r,c,double(v)); }
};
void check(bool ok,const char* why) { if(!ok) throw std::runtime_error(why); }

int main() {
 try {
    auto state=sofa::core::objectmodel::New<sofa::component::statecontainer::MechanicalObject<tangential_v110::Types>>();
    state->resize(4);
    auto ff=sofa::core::objectmodel::New<FF>(state.get());
    ff->d_nodesPerLayer.setValue(2);
    check(ff->getMState()==state.get(),"mstate binding failed");
    check(state->getSize()==4,"state resize failed");
    ff->d_stiffness.setValue(.1);
    Accumulator acc;
    sofa::core::behavior::StiffnessMatrix matrix;
    matrix.setMatrixAccumulator(&acc,state.get());
    ff->buildStiffnessMatrix(&matrix);
    unsigned ids[4]={6,10,18,22};
    double b[4]={-1,-.2,1,-.2};
    for(int r=0;r<24;++r) for(int c=0;c<24;++c) {
        double expected=0;
        for(int i=0;i<4;++i) for(int j=0;j<4;++j)
            if(r==int(ids[i]) && c==int(ids[j])) expected=-.1*b[i]*b[j];
        check(std::abs(acc.a[r][c]-expected)<1e-15,"assembled matrix/DOF mismatch");
    }
    std::mt19937 rng(11);std::uniform_real_distribution<double> dist(-.0049,.0049);
    double maxEnergyError=0,maxTangentError=0;
    auto position=[](const double q[4]) {
        FF::VecCoord x(4);
        for(auto& p:x) p.getOrientation()=sofa::type::Quat<double>(0,0,0,1);
        x[1].getCenter()[0]=q[0];x[3].getCenter()[0]=q[2];
        x[1].getOrientation()=sofa::type::Quat<double>(0,std::sin(q[1]/2),0,std::cos(q[1]/2));
        x[3].getOrientation()=sofa::type::Quat<double>(0,std::sin(q[3]/2),0,std::cos(q[3]/2));
        return x;
    };
    auto forces=[&](const double q[4]) {
        FF::DataVecCoord x; x.setValue(position(q));
        FF::DataVecDeriv force,velocity;
        force.setValue(FF::VecDeriv(4)); velocity.setValue(FF::VecDeriv(4));
        ff->addForce(nullptr,force,x,velocity);
        return force.getValue();
    };
    auto energy=[&](const double q[4]) {
        FF::DataVecCoord x;x.setValue(position(q));return ff->getPotentialEnergy(nullptr,x);
    };
    for(int trial=0;trial<100;++trial) {
        double q[4]; for(double& v:q)v=dist(rng);
        auto force=forces(q);
        check(std::abs(force[1][0]+force[3][0])<1e-15,"pair forces do not cancel");
        for(int node=0;node<4;++node) for(int axis:{1,2,3,5})
            check(force[node][axis]==0,"unexpected normal force/torque");
        for(int j=0;j<4;++j) {
            double qp[4],qm[4];std::copy(q,q+4,qp);std::copy(q,q+4,qm);
            qp[j]+=1e-7;qm[j]-=1e-7;
            const double grad=(energy(qp)-energy(qm))/2e-7;
            const double value=force[ids[j]/6][ids[j]%6];
            maxEnergyError=std::max(maxEnergyError,std::abs(value+grad));
            check(std::abs(value+grad)<1e-9,"energy gradient exceeds small-angle error budget");
            auto fp=forces(qp),fm=forces(qm);
            for(int i=0;i<4;++i) {
                double fd=(fp[ids[i]/6][ids[i]%6]-fm[ids[i]/6][ids[i]%6])/2e-7;
                maxTangentError=std::max(maxTangentError,std::abs(fd-acc.a[ids[i]][ids[j]]));
                check(std::abs(fd-acc.a[ids[i]][ids[j]])<1e-7,"SOFA rotation tangent mismatch");
            }
        }
        FF::VecDeriv u(4);for(auto& d:u)for(int i=0;i<6;++i)d[i]=dist(rng);
        for(double factor:{0.,2.5,-.25}) {
            FF::DataVecDeriv dx,df;dx.setValue(u);df.setValue(FF::VecDeriv(4));
            sofa::core::MechanicalParams mp;mp.setKFactor(factor);
            ff->addDForce(&mp,df,dx);
            double quadratic=0;
            for(int r=0;r<24;++r) {
                double expected=0;for(int c=0;c<24;++c)expected+=acc.a[r][c]*u[c/6][c%6];
                check(std::abs(df.getValue()[r/6][r%6]-factor*expected)<1e-14,"addDForce/kFactor mismatch");
                quadratic+=u[r/6][r%6]*expected;
            }
            check(quadratic<1e-15,"negative energy stiffness");
        }
    }
    // Positive X slip must restore X and generate positive y moments.
    double q[4]={0,0,.001,0};auto f=forces(q);
    check(f[1][0]>0 && f[3][0]<0 && f[1][4]>0 && f[3][4]>0,"restoring force or torque sign");
    state->resize(6);ff->d_nodesPerLayer.setValue(3);
    ff->d_connectorIndices.setValue({2});
    FF::VecCoord chosen(6);
    for(auto& p:chosen)p.getOrientation()=sofa::type::Quat<double>(0,0,0,1);
    chosen[4].getCenter()[0]=.001;chosen[5].getCenter()[0]=.002;
    FF::DataVecCoord selectedX;selectedX.setValue(chosen);
    FF::DataVecDeriv selectedF,selectedV;
    selectedF.setValue(FF::VecDeriv(6));selectedV.setValue(FF::VecDeriv(6));
    ff->addForce(nullptr,selectedF,selectedX,selectedV);
    check(selectedF.getValue()[1][0]==0 && selectedF.getValue()[4][0]==0,"unselected pair receives force");
    check(std::abs(selectedF.getValue()[2][0]-.0002)<1e-15,"selected pair force mismatch");
    Accumulator subset;sofa::core::behavior::StiffnessMatrix subsetMatrix;
    subsetMatrix.setMatrixAccumulator(&subset,state.get());ff->buildStiffnessMatrix(&subsetMatrix);
    check(subset.a[6][6]==0 && std::abs(subset.a[12][12]+.1)<1e-15,"connector subset matrix mismatch");
    std::cout<<"PASS actual addForce/addDForce/buildStiffnessMatrix, 100 random small-angle checks; "
             <<"max energy-gradient error="<<maxEnergyError<<", max tangent error="<<maxTangentError<<"\n";
    return 0;
 } catch(const std::exception& e) { std::cerr<<"FAIL "<<e.what()<<"\n";return 1; }
}
