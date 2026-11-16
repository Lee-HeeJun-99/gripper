#pragma once
#include "VectorReturn.h"
#include <algorithm>
#include <cfenv>
#include <limits>
#include <vector>
namespace regrip_vector_history {
// Nearest-rounded binary primitives expanded by one REPRESENTABLE neighbour.
// Finite,IEC559,non-fast-math only. No epsilon pressure/capacity/force floor.
// Inconclusive enclosures fall back to the unchanged exact-rational test.
struct Outward {
  R lo, hi;
  Outward(R value = 0) : lo(value), hi(value) {
    if (!std::isfinite(value))
      throw std::domain_error("finite interval input");
  }
  Outward(R l, R h) : lo(l), hi(h) {
    if (!std::isfinite(l) || !std::isfinite(h) || l > h)
      throw std::domain_error("finite ordered enclosure");
  }
  static bool supported() {
#ifdef __FAST_MATH__
    return false;
#else
    return std::numeric_limits<R>::is_iec559 &&
           std::numeric_limits<R>::radix == 2 &&
           std::fegetround() == FE_TONEAREST;
#endif
  }
  static R down(R value) {
    if (!std::isfinite(value))
      throw std::overflow_error("outward interval overflow");
    return std::nextafter(value, -std::numeric_limits<R>::infinity());
  }
  static R up(R value) {
    if (!std::isfinite(value))
      throw std::overflow_error("outward interval overflow");
    return std::nextafter(value, std::numeric_limits<R>::infinity());
  }
  friend Outward operator+(Outward a, Outward b) {
    volatile R l = a.lo + b.lo, h = a.hi + b.hi;
    return {down(l), up(h)};
  }
  friend Outward operator-(Outward a, Outward b) {
    volatile R l = a.lo - b.hi, h = a.hi - b.lo;
    return {down(l), up(h)};
  }
  friend Outward operator*(Outward a, Outward b) {
    volatile R x = a.lo * b.lo, y = a.lo * b.hi, z = a.hi * b.lo,
               w = a.hi * b.hi;
    return {down(std::min(std::min(R(x), R(y)), std::min(R(z), R(w)))),
            up(std::max(std::max(R(x), R(y)), std::max(R(z), R(w))))};
  }
  friend Outward operator/(Outward a, Outward b) {
    if (b.lo <= 0 && b.hi >= 0)
      throw std::domain_error("interval denominator crosses zero");
    volatile R l = 1 / b.hi, h = 1 / b.lo;
    return a * Outward(down(l), up(h));
  }
};
using OP = std::vector<Outward>;
inline OP outwardProduct(const OP &a, const OP &b) {
  OP result(a.size() + b.size() - 1);
  for (unsigned j = 0; j < a.size(); ++j)
    for (unsigned k = 0; k < b.size(); ++k)
      result[j + k] = result[j + k] + a[j] * b[k];
  return result;
}
inline OP outwardSum(OP a, const OP &b, R factor) {
  a.resize(std::max(a.size(), b.size()));
  for (unsigned j = 0; j < b.size(); ++j)
    a[j] = a[j] + Outward(factor) * b[j];
  return a;
}
inline OP outwardPower(Outward a, Outward b, Outward c, Outward d) {
  return {a, Outward(3) * (b - a), Outward(3) * (a - Outward(2) * b + c),
          Outward(0) - a + Outward(3) * b - Outward(3) * c + d};
}
inline unsigned long long outwardChoose(unsigned n, unsigned k) {
  if (n > 30)
    throw std::invalid_argument("bounded interval polynomial degree");
  unsigned long long r = 1;
  for (unsigned j = 1; j <= k; ++j)
    r = r * (n - j + 1) / j;
  return r;
}
inline OP outwardBernstein(const OP &p, Outward lo, Outward hi) {
  unsigned n = unsigned(p.size() - 1);
  OP powers(n + 1), lp(n + 1, Outward(1)), wp(n + 1, Outward(1));
  for (unsigned j = 1; j <= n; ++j) {
    lp[j] = lp[j - 1] * lo;
    wp[j] = wp[j - 1] * (hi - lo);
  }
  for (unsigned j = 0; j <= n; ++j)
    for (unsigned i = j; i <= n; ++i)
      powers[j] =
          powers[j] + p[i] * Outward(outwardChoose(i, j)) * lp[i - j] * wp[j];
  OP result(n + 1);
  for (unsigned i = 0; i <= n; ++i)
    for (unsigned j = 0; j <= i; ++j)
      result[i] = result[i] + powers[j] * Outward(outwardChoose(i, j)) /
                                  Outward(outwardChoose(n, j));
  return result;
}
inline bool outwardNegative(const OP &p, Outward lo, Outward hi) {
  for (auto b : outwardBernstein(p, lo, hi))
    if (b.hi > 0)
      return false;
  return true;
}
inline bool outwardPositive(const OP &p, Outward lo, Outward hi) {
  for (auto b : outwardBernstein(p, lo, hi))
    if (b.lo < 0)
      return false;
  return true;
}
} // namespace regrip_vector_history
