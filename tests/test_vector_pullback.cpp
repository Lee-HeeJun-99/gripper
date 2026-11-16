#include "../models/conservative_beam/EnergyKernel.h"
#include "../models/yield_front_history/MaterialDerivative.h"
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
int main() {
  try {
    constexpr R k = .001L, C = 3e-6L;
    std::vector<V> probes{{1e-8L, 0, 0}};
    NormalizedSnapshot field([](R) { return VectorField::MaterialValue{}; },
                             [](R) { return V{}; }, k, C, 1e-9L, probes, 1e-18L,
                             true);
    // Independent manufactured admissible cubic,not fitted to derivative
    // answers.
    NormalizedSnapshot::Cell cell;
    cell.lo = -.8L;
    cell.hi = .9L;
    cell.left = {.1L, {1, 0, 0}};
    cell.control1 = {.4L, {.9L, .2L, 0}};
    cell.control2 = {.2L, {.8L, .35L, 0}};
    cell.right = {0, {.7L, .5L, 0}};
    R maxValue = 0, maxFirst = 0, maxSecond = 0, maxFD = 0, maxChain = 0,
      maxLift = 0;
    unsigned count = 0;
    for (unsigned j = 0; j < 257; ++j) {
      R x = cell.lo + (cell.hi - cell.lo) * (R(j) + .5L) / 257;
      auto result = materialDerivative(field, cell, x);
      using J = regrip_beam::Jet;
      J s{double(x)};
      s = s + J::variable(0);
      J u = (s - J(double(cell.lo))) * J(1 / double(cell.hi - cell.lo)),
        v = J(1) - u;
      J weights[4] = {v * v * v, J(3) * u * v * v, J(3) * u * u * v, u * u * u};
      J gap;
      std::array<J, 3> p{};
      const NormalizedSnapshot::Node *ns[4] = {&cell.left, &cell.control1,
                                               &cell.control2, &cell.right};
      for (int m = 0; m < 4; ++m) {
        gap = gap + weights[m] * J(double(ns[m]->gap));
        for (int a = 0; a < 3; ++a)
          p[a] = p[a] + weights[m] * J(double(ns[m]->direction[a]));
      }
      J norm2;
      for (int a = 0; a < 3; ++a)
        norm2 = norm2 + p[a] * p[a];
      J amp = J(double(C / k)) * (J(1) - s * s) * (J(1) - gap) *
              regrip_beam::inverse(regrip_beam::root(norm2));
      for (int a = 0; a < 3; ++a) {
        J value = amp * p[a];
        maxValue = std::max(maxValue, std::abs(result.value[a] - value.v));
        maxFirst = std::max(maxFirst, std::abs(result.first[a] - value.g[0]));
        maxSecond =
            std::max(maxSecond, std::abs(result.second[a] - value.h[0]));
      }
      R h = 1e-6L;
      auto plus = materialDerivative(field, cell, x + h),
           minus = materialDerivative(field, cell, x - h);
      for (int a = 0; a < 3; ++a)
        maxFD = std::max(maxFD,
                         std::abs((plus.value[a] - minus.value[a]) / (2 * h) -
                                  result.first[a]));
      // x(q)=x+.3q+.1q²:both chain terms are needed at second order.
      J q = J::variable(0), composed = J(double(x)) + J(.3) * q + J(.1) * q * q;
      auto lifted = materialLift(result, composed, x);
      for (int a = 0; a < 3; ++a) {
        R fd = (plus.first[a] - minus.first[a]) / (2 * h) * .09L +
               result.first[a] * .2L;
        maxChain = std::max(maxChain, std::abs(fd - (result.second[a] * .09L +
                                                     result.first[a] * .2L)));
        maxLift = std::max(
            maxLift, std::abs(R(lifted[a].h[0]) - (result.second[a] * .09L +
                                                   result.first[a] * .2L)));
      }
      ++count;
    }
    bool rejected = false;
    try {
      materialDerivative(field, cell, cell.lo);
    } catch (const std::domain_error &) {
      rejected = true;
    }
    if (!rejected)
      throw std::runtime_error(
          "partition boundary silently assigned a classical derivative");
    std::cout << std::setprecision(18) << "PULLBACK {\"states\":" << count
              << ",\"value_AD\":" << maxValue << ",\"first_AD\":" << maxFirst
              << ",\"second_AD\":" << maxSecond << ",\"first_FD\":" << maxFD
              << ",\"second_chain_FD\":" << maxChain
              << ",\"AD_material_lift\":" << maxLift << "}\n";
    if (maxValue > 1e-16L || maxFirst > 1e-15L || maxSecond > 1e-14L ||
        maxFD > 1e-11L || maxChain > 1e-10L || maxLift > 1e-16L)
      throw std::runtime_error("material pullback derivative gate");
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
