#include "../models/yield_front_history/NormalizedSnapshot.h"
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
int main() {
  try {
    constexpr R k = .001L, C = 3e-6L, a = .3192L;
    VectorField source(a, k);
    for (int i = 0; i < 8; ++i) {
      Step s;
      s.capacity = C;
      s.increment = {
          V{.001L * std::cos(.7L * i), .0012L * std::sin(.9L * i), 0},
          V{.0001L, -.0001L, 0}, V{}};
      auto t = source.evaluate(s, 1e-6L, 1e-25L);
      source.commit(t);
    }
    std::vector<V> probes{{1e-8L, 0, 0},
                          {0, 1e-8L, 0},
                          {-1e-8L, 0, 0},
                          {0, -1e-8L, 0},
                          {1e-5L, -2e-5L, 0}};
    NormalizedSnapshot base([&](R x) { return source.materialAt(x); },
                            [&](R x) { return source.lastIncrementAt(x); }, k,
                            C, 1e-9L, probes, 3e-18L);
    R maxState = 0, maxForce = 0, maxEnergy = 0, maxLoss = 0, maxJacobian = 0;
    unsigned states = 0;
    V axis = scale(V{1, 2, 3}, 1 / std::sqrt(14.L));
    for (R angle : {.1L, 1.7L, 3.0L}) {
      R c = std::cos(angle), s = std::sin(angle);
      M Q{};
      for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
          Q[3 * i + j] = c * (i == j ? 1 : 0) + (1 - c) * axis[i] * axis[j];
      Q[1] -= s * axis[2];
      Q[2] += s * axis[1];
      Q[3] += s * axis[2];
      Q[5] -= s * axis[0];
      Q[6] -= s * axis[1];
      Q[7] += s * axis[0];
      auto rotate = [&](V v) {
        V out{};
        for (int i = 0; i < 3; ++i)
          for (int j = 0; j < 3; ++j)
            out[i] += Q[3 * i + j] * v[j];
        return out;
      };
      auto moved = base.transformed(Q);
      for (unsigned j = 0; j < 257; ++j) {
        R x = -1 + 2 * (R(j) + .5L) / 257;
        auto old = base.at(x), next = moved.at(x);
        maxState = std::max(
            maxState, norm(add(next.elastic, scale(rotate(old.elastic), -1))));
        if (old.onYield != next.onYield ||
            old.normalizedGap != next.normalizedGap)
          throw std::runtime_error("frame change altered phase/gap");
        V du = {1e-5L, -2e-5L, 0};
        auto r = radialReturn(old.elastic, du, base.normal, k, C * (1 - x * x)),
             t = radialReturn(next.elastic, rotate(du), moved.normal, k,
                              C * (1 - x * x));
        maxForce = std::max(
            maxForce, norm(add(t.traction, scale(rotate(r.traction), -1))));
        maxEnergy = std::max(maxEnergy, std::abs(r.energy - t.energy));
        maxLoss = std::max(maxLoss, std::abs(r.loss - t.loss));
        for (int i = 0; i < 3; ++i)
          for (int z = 0; z < 3; ++z) {
            R expected = 0;
            for (int m = 0; m < 3; ++m)
              for (int n = 0; n < 3; ++n)
                expected += Q[3 * i + m] * r.tangent[3 * m + n] * Q[3 * z + n];
            maxJacobian = std::max(maxJacobian,
                                   std::abs(expected - t.tangent[3 * i + z]));
          }
        ++states;
      }
    }
    bool rejected = false;
    try {
      base.transformed(M{1, 0, 0, 0, 1, 0, 0, 0, -1});
    } catch (const std::invalid_argument &) {
      rejected = true;
    }
    if (!rejected)
      throw std::runtime_error("reflection accepted");
    std::cout << std::setprecision(18) << "FRAME {\"states\":" << states
              << ",\"state\":" << maxState << ",\"force\":" << maxForce
              << ",\"energy\":" << maxEnergy << ",\"loss\":" << maxLoss
              << ",\"jacobian\":" << maxJacobian << "}\n";
    if (maxState > 1e-19L || maxForce > 1e-22L || maxEnergy > 1e-24L ||
        maxLoss > 1e-24L || maxJacobian > 1e-18L)
      throw std::runtime_error("normalized constant-frame covariance gate");
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
