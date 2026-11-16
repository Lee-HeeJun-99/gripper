#include "../models/yield_front_history/NormalizedSnapshot.h"
#include <iomanip>
#include <iostream>
#include <memory>
using namespace regrip_vector_history;
int main(int argc, char **) {
  try {
    constexpr R a = .3192L, k = .001L, C = 3e-6L;
    VectorField truth(a, k);
    for (int i = 0; i < 24; ++i) {
      Step s;
      s.capacity = C;
      s.increment = {
          V{.0012L * std::cos(.9L * i), .0009L * std::sin(.7L * i), 0},
          V{.0001L, -.00013L, 0}, V{.00003L, .00002L, 0}};
      auto t = truth.evaluate(s, 1e-6L, 1e-25L);
      truth.commit(t);
    }
    std::vector<V> probes{{1e-8L, 0, 0},
                          {0, 1e-8L, 0},
                          {-1e-8L, 0, 0},
                          {0, -1e-8L, 0},
                          {1e-5L, -2e-5L, 0}};
    NormalizedSnapshot snapshot([&](R x) { return truth.materialAt(x); },
                                [&](R x) { return truth.lastIncrementAt(x); },
                                k, C, 1e-9L, probes, 3e-18L);
    R maximum = 0;
    unsigned phaseMismatch = 0;
    constexpr unsigned count = 131072;
    for (unsigned j = 0; j < count; ++j) {
      R x = -1 + 2 * (R(j) + .5L) / count;
      auto exact = truth.materialAt(x), approx = snapshot.at(x);
      maximum = std::max(maximum,
                         norm(add(exact.elastic, scale(approx.elastic, -1))));
      if (exact.onYield != approx.onYield)
        ++phaseMismatch;
    }
    std::cout << std::setprecision(18)
              << "NORMALIZED {\"cells\":" << snapshot.cells.size()
              << ",\"queries\":" << snapshot.queries
              << ",\"max_state_error\":" << maximum
              << ",\"phase_mismatches\":" << phaseMismatch
              << ",\"phase_uncertain_width\":" << snapshot.phaseUncertainWidth
              << "}\n";
    if (maximum > 1e-9L || phaseMismatch)
      throw std::runtime_error("independent normalized state/phase gate fails");
    NormalizedSnapshot zero([](R) { return VectorField::MaterialValue{}; },
                            [](R) { return V{}; }, k, C, 1e-9L, probes, 3e-18L,
                            true);
    if (zero.at(0).elastic != V{} || zero.at(0).onYield)
      throw std::runtime_error("zero state must not invent a direction");
    auto mutableSaved = std::make_shared<NormalizedSnapshot>(snapshot);
    mutableSaved->outwardPrefilter = argc == 2;
    std::shared_ptr<const NormalizedSnapshot> saved = std::move(mutableSaved);
    for (unsigned j = 0; j < 257; ++j) {
      R lo = -1 + 2 * R(j) / 258, hi = lo + 1.L / 258;
      R brute = 0;
      for (const auto &c : saved->cells)
        if (c.hi > lo && c.lo < hi) {
          R width = c.hi - c.lo, gap = 0, direction = 0;
          const NormalizedSnapshot::Node *ns[4] = {&c.left, &c.control1,
                                                   &c.control2, &c.right};
          for (int axis = 1; axis < 4; ++axis) {
            gap = std::max(
                gap, 3 * std::abs(ns[axis]->gap - ns[axis - 1]->gap) / width);
            direction = std::max(
                direction, 3 *
                               norm(add(ns[axis]->direction,
                                        scale(ns[axis - 1]->direction, -1))) /
                               width);
          }
          brute = std::max(brute, 2 * C / k + C / k * (gap + 2 * direction));
        }
      if (brute != saved->localBound(lo, hi))
        throw std::runtime_error("range lookup changes material bound");
      auto &c = saved->cellAt((lo + hi) / 2);
      Step probe;
      probe.capacity = C;
      probe.increment[0] = probes[j % probes.size()];
      R l = c.lo + .2L * (c.hi - c.lo), r = c.lo + .8L * (c.hi - c.lo);
      R direct = saved->uncachedStickRoundoffBound(probe, l, r);
      if (saved->stickRoundoffBound(probe, l, r) != direct ||
          saved->stickRoundoffBound(probe, l, r) != direct)
        throw std::runtime_error("pure exact certificate cache changes result");
    }
    for (unsigned p = 0; p < probes.size(); ++p) {
      VectorField candidate(
          a, k, {0, 0, 1}, [saved](R x) { return saved->at(x); }, C,
          saved->lipschitzBound(), saved->knots(),
          [saved](R lo, R hi) { return saved->localBound(lo, hi); },
          [saved](const Step &s, R lo, R hi) {
            return saved->stickRoundoffBound(s, lo, hi);
          },
          [saved](V v) { return saved->tangentKnots(v); },
          [saved](R x, V v) { return saved->loadingSide(x, v); });
      VectorField reference(
          a, k, {0, 0, 1}, [&](R x) { return truth.materialAt(x); }, C,
          truth.lipschitzUpperBound(), saved->knots());
      Step step;
      step.capacity = C;
      step.increment[0] = probes[p];
      std::cout << "NORMALIZED_PROBE_BEGIN " << p << std::endl;
      auto exact = reference.evaluate(step, 1e-7L, 1e-35L);
      auto fit = candidate.evaluate(step, 1e-7L, 1e-35L);
      R error = exact.integral.v[2]
                    ? std::abs(fit.integral.v[2] - exact.integral.v[2]) /
                          exact.integral.v[2]
                    : (fit.integral.v[2] ? INFINITY : 0);
      std::cout << "NORMALIZED_PROBE " << p << ' ' << exact.integral.v[2] << ' '
                << fit.integral.v[2] << ' ' << error << std::endl;
      if (!(error < .01L))
        throw std::runtime_error(
            "normalized prospective loss fails unchanged1%gate");
    }
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
