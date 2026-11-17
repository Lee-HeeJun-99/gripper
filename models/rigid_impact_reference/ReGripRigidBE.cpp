/******************************************************************************
*                 SOFA, Simulation Open-Framework Architecture                *
*                    (c) 2006 INRIA, USTL, UJF, CNRS, MGH                     *
*                                                                             *
* This program is free software; you can redistribute it and/or modify it     *
* under the terms of the GNU Lesser General Public License as published by    *
* the Free Software Foundation; either version 2.1 of the License, or (at     *
* your option) any later version.                                             *
*                                                                             *
* This program is distributed in the hope that it will be useful, but WITHOUT *
* ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       *
* FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License *
* for more details.                                                           *
*                                                                             *
* You should have received a copy of the GNU Lesser General Public License    *
* along with this program. If not, see <http://www.gnu.org/licenses/>.        *
*******************************************************************************
* Authors: The SOFA Team and external contributors (see Authors.txt)          *
*                                                                             *
* Contact information: contact@sofa-framework.org                             *
******************************************************************************/
#include "ReGripRigidBE.h"
#include <sofa/core/ObjectFactory.h>
#include <chrono>
#include <fstream>
#include <iomanip>
#include <sofa/core/behavior/BaseMatrixLinearSystem.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/defaulttype/RigidTypes.h>
#include <sofa/core/behavior/BaseMass.h>
#include <sofa/core/behavior/BaseForceField.h>
#include <sofa/core/BaseMapping.h>
#include <sofa/linearalgebra/FullMatrix.h>
#include <sofa/linearalgebra/BaseMatrix.h>

