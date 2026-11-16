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
#include "ReGripBDFSolver.h"
#include <sofa/core/ObjectFactory.h>

namespace sofa::component::odesolver::backward
{

ReGripBDFSolver::ReGripBDFSolver()
    : d_order(initData(&d_order, static_cast<std::size_t>(1), "order", "Order of the numerical method"))
    , d_theta(initData(&d_theta, 1_sreal, "theta", "1=BDF1;0.5=trapezoidal;distinct integration experiments"))
    , d_rayleighStiffness(initData(&d_rayleighStiffness, 0_sreal, "rayleighStiffness",
                                   "Rayleigh damping coefficient related to stiffness, > 0"))
    , d_rayleighMass(initData(&d_rayleighMass, 0_sreal, "rayleighMass",
                              "Rayleigh damping coefficient related to mass, > 0"))
    , l_newtonSolver(initLink("newtonSolver", "Link to a Newton-Raphson solver to solve the nonlinear equation produced by this numerical method"))
{
}

void ReGripBDFSolver::init()
{
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

void ReGripBDFSolver::reset()
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
struct ReGripResidualFunction : newton_raphson::BaseNonLinearFunction
{
    void evaluateCurrentGuess() override
    {
        {
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

        for (unsigned int i = 0; i < order + 1; ++i)
        {
            if (a_coef[i] != 0)
            {
                r1Vec.peq(position[i], a_coef[i]);
            }
        }
        for (unsigned int i = 0; i < order + 1; ++i)
        {
            if (b_coef[i] != 0)
            {
                r1Vec.peq(velocity[i], -dt * b_coef[i]);
            }
        }

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
        mop.propagateDxAndResetDf(velocitySum,r2);
        mop.addMBKdx(r2,core::MatricesFactors::M(1),core::MatricesFactors::B(0),core::MatricesFactors::K(0),false,true);

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
        const core::MatricesFactors::M m(a_coef[order] + dt * b_coef[order] * rayleighMass);
        const core::MatricesFactors::B b(-dt * b_coef[order]);
        const core::MatricesFactors::K k(-dt * b_coef[order] * (rayleighStiffness + dt * b_coef[order] / a_coef[order]));

        mop.setSystemMBKMatrix(m, b, k, linearSolver);

        core::behavior::MultiVecDeriv rhsVec(&vop, rhs);
        rhsVec.eq(r2, -1);

        // rhs += -dt * (bs /as) * K * r1
        {
            const auto vBackup = mop.mparams.v();
            mop.mparams.setV(r1);
            mop.propagateDx(r1);
            core::behavior::MultiVecDeriv correction(&vop);
            mop.addMBKv(correction, core::MatricesFactors::M(0), core::MatricesFactors::B(0),
                core::MatricesFactors::K(-dt * b_coef[order] / a_coef[order]),true,true);
            rhsVec.peq(correction);
            mop.mparams.setV(vBackup);
        }

        mop.projectResponse(rhs);
    }

    void updateGuessFromLinearSolution(SReal alpha) override
    {
        vop.v_peq(velocity[order], dv, alpha);
        computeDxFromDv(alpha);
        vop.v_peq(position[order], dx);

        mop.projectPositionAndVelocity(position[order], velocity[order]);
        mop.propagateXAndV(position[order], velocity[order]);
    }

    void solveLinearEquation() override
    {
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

    ReGripResidualFunction(sofa::simulation::common::MechanicalOperations& mop,
                     simulation::common::VectorOperations& vop)
        : mop(mop), vop(vop)
    {
    }
};

void ReGripBDFSolver::solve(
    const core::ExecParams* params, SReal dt,
    core::MultiVecCoordId xResult,
    core::MultiVecDerivId vResult)
{
    if (!isComponentStateValid())
    {
        return;
    }

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
    vop.v_eq(m_position[order-1],xResult);
    vop.v_eq(m_velocity[order-1],vResult);
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
        vop.v_eq(m_position[2],m_position[1],2/1.5);
        vop.v_peq(m_position[2],m_position[0],-.5/1.5);
        vop.v_peq(m_position[2],m_velocity[2],dt/1.5);
    }

    mop.propagateX(m_position[order]);
    mop.propagateV(m_velocity[order]);

    ReGripResidualFunction residualFunction(mop, vop);
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

    l_newtonSolver->solve(residualFunction);

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
void registerReGripBDFSolver(sofa::core::ObjectFactory* factory) { factory->registerObjects(sofa::core::ObjectRegistrationData("Independent BDF1/fixed-step BDF2 or trapezoidal with consistent line search and mapped residuals; adapted from SOFA LGPL source").add<ReGripBDFSolver>()); }
}
