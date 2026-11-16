#include "ExactInterval.h"
#include "NormalizedSnapshot.h"
#include "VectorField.h"
#include <fstream>
#include <iomanip>
#include <memory>
#include <optional>
#include <sofa/core/MechanicalParams.h>
#include <sofa/core/ObjectFactory.h>
#include <sofa/core/behavior/BaseLocalForceFieldMatrix.h>
#include <sofa/core/behavior/ForceField.h>
#include <sofa/defaulttype/VecTypes.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/simulation/AnimateEndEvent.h>

// FIXED-PATCH ISOLATION BENCHMARK,not a 3D collision/grasp replacement.
// One Vec3 material displacement couples to an externally supported planar
// interface. Fixed normal z,capacity C(1-x*x),uniform displacement over x.
// No normal compliance,birth/death,rotations or hidden position correction.
class VectorPatchBenchmark final
    : public sofa::core::behavior::ForceField<sofa::defaulttype::Vec3Types> {
public:
  using Types = sofa::defaulttype::Vec3Types;
  using Base = sofa::core::behavior::ForceField<Types>;
  SOFA_CLASS(VectorPatchBenchmark, Base);
  sofa::core::objectmodel::Data<double> halfLength, stiffness, capacity;
  sofa::core::objectmodel::Data<bool> velocityDirectedTangent;
  sofa::core::objectmodel::Data<unsigned> compressionEvery;
  sofa::core::objectmodel::Data<bool> normalizedRepresentation;
  sofa::core::objectmodel::Data<bool> outwardCertificates;
  sofa::core::objectmodel::Data<double> snapshotTolerance;
  sofa::core::objectmodel::Data<std::string> filename;
  std::unique_ptr<regrip_vector_history::VectorField> field;
  std::array<double, 3> frozen{}, previous{};
  std::ofstream journal;
  unsigned begins = 0, ends = 0;
  long double cumulativeLoss = 0;
  unsigned commits = 0, frozenCompression = 0;
  double frozenTolerance = 0;
  mutable std::optional<regrip_vector_history::VectorField::Trial> cached;
  mutable std::array<double, 3> cachedX{};
  mutable std::size_t cachedEpoch = 0;
  mutable std::array<double, 3> cachedV{};
  bool frozenDirected = false;
  bool frozenNormalized = false;
  bool frozenOutward = false;
  std::array<double, 3> beginX{}, beginV{};
  std::array<long double, 17> beginMeasures{};
  explicit VectorPatchBenchmark(
      sofa::core::behavior::MechanicalState<Types> *s = nullptr)
      : Base(s), halfLength(initData(&halfLength, .3192, "halfLength",
                                     "Fixed material patch half length mm")),
        stiffness(initData(&stiffness, .001, "stiffness",
                           "Tangential line stiffness F/mm2")),
        capacity(initData(&capacity, 3e-6, "capacity",
                          "Prescribed peak Coulomb capacity F/mm")),
        velocityDirectedTangent(initData(&velocityDirectedTangent, false,
                                         "velocityDirectedTangent",
                                         "Explicit velocity-sided generalized "
                                         "derivative at positive yield")),
        compressionEvery(initData(
            &compressionEvery, 0u, "compressionEvery",
            "Experimental fixed-patch compression period;zero disables")),
        normalizedRepresentation(initData(
            &normalizedRepresentation, false, "normalizedRepresentation",
            "Independent gap/direction representation;requires compression")),
        outwardCertificates(
            initData(&outwardCertificates, false, "outwardCertificates",
                     "Optional outward interval prefilter;exact rational "
                     "fallback unchanged")),
        snapshotTolerance(
            initData(&snapshotTolerance, 1e-9, "snapshotTolerance",
                     "Numerical state-fit target mm;not a physical parameter")),
        filename(initData(&filename, std::string(""), "filename",
                          "Exclusive reference Commit journal")) {
    if (s)
      mstate.set(s);
    f_listening.setValue(true);
  }
  std::array<double, 3> parameters() const {
    return {halfLength.getValue(), stiffness.getValue(), capacity.getValue()};
  }
  void prepare(const VecCoord &x) {
    if (x.size() != 1)
      throw std::invalid_argument(
          "fixed-patch reference requires one Vec3 displacement");
    frozen = parameters();
    field = std::make_unique<regrip_vector_history::VectorField>(frozen[0],
                                                                 frozen[1]);
    frozenDirected = velocityDirectedTangent.getValue();
    frozenNormalized = normalizedRepresentation.getValue();
    frozenOutward = outwardCertificates.getValue();
    frozenCompression = compressionEvery.getValue();
    frozenTolerance = snapshotTolerance.getValue();
    commits = 0;
    if (frozenCompression > 1024 || !std::isfinite(frozenTolerance) ||
        frozenTolerance <= 0)
      throw std::invalid_argument("snapshot controls");
    if (frozenNormalized && !frozenCompression)
      throw std::invalid_argument(
          "normalized representation requires explicit compression period");
    if (frozenOutward && !frozenNormalized)
      throw std::invalid_argument(
          "outward prefilter requires normalized representation");
    cached.reset();
    regrip_vector_history::radialReturn({}, {}, {0, 0, 1}, frozen[1],
                                        frozen[2]);
    for (int j = 0; j < 3; ++j) {
      if (!std::isfinite(x[0][j]))
        throw std::invalid_argument("patch reference position");
      previous[j] = x[0][j];
    }
  }
  void init() override {
    Base::init();
    if (!mstate)
      throw std::runtime_error("patch reference missing state");
    prepare(
        mstate->read(sofa::core::vec_id::read_access::position)->getValue());
    if (filename.getValue().empty() ||
        std::ifstream(filename.getValue()).good())
      throw std::runtime_error("refuse empty/existing patch journal");
    journal.open(filename.getValue());
    if (!journal)
      throw std::runtime_error("patch journal open");
    journal << std::setprecision(18)
            << "time,commit,x,y,fx,fy,old_energy,energy,loss,cumulative_loss,"
               "endpoint_projection,endpoint_work,energy_residual,evaluations,"
               "nonunique_samples,z,vx,vy,vz,begin_x,begin_y,begin_z,begin_vx,"
               "begin_vy,begin_vz,begin_fx,begin_fy,begin_fz";
    for (int i = 0; i < 9; ++i)
      journal << ",begin_J" << i;
    journal
        << ",stored_energy_post,representation_delta_16,representation_"
           "quadrature_difference,post_inventory_difference,snapshot_cells\n";
  }
  regrip_vector_history::VectorField::Trial
  uncachedTrial(const VecCoord &x) const {
    if (!field || parameters() != frozen || x.size() != 1)
      throw std::invalid_argument(
          "patch reference changed topology/parameters");
    for (int j = 0; j < 3; ++j)
      if (!std::isfinite(x[0][j]))
        throw std::invalid_argument("patch reference nonfinite position");
    // z is a normal-free DOF,not a hidden projective constraint. It is simply
    // excluded from a prescribed tangential-only benchmark's spring work.
    regrip_vector_history::Step step;
    step.capacity = frozen[2];
    step.increment[0] = {x[0][0] - previous[0], x[0][1] - previous[1], 0};
    regrip_vector_history::V direction{};
    if (frozenDirected) {
      const auto &v =
          mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
      direction = {v[0][0], v[0][1], 0};
    }
    return field->evaluate(step, 1e-7L, 1e-30L, 100000, direction);
  }
  regrip_vector_history::VectorField::Trial trial(const VecCoord &x) const {
    if (!field || parameters() != frozen || x.size() != 1 ||
        velocityDirectedTangent.getValue() != frozenDirected ||
        normalizedRepresentation.getValue() != frozenNormalized ||
        outwardCertificates.getValue() != frozenOutward ||
        compressionEvery.getValue() != frozenCompression ||
        snapshotTolerance.getValue() != frozenTolerance)
      throw std::invalid_argument("patch cache scope changed");
    std::array<double, 3> position{x[0][0], x[0][1], x[0][2]};
    std::array<double, 3> velocity{};
    if (frozenDirected) {
      const auto &v =
          mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
      for (int j = 0; j < 3; ++j)
        velocity[j] = v[0][j];
    }
    if (cached && cachedEpoch == field->epoch() && cachedX == position &&
        cachedV == velocity)
      return *cached;
    auto t = uncachedTrial(x);
    cached = t;
    cachedEpoch = field->epoch();
    cachedX = position;
    cachedV = velocity;
    return t;
  }
  void commit(const VecCoord &x) {
    auto t = trial(x);
    const auto &v = t.integral.v;
    field->commit(t);
    cumulativeLoss += v[2];
    cached.reset();
    for (int j = 0; j < 3; ++j)
      previous[j] = x[0][j];
    ++commits;
    long double stored = v[1], rep16 = 0, repDifference = 0;
    std::size_t cells = 0;
    if (frozenCompression && commits % frozenCompression == 0) {
      using namespace regrip_vector_history;
      std::vector<V> probes{{1e-8L, 0, 0},
                            {0, 1e-8L, 0},
                            {-1e-8L, 0, 0},
                            {0, -1e-8L, 0},
                            {1e-5L, -2e-5L, 0}};
      if (frozenNormalized) {
        auto mutableSnapshot = std::make_shared<NormalizedSnapshot>(
            [&](R s) { return field->materialAt(s); },
            [&](R s) { return field->lastIncrementAt(s); }, frozen[1],
            frozen[2], frozenTolerance, probes,
            frozenTolerance * frozen[2] * 1e-3L, field->isZeroState());
        mutableSnapshot->outwardPrefilter = frozenOutward;
        std::shared_ptr<const NormalizedSnapshot> snapshot =
            std::move(mutableSnapshot);
        auto transfer = [&](unsigned count) {
          R value = 0;
          for (const auto &cell : snapshot->cells)
            for (unsigned j = 0; j < count; ++j) {
              R s = cell.lo + (cell.hi - cell.lo) * (R(j) + .5L) / count;
              auto old = field->elasticAt(s), next = snapshot->at(s).elastic;
              value += frozen[0] * (cell.hi - cell.lo) / count * .5L *
                       frozen[1] * (dot(next, next) - dot(old, old));
            }
          return value;
        };
        R rep8 = transfer(8);
        rep16 = transfer(16);
        repDifference = rep16 - rep8;
        cells = snapshot->cells.size();
        auto next = std::make_unique<VectorField>(
            frozen[0], frozen[1], V{0, 0, 1},
            [snapshot](R s) { return snapshot->at(s); }, frozen[2],
            snapshot->lipschitzBound(), snapshot->knots(),
            [snapshot](R lo, R hi) { return snapshot->localBound(lo, hi); },
            [snapshot](const Step &s, R lo, R hi) {
              return snapshot->stickRoundoffBound(s, lo, hi);
            },
            [snapshot](V v) { return snapshot->tangentKnots(v); },
            [snapshot](R s, V v) { return snapshot->loadingSide(s, v); });
        Step rest;
        rest.capacity = frozen[2];
        stored = next->evaluate(rest, 1e-7L, 1e-30L, 100000).integral.v[1];
        field = std::move(next);
      } else {
        auto snapshot = std::make_shared<const AdaptiveSnapshot>(
            [&](R s) { return field->elasticAt(s); }, frozen[1], frozen[2],
            frozenTolerance, probes, frozenTolerance * frozen[2] * 1e-3L);
        auto yieldState = std::make_shared<const IdealYieldState>(snapshot);
        yieldState->tangentKnots(
            V{1, 0, 0}); // Pure exact-sign precomputation,not history update.
        auto transfer = [&](unsigned count) {
          R value = 0;
          for (const auto &cell : snapshot->cells)
            for (unsigned j = 0; j < count; ++j) {
              R s = cell.lo + (cell.hi - cell.lo) * (R(j) + .5L) / count;
              auto old = field->elasticAt(s), next = snapshot->at(s);
              value += frozen[0] * (cell.hi - cell.lo) / count * .5L *
                       frozen[1] * (dot(next, next) - dot(old, old));
            }
          return value;
        };
        R rep8 = transfer(8);
        rep16 = transfer(16);
        repDifference = rep16 - rep8;
        cells = snapshot->cells.size();
        auto next = std::make_unique<VectorField>(
            frozen[0], frozen[1], V{0, 0, 1},
            [snapshot, yieldState](R s) {
              return VectorField::MaterialValue{snapshot->at(s),
                                                yieldState->at(s)};
            },
            frozen[2], snapshot->lipschitzBound(), snapshot->knots(),
            [snapshot](R lo, R hi) { return snapshot->localBound(lo, hi); },
            [snapshot](const Step &s, R lo, R hi) {
              if (s.capacity != snapshot->C || s.increment[1] != V{} ||
                  s.increment[2] != V{})
                return -1.L;
              return certifiedStickDensityError(*snapshot, s.increment[0], lo,
                                                hi);
            },
            [yieldState](V direction) {
              return yieldState->tangentKnots(direction);
            });
        Step rest;
        rest.capacity = frozen[2];
        stored = next->evaluate(rest, 1e-7L, 1e-30L, 100000).integral.v[1];
        field = std::move(next); // New immutable seed owns its snapshot;no
                                 // old-pointer capture.
      }
    }
    if (journal) {
      journal << getContext()->getTime() << ',' << commits << ',' << previous[0]
              << ',' << previous[1] << ',' << -v[5] << ',' << -v[6] << ','
              << v[0] << ',' << v[1] << ',' << v[2] << ',' << cumulativeLoss
              << ',' << v[3] << ',' << v[4] << ','
              << v[1] - v[0] - v[4] + v[2] + v[3] << ','
              << t.integral.evaluations << ',' << t.integral.nonuniqueSamples
              << ',' << previous[2];
      const auto &velocity =
          mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
      for (int j = 0; j < 3; ++j)
        journal << ',' << velocity[0][j];
      for (double z : beginX)
        journal << ',' << z;
      for (double z : beginV)
        journal << ',' << z;
      for (int j = 0; j < 3; ++j)
        journal << ',' << -beginMeasures[5 + j];
      for (int j = 0; j < 9; ++j)
        journal << ',' << -beginMeasures[8 + j];
      journal << ',' << stored << ',' << rep16 << ',' << repDifference << ','
              << stored - v[1] - rep16 << ',' << cells << '\n';
      journal.flush();
    }
  }
  void handleEvent(sofa::core::objectmodel::Event *event) override {
    if (dynamic_cast<sofa::simulation::AnimateBeginEvent *>(event)) {
      if (begins != ends)
        throw std::runtime_error("duplicate begin");
      ++begins;
      const auto &x =
          mstate->read(sofa::core::vec_id::read_access::position)->getValue();
      const auto &velocity =
          mstate->read(sofa::core::vec_id::read_access::velocity)->getValue();
      for (int j = 0; j < 3; ++j) {
        beginX[j] = x[0][j];
        beginV[j] = velocity[0][j];
      }
      beginMeasures = trial(x).integral.v;
    } else if (dynamic_cast<sofa::simulation::AnimateEndEvent *>(event)) {
      if (ends + 1 != begins)
        throw std::runtime_error("missing/duplicate end");
      commit(
          mstate->read(sofa::core::vec_id::read_access::position)->getValue());
      ++ends;
    }
  }
  void addForce(const sofa::core::MechanicalParams *, DataVecDeriv &f,
                const DataVecCoord &x, const DataVecDeriv &) override {
    auto t = trial(x.getValue());
    auto v = f.getValue();
    if (v.size() != 1)
      throw std::invalid_argument("patch force size");
    for (int j = 0; j < 3; ++j)
      v[0][j] -= double(t.integral.v[5 + j]);
    f.setValue(v);
  }
  void addDForce(const sofa::core::MechanicalParams *p, DataVecDeriv &df,
                 const DataVecDeriv &dx) override {
    if (!p || df.getValue().size() != 1 || dx.getValue().size() != 1)
      throw std::invalid_argument("patch dforce size/params");
    auto t = trial(
        mstate->read(sofa::core::vec_id::read_access::position)->getValue());
    auto v = df.getValue();
    double factor =
        p->kFactorIncludingRayleighDamping(rayleighStiffness.getValue());
    for (int i = 0; i < 3; ++i)
      for (int j = 0; j < 3; ++j)
        v[0][i] -=
            factor * double(t.integral.v[8 + 3 * i + j]) * dx.getValue()[0][j];
    df.setValue(v);
  }
  void buildStiffnessMatrix(sofa::core::behavior::StiffnessMatrix *m) override {
    if (!m)
      throw std::invalid_argument("patch matrix");
    auto t = trial(
        mstate->read(sofa::core::vec_id::read_access::position)->getValue());
    auto a = m->getForceDerivativeIn(mstate.get())
                 .withRespectToPositionsIn(mstate.get());
    if (!a)
      throw std::invalid_argument("patch accumulator");
    for (int i = 0; i < 3; ++i)
      for (int j = 0; j < 3; ++j)
        a(i, j) += -double(t.integral.v[8 + 3 * i + j]);
  }
  SReal getPotentialEnergy(const sofa::core::MechanicalParams *,
                           const DataVecCoord &x) const override {
    // Stored elastic inventory only,NOT the incremental potential U+D.
    // Friction is history-dependent;generic conservative-energy claims invalid.
    return double(trial(x.getValue()).integral.v[1]);
  }
};
extern "C" {
__attribute__((visibility("default"))) void initExternalModule() {}
__attribute__((visibility("default"))) const char *getModuleName() {
  return "ReGripVectorPatchReference";
}
__attribute__((visibility("default"))) void
registerObjects(sofa::core::ObjectFactory *f) {
  f->registerObjects(sofa::core::ObjectRegistrationData(
                         "Independent fixed-normal function-history "
                         "benchmark,NOT collision/grasp")
                         .add<VectorPatchBenchmark>());
}
}