namespace sofa::component::odesolver::backward
{
// Independent BE specialization. No original ReGripBDFSolver or SDK source
// is changed. Rotational force tangents are NOT generalized here: only an
// isotropic free rigid and zero-offset center mappings are supported.
static void requireOrientationIndependentRigid(core::objectmodel::BaseContext*context){
    using Rigid=core::behavior::MechanicalState<defaulttype::Rigid3Types>;
    using Vec=core::behavior::MechanicalState<defaulttype::Vec3Types>;
    auto bodies=context->getObjects<Rigid>(core::objectmodel::BaseContext::SearchDown);
    if(bodies.size()>1)throw std::runtime_error("mixed BE currently supports at most one free rigid body");
    for(auto*body:bodies){
        auto*mass=body->getContext()->getMass();if(!mass||mass->getClassName()!="UniformMass"||body->getSize()!=1)throw std::runtime_error("mixed BE rigid requires one actual UniformMass");
        linearalgebra::FullMatrix<double>M(6,6);M.clear();mass->getElementMass(0,&M);double m=M.element(0,0),I=M.element(3,3);
        if(!(m>0&&I>0))throw std::runtime_error("mixed BE positive rigid mass/inertia required");
        for(int i=0;i<6;++i)for(int j=0;j<6;++j)if(M.element(i,j)!=(i==j?(i<3?m:I):0))throw std::runtime_error("mixed BE anisotropic rigid inertia is NOT supported");
        for(auto*force:context->getObjects<core::behavior::BaseForceField>(core::objectmodel::BaseContext::SearchDown))if(force->getContext()->getMechanicalState()==body&&dynamic_cast<core::behavior::BaseMass*>(force)!=mass)throw std::runtime_error("mixed BE rigid orientation-dependent force scope rejected");
        for(auto*mapping:context->getObjects<core::BaseMapping>(core::objectmodel::BaseContext::SearchDown)){
            auto inputs=mapping->getMechFrom();if(std::find(inputs.begin(),inputs.end(),body)==inputs.end())continue;
            auto outputs=mapping->getMechTo();if(mapping->getClassName()!="RigidMapping"||outputs.size()!=1)throw std::runtime_error("mixed BE only center RigidMapping is certified");
            auto*point=dynamic_cast<Vec*>(outputs[0]);if(!point||point->getSize()!=1)throw std::runtime_error("mixed BE only one mapped rigid center is supported");
            auto p=point->read(core::vec_id::read_access::position)->getValue()[0];auto c=body->read(core::vec_id::read_access::position)->getValue()[0].getCenter();if((p-c).norm()>1e-12)throw std::runtime_error("mixed BE noncentral rigid mapping needs SO3 consistent tangent;rejected");
            for(auto*force:point->getContext()->getObjects<core::behavior::BaseForceField>(core::objectmodel::BaseContext::Local))throw std::runtime_error("mapped rigid center force field outside certified mixed BE scope");
        }
    }
}
struct RigidBEProfileScope {
    double*total;
    std::chrono::steady_clock::time_point start;
    explicit RigidBEProfileScope(double*p):total(p){if(total)start=std::chrono::steady_clock::now();}
    ~RigidBEProfileScope(){if(total)*total+=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();}
};

ReGripRigidBE::ReGripRigidBE()
    : d_order(initData(&d_order, static_cast<std::size_t>(1), "order", "Order of the numerical method"))
    , d_theta(initData(&d_theta, 1_sreal, "theta", "1=BDF1;0.5=trapezoidal;distinct integration experiments"))
    , d_profileFilename(initData(&d_profileFilename,std::string(),"profileFilename","Passive per-step stage timings;exclusive campaign path"))
    , d_tangentProbeFilename(initData(&d_tangentProbeFilename,std::string(),"tangentProbeFilename","Passive first-Newton mapped matrix/trial export for first two steps only"))
    , d_variableStep(initData(&d_variableStep,false,"variableStep","Explicit variable-step BDF2;fixed-step default preserved"))
    , d_nativeConstraintBE(initData(&d_nativeConstraintBE,true,"nativeConstraintBE","Opt-in backward-Euler-only compliance factors and actual-state free-motion initialization"))
    , d_nativeCoupledPredictor(initData(&d_nativeCoupledPredictor,false,"nativeCoupledPredictor","Experimental single Newton predictor ONLY;requires explicit coupled owner solving every accepted step"))
    , d_rayleighStiffness(initData(&d_rayleighStiffness, 0_sreal, "rayleighStiffness",
                                   "Rayleigh damping coefficient related to stiffness, > 0"))
    , d_rayleighMass(initData(&d_rayleighMass, 0_sreal, "rayleighMass",
                              "Rayleigh damping coefficient related to mass, > 0"))
    , l_newtonSolver(initLink("newtonSolver", "Link to a Newton-Raphson solver to solve the nonlinear equation produced by this numerical method"))
{
}

void ReGripRigidBE::init()
{
    if(d_order.getValue()!=1||d_theta.getValue()!=1||!d_nativeConstraintBE.getValue()||d_nativeCoupledPredictor.getValue()||d_variableStep.getValue()||d_rayleighStiffness.getValue()!=0)throw std::runtime_error("Rigid-compatible reconstructed BE only;BDF2/predictor/stiffness damping unsupported");

    OdeSolver::init();
    LinearSolverAccessor::init();

    if (!l_newtonSolver.get())
    {
        l_newtonSolver.set(getContext()->get<NewtonRaphsonSolver>(
            getContext()->getTags(), core::objectmodel::BaseContext::SearchDown));

        if (!l_newtonSolver)
        {
            msg_error()
                << "A Newton-Raphson solver is required by this component but has not been found.";
            this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
        }
    }

    if (auto* context = this->getContext())
    {
        m_timeList.push_back(context->getTime());
    }

    if (this->d_componentState.getValue() != core::objectmodel::ComponentState::Invalid)
    {
        d_componentState.setValue(core::objectmodel::ComponentState::Valid);
    }
}

void ReGripRigidBE::reset()
{
    while (!m_timeList.empty())
    {
        m_timeList.pop_front();
    }
    if (auto* context = this->getContext())
    {
        m_timeList.push_back(context->getTime());
    }

    m_currentSolve = 0;
}

/**
 * Represent the mathematical function to be solved by a Newton-Raphson solver. See documentation of
 * @BaseNonLinearFunction
 *
 * The function is r(x) = [r1(x), r2(x)] with
 * x = [position, velocity]
 * r_1(x) = \sum_{j=0}^s a_j \text{position}_j - h \sum_{j=0}^s b_j \text{velocity}_j
 * r_2(x) = \sum_{j=0}^s a_j M \text{velocity}_j - h \sum_{j=0}^s b_j \text{force}_j
 */
struct RigidBEResidualFunction : newton_raphson::BaseNonLinearFunction
{
    double*profile=nullptr;
    std::string tangentProbeFilename;
    unsigned residualEvaluations=0,gradientEvaluations=0,linearSolves=0,trialUpdates=0,newtonIterations=0;
    void startNewtonIteration() override {++newtonIterations;}
    void evaluateCurrentGuess() override
    {
        ++residualEvaluations;
        RigidBEProfileScope residualTimer(profile?profile+0:nullptr);
        {
            RigidBEProfileScope forceTimer(profile?profile+1:nullptr);
            SCOPED_TIMER("ComputeForce");
            static constexpr bool clearForcesBeforeComputingThem = true;
            static constexpr bool applyBottomUpMappings = true;

            mop.mparams.setX(position[order]);
            mop.mparams.setV(velocity[order]);
            mop.computeForce(force[order], clearForcesBeforeComputingThem, applyBottomUpMappings);

            //Rayleigh damping
            core::behavior::MultiVecDeriv damping(&vop);
            mop.addMBKv(damping,
                core::MatricesFactors::M(-rayleighMass),
                core::MatricesFactors::B(0),
                core::MatricesFactors::K(rayleighStiffness),true,true);
            core::behavior::MultiVecDeriv currentForce(&vop,force[order]);
            currentForce.peq(damping);

            mop.projectResponse(force[order]);
        }

        core::behavior::MultiVecDeriv r1Vec(&vop, r1);
        core::behavior::MultiVecDeriv r2Vec(&vop, r2);

        r1Vec.clear();
        r2Vec.clear();

        // r1 is identically satisfied: every trial reconstructs q_n (+) h*v.
        // Never add Rigid3 coordinates (7 scalars) to derivatives (6 scalars).

        core::behavior::MultiVecDeriv velocitySum(&vop);
        for (unsigned int i = 0; i < order + 1; ++i)
        {
            if (a_coef[i] != 0)
            {
                velocitySum.peq(velocity[i], a_coef[i]);
            }
        }
        // addMdx prunes mechanical mappings in this SDK. Propagate and use a
        // cleared MBK product so mapped mass contributes J^T M J exactly once.
        {
            RigidBEProfileScope massTimer(profile?profile+2:nullptr);
            mop.propagateDxAndResetDf(velocitySum,r2);
            mop.addMBKdx(r2,core::MatricesFactors::M(1),core::MatricesFactors::B(0),core::MatricesFactors::K(0),false,true);
        }

        for (unsigned int i = 0; i < order + 1; ++i)
        {
            if (b_coef[i] != 0)
            {
                r2Vec.peq(force[i], -dt * b_coef[i]);
            }
        }

        mop.projectResponse(r1);
        mop.projectResponse(r2);
    }

