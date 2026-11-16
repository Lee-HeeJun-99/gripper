#include "../models/yield_front_history/NormalizedSnapshot.h"
#include <chrono>
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
int main() {
  try {
    if (!Outward::supported())
      throw std::runtime_error("unsupported outward nearest binary platform");
    unsigned coefficients = 0;
    for (unsigned degree : {2u, 6u, 10u, 26u})
      for (unsigned seed = 0; seed < 8; ++seed) {
        OP p;
        QP q;
        for (unsigned j = 0; j <= degree; ++j) {
          R value = std::sin(R(17 * j + seed)) * .01L;
          p.emplace_back(value);
          q.push_back(binaryRational(value));
        }
        R lo = R(seed) / 17, hi = lo + .01L;
        auto bs = outwardBernstein(p, lo, hi);
        unsigned n = degree;
        for (unsigned i = 0; i <= n; ++i) {
          Q exact = 0;
          for (unsigned j = 0; j <= i; ++j) {
            Q power = 0;
            for (unsigned z = j; z <= n; ++z) {
              Q l = 1, w = 1;
              for (unsigned a = 0; a < z - j; ++a)
                l *= binaryRational(lo);
              for (unsigned a = 0; a < j; ++a)
                w *= binaryRational(hi) - binaryRational(lo);
              power += q[z] * choose(z, j) * l * w;
            }
            exact += power * choose(i, j) / choose(n, j);
          }
          if (binaryRational(bs[i].lo) > exact ||
              binaryRational(bs[i].hi) < exact)
            throw std::runtime_error(
                "exact Bernstein coefficient outside enclosure");
          ++coefficients;
        }
      }
    constexpr R a = .3192L, k = .001L, C = 3e-6L;
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
    NormalizedSnapshot saved([&](R x) { return source.materialAt(x); },
                             [&](R x) { return source.lastIncrementAt(x); }, k,
                             C, 1e-9L, probes, 3e-18L);
    auto faster = saved;
    faster.outwardPrefilter = true;
    unsigned certified = 0;
    double fastSeconds = 0, exactSeconds = 0;
    using Clock = std::chrono::steady_clock;
    for (unsigned j = 0; j < 257; ++j) {
      R x = -1 + 2 * (R(j) + .5L) / 257;
      const auto &c = saved.cellAt(x);
      R lo = c.lo + .2L * (c.hi - c.lo), hi = c.lo + .8L * (c.hi - c.lo);
      Step s;
      s.capacity = C;
      s.increment[0] = probes[j % probes.size()];
      auto start = Clock::now();
      R exact = saved.uncachedStickRoundoffBound(s, lo, hi);
      exactSeconds +=
          std::chrono::duration<double>(Clock::now() - start).count();
      start = Clock::now();
      R fast = faster.uncachedStickRoundoffBound(s, lo, hi);
      fastSeconds +=
          std::chrono::duration<double>(Clock::now() - start).count();
      if (fast != exact)
        throw std::runtime_error("prefilter changed exact certificate/bound");
      if (saved.outwardStick(s, lo, hi))
        ++certified;
    }
    if (!certified || std::fegetround() != FE_TONEAREST)
      throw std::runtime_error(
          "no useful certificates or changed caller rounding");
    std::cout << std::setprecision(18)
              << "OUTWARD {\"exact_coefficient_enclosures\":" << coefficients
              << ",\"material_intervals\":257,\"prefilter_certified\":"
              << certified << ",\"fast_seconds\":" << fastSeconds
              << ",\"exact_seconds\":" << exactSeconds << "}\n";
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
