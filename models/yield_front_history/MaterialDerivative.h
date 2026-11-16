#pragma once
#include "NormalizedSnapshot.h"
namespace regrip_vector_history {
struct MaterialDerivative {
  V value{}, first{}, second{};
};
template <class T>
std::array<T, 3> materialLift(const MaterialDerivative &jet,
                              const T &coordinate, R origin) {
  if (coordinate.v != double(origin))
    throw std::invalid_argument(
        "material Taylor lift must be based at actual AD coordinate");
  T delta = coordinate - T(double(origin));
  std::array<T, 3> out;
  for (int j = 0; j < 3; ++j)
    out[j] = T(double(jet.value[j])) + T(double(jet.first[j])) * delta +
             T(double(.5L * jet.second[j])) * delta * delta;
  return out;
}
// Interior jet in FIXED material coordinates. Required when a force quadrature
// abscissa moves with mechanical coordinates;freezing old e(s(q)) drops chain
// terms. This helper alone is NOT a SOFA curved-contact Jacobian.
inline MaterialDerivative
materialDerivative(const NormalizedSnapshot &field,
                   const NormalizedSnapshot::Cell &cell, R x) {
  if (!(x > cell.lo && x < cell.hi))
    throw std::domain_error(
        "material derivative requires explicit open-cell side;no classical "
        "derivative at partition boundary");
  MaterialDerivative result;
  const NormalizedSnapshot::Node *ns[4] = {&cell.left, &cell.control1,
                                           &cell.control2, &cell.right};
  bool zero = true;
  for (auto n : ns)
    zero = zero && n->gap == 1;
  if (zero)
    return result;
  R width = cell.hi - cell.lo, u = (x - cell.lo) / width, v = 1 - u,
    w[4] = {v * v * v, 3 * u * v * v, 3 * u * u * v, u * u * u};
  V p{}, dp{}, ddp{};
  R gap = 0, dgap = 0, ddgap = 0;
  for (int j = 0; j < 4; ++j) {
    p = add(p, scale(ns[j]->direction, w[j]));
    gap += w[j] * ns[j]->gap;
  }
  R w1[3] = {v * v, 2 * u * v, u * u};
  for (int j = 0; j < 3; ++j) {
    dp = add(dp, scale(add(ns[j + 1]->direction, scale(ns[j]->direction, -1)),
                       3 * w1[j] / width));
    dgap += 3 * w1[j] * (ns[j + 1]->gap - ns[j]->gap) / width;
  }
  for (int j = 0; j < 2; ++j) {
    R w2 = j ? u : v;
    ddp = add(ddp,
              scale(add(ns[j + 2]->direction,
                        add(scale(ns[j + 1]->direction, -2), ns[j]->direction)),
                    6 * w2 / (width * width)));
    ddgap += 6 * w2 * (ns[j + 2]->gap - 2 * ns[j + 1]->gap + ns[j]->gap) /
             (width * width);
  }
  R r = norm(p);
  if (r < .5L)
    throw std::domain_error("unresolved material direction chart");
  R pp = dot(p, dp), p2 = dot(dp, dp) + dot(p, ddp);
  V n = scale(p, 1 / r),
    dn = add(scale(dp, 1 / r), scale(p, -pp / (r * r * r))),
    ddn = add(
        scale(ddp, 1 / r),
        add(scale(dp, -2 * pp / (r * r * r)),
            scale(p, -p2 / (r * r * r) + 3 * pp * pp / (r * r * r * r * r))));
  R c = field.C * (1 - x * x), dc = -2 * field.C * x, ddc = -2 * field.C,
    rho = 1 - gap, drho = -dgap, ddrho = -ddgap;
  R A = c * rho / field.k, dA = (dc * rho + c * drho) / field.k,
    ddA = (ddc * rho + 2 * dc * drho + c * ddrho) / field.k;
  result.value = scale(n, A);
  result.first = add(scale(n, dA), scale(dn, A));
  result.second = add(scale(n, ddA), add(scale(dn, 2 * dA), scale(ddn, A)));
  return result;
}
} // namespace regrip_vector_history