    SReal squaredNormLastEvaluation() override
    {
        core::behavior::MultiVecDeriv r2Vec(&vop, r2);
        return r2Vec.dot(r2Vec);
    }

    void computeGradientFromCurrentGuess() override
    {
        ++gradientEvaluations;
        RigidBEProfileScope gradientTimer(profile?profile+3:nullptr);
        const core::MatricesFactors::M m(a_coef[order] + dt * b_coef[order] * rayleighMass);
        const core::MatricesFactors::B b(-dt * b_coef[order]);
        const core::MatricesFactors::K k(-dt * b_coef[order] * (rayleighStiffness + dt * b_coef[order] / a_coef[order]));

        mop.setSystemMBKMatrix(m, b, k, linearSolver);
        if(!tangentProbeFilename.empty()&&gradientEvaluations==1){
            auto*system=linearSolver->getLinearSystem();auto*matrix=system->getSystemBaseMatrix();
            auto*state=dynamic_cast<core::behavior::MechanicalState<defaulttype::Vec3Types>*>(mop.ctx->getMechanicalState());
            if(!matrix||!state)throw std::runtime_error("Vec3 tangent probe unavailable");
            std::ifstream previous(tangentProbeFilename+".matrix.csv");if(previous)throw std::runtime_error("tangent probe already exists");
            std::ofstream out(tangentProbeFilename+".matrix.csv");out<<std::setprecision(17)<<"row,col,value\n";
            for(int i=0;i<matrix->rowSize();++i)for(int j=0;j<matrix->colSize();++j)if(matrix->element(i,j))out<<i<<','<<j<<','<<matrix->element(i,j)<<'\n';
            std::ofstream positionOut(tangentProbeFilename+".state.csv");positionOut<<std::setprecision(17)<<"dt,a2,mfactor,kfactor\n"<<dt<<','<<a_coef[order]<<','<<m.get()<<','<<k.get()<<"\nx,y,z\n";
            for(const auto&q:mop.mparams.readX(state)->getValue())positionOut<<q[0]<<','<<q[1]<<','<<q[2]<<'\n';
        }

        core::behavior::MultiVecDeriv rhsVec(&vop, rhs);
        rhsVec.eq(r2, -1);

        // No kinematic residual correction: r1 is identically zero.

        mop.projectResponse(rhs);
    }

    void updateGuessFromLinearSolution(SReal alpha) override
    {
        ++trialUpdates;
        RigidBEProfileScope updateTimer(profile?profile+5:nullptr);
        vop.v_peq(velocity[order], dv, alpha);
        vop.v_eq(position[order],position[order-1]);
        vop.v_peq(position[order],velocity[order],dt);

        mop.projectPositionAndVelocity(position[order], velocity[order]);
        mop.propagateXAndV(position[order], velocity[order]);
    }

    void solveLinearEquation() override
    {
        ++linearSolves;
        RigidBEProfileScope solveTimer(profile?profile+4:nullptr);
        vop.v_clear(dv);

        linearSolver->getLinearSystem()->setSystemSolution(dv);
        linearSolver->getLinearSystem()->setRHS(rhs);
        linearSolver->solveSystem();
        linearSolver->getLinearSystem()->dispatchSystemSolution(dv);
    }

    void computeDxFromDv(SReal alpha)
    {
        core::behavior::MultiVecDeriv dxVec(&vop, dx);
        dxVec.eq(dv, alpha * dt * b_coef[order] / a_coef[order]);
        dxVec.peq(r1, - 1 / a_coef[order]);
    }

    SReal squaredNormDx() override
    {
        core::behavior::MultiVecDeriv dvVec(&vop, dv);
        return dvVec.dot(dvVec);
    }

    SReal squaredLastEvaluation() override
    {
        core::behavior::MultiVecDeriv v(&vop, velocity[order]);
        return v.dot(v);
    }

    std::size_t order = 1;
    sofa::type::vector<SReal> a_coef;
    sofa::type::vector<SReal> b_coef;
    SReal dt = 0;
    SReal rayleighStiffness = 0;
    SReal rayleighMass = 0;
    sofa::simulation::common::MechanicalOperations& mop;
    simulation::common::VectorOperations& vop;
    sofa::type::vector<core::MultiVecCoordId> position;
    sofa::type::vector<core::MultiVecDerivId> velocity;
    sofa::type::vector<core::MultiVecDerivId> force;
    core::MultiVecDerivId r1;
    core::MultiVecDerivId r2;
    core::MultiVecDerivId dx;
    core::MultiVecDerivId dv;
    core::MultiVecDerivId rhs;
    core::behavior::LinearSolver* linearSolver { nullptr };

    RigidBEResidualFunction(sofa::simulation::common::MechanicalOperations& mop,
                     simulation::common::VectorOperations& vop)
        : mop(mop), vop(vop)
    {
    }
};

void ReGripRigidBE::solve(
    const core::ExecParams* params, SReal dt,
    core::MultiVecCoordId xResult,
    core::MultiVecDerivId vResult)
{
    if(d_order.getValue()!=1||d_theta.getValue()!=1||!d_nativeConstraintBE.getValue()||d_nativeCoupledPredictor.getValue()||d_variableStep.getValue()||d_rayleighStiffness.getValue()!=0)throw std::runtime_error("Rigid-compatible reconstructed BE only;BDF2/predictor/stiffness damping unsupported");

    if (!isComponentStateValid())
    {
        return;
    }
    requireOrientationIndependentRigid(getContext());

    /**
     * High-order methods requires an amount of previous time steps. At the begining of the simulation,
     * those time steps are not yet computed. Therefore, the order is reduced to the appropriate order.
     */
    const auto order = std::max(std::min(d_order.getValue(), m_currentSolve + 1), static_cast<std::size_t>(1));

    /**
     * Save the time into a list of size order
     */
    if (auto* context = this->getContext())
    {
        m_timeList.push_back(context->getTime() + dt);
        while (m_timeList.size() > order + 1)
        {
            m_timeList.pop_front();
        }
    }

    recomputeCoefficients(order, dt);


    // Create the vector and mechanical operations tools. These are used to execute special
    // operations (multiplication, additions, etc.) on multi-vectors (a vector that is stored
    // in different buffers inside the mechanical objects)
    sofa::simulation::common::VectorOperations vop(params, this->getContext());
    sofa::simulation::common::MechanicalOperations mop(params, this->getContext());
    mop->setImplicit(true);

    {
        core::behavior::MultiVecDeriv dx(&vop, sofa::core::vec_id::write_access::dx);
        dx.realloc(&vop, false, true);
    }

    m_position.resize(order + 1);
    m_velocity.resize(order + 1);
    m_force.resize(order + 1);

    for (unsigned int i = 0; i < order + 1; ++i)
    {
            realloc(vop, m_position[i], "x+" + std::to_string(i));
            realloc(vop, m_velocity[i], "v+" + std::to_string(i));
            realloc(vop, m_force[i], "f+" + std::to_string(i));
    }
    realloc(vop,m_previousPosition,"previous_position");
    realloc(vop,m_previousVelocity,"previous_velocity");
    // Keep owned history buffers: never alias both n and n-1 to main state.
    if(d_nativeConstraintBE.getValue()){
        requireNativeBE();
        // FreeMotion's output vectors can still contain the preceding FREE
        // state. Initialize from actual constraint-corrected main x/v, as the
        // SDK EulerImplicitSolver does;never use stale free motion as history.
        vop.v_eq(m_position[order-1],sofa::core::vec_id::read_access::position);
        vop.v_eq(m_velocity[order-1],sofa::core::vec_id::read_access::velocity);
    }else{
        vop.v_eq(m_position[order-1],xResult);
        vop.v_eq(m_velocity[order-1],vResult);
    }
    vop.v_eq(m_force[order-1],sofa::core::vec_id::read_access::force);
    if(order==2){vop.v_eq(m_position[0],m_previousPosition);vop.v_eq(m_velocity[0],m_previousVelocity);}

    realloc(vop, m_r1, "r1");
    realloc(vop, m_r2, "r2");
    realloc(vop, m_rhs, "rhs");
    realloc(vop, m_dv, "dv");

    //initial guess
    vop.v_eq(m_position[order], m_position[order - 1]);
    vop.v_eq(m_velocity[order], m_velocity[order - 1]);

    //prediction using the previous velocity
    vop.v_peq(m_position[order], m_velocity[order], dt);
    if(order==2){
        vop.v_eq(m_position[2],m_position[1],-m_a_coef[1]/m_a_coef[2]);
        vop.v_peq(m_position[2],m_position[0],-m_a_coef[0]/m_a_coef[2]);
        vop.v_peq(m_position[2],m_velocity[2],dt/m_a_coef[2]);
    }

    mop.propagateX(m_position[order]);
    mop.propagateV(m_velocity[order]);

    RigidBEResidualFunction residualFunction(mop, vop);
    if(!d_tangentProbeFilename.getValue().empty()&&m_currentSolve<2)residualFunction.tangentProbeFilename=d_tangentProbeFilename.getValue()+"."+std::to_string(m_currentSolve);
    double profile[6]{};
    if(!d_profileFilename.getValue().empty())residualFunction.profile=profile;
    residualFunction.order = order;
    residualFunction.a_coef = m_a_coef;
    residualFunction.b_coef = m_b_coef;
    residualFunction.dt = dt;
    residualFunction.rayleighMass = d_rayleighMass.getValue();
    residualFunction.rayleighStiffness = d_rayleighStiffness.getValue();
    residualFunction.position = m_position;
    residualFunction.velocity = m_velocity;
    residualFunction.force = m_force;
    residualFunction.r1 = m_r1;
    residualFunction.r2 = m_r2;
    residualFunction.dx = sofa::core::vec_id::write_access::dx;
    residualFunction.dv = m_dv;
    residualFunction.rhs = m_rhs;
    residualFunction.linearSolver = l_linearSolver.get();

    if(d_nativeCoupledPredictor.getValue()){
        requireNativeBE();
        auto*owner=getContext()->get<sofa::core::objectmodel::BaseObject>(std::string("coupled"));
        auto*complete=owner?dynamic_cast<Data<bool>*>(owner->findData("completeFreeStage")):nullptr;
        if(!owner||owner->getClassName()!="FilmNativeCoupledCorrection"||!complete||!complete->getValue())throw std::runtime_error("predictor-only mode requires coupled.completeFreeStage=1;no unconverged accepted publication");
        // This is explicitly NOT a converged free solution. The accepted
        // constrained/non-contact solution must be computed by the linked
        // owner at end-step, BEFORE recorders or the next physical step.
        residualFunction.startNewtonIteration();
        residualFunction.evaluateCurrentGuess();
        residualFunction.computeGradientFromCurrentGuess();
        residualFunction.solveLinearEquation();
        residualFunction.updateGuessFromLinearSolution(1);
        residualFunction.evaluateCurrentGuess();
        residualFunction.computeGradientFromCurrentGuess();
        if(!m_currentSolve)msg_info()<<"Single Newton collision predictor only;accepted nonlinear coupled solve is mandatory on EVERY step";
    }else l_newtonSolver->solve(residualFunction);
    if(d_nativeConstraintBE.getValue()&&!d_nativeCoupledPredictor.getValue()){
        const auto status=static_cast<std::size_t>(l_newtonSolver->d_status.getValue());
        if(status==0||status==1||status==3||status==4)throw std::runtime_error("Native BE free-motion Newton solve failed;no constraint correction or state publication is allowed");
        // Constraint compliance must use the converged FREE-state tangent,
        // not the matrix from the preceding Newton correction. Pure query.
        residualFunction.computeGradientFromCurrentGuess();
    }
    if(residualFunction.profile){
        const auto&path=d_profileFilename.getValue();
        if(!m_currentSolve){std::ifstream previous(path);if(previous)throw std::runtime_error("profile already exists");}
        std::ofstream output(path,std::ios::app);
        if(!m_currentSolve)output<<"time,residual_s,force_damping_s,mass_product_s,gradient_rhs_s,linear_s,update_mapping_s,residual_evaluations,gradient_evaluations,linear_solves,newton_iterations,trial_updates,extra_line_search_trials,momentum_residual_norm\n";
        output<<std::setprecision(17)<<getContext()->getTime()+dt;
        for(double value:profile)output<<','<<value;
        // A successful Newton iteration has one accepted line-search trial;
        // extras are rejected trials only when the runtime reports no failure.
        output<<','<<residualFunction.residualEvaluations<<','<<residualFunction.gradientEvaluations
              <<','<<residualFunction.linearSolves<<','<<residualFunction.newtonIterations
              <<','<<residualFunction.trialUpdates<<','<<(residualFunction.trialUpdates-residualFunction.newtonIterations)
              <<','<<std::sqrt(residualFunction.squaredNormLastEvaluation())<<'\n';
    }

    // Save n before publishing n+1. History remains distinct from main state.
    vop.v_eq(m_previousPosition,m_position[order-1]);
    vop.v_eq(m_previousVelocity,m_velocity[order-1]);
    vop.v_eq(xResult,m_position[order]);
    vop.v_eq(vResult,m_velocity[order]);
    vop.v_eq(sofa::core::vec_id::write_access::force,m_force[order]);

    ++m_currentSolve;
}

}

namespace sofa::component::odesolver::backward {
void registerReGripRigidBE(sofa::core::ObjectFactory* factory) { factory->registerObjects(sofa::core::ObjectRegistrationData("Independent reconstructed R3/SO3 backward Euler;orientation-independent rigid mechanics only;NOT general rigid BDF2").add<ReGripRigidBE>()); }
}
