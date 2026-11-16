#pragma once
#include "../conservative_beam/EnergyKernel.h"
#include "MaterialDerivative.h"
namespace regrip_vector_history {
// Adapter prerequisite:immutable previous Hermite geometry supplies the REAL
// sphere normal/capacity,not the isolation patch's parabolic pressure.
// Still a prescribed-history chart,NOT a new production SOFA contact component.
struct SphereChartInput {
  regrip3d::Pose left, right;
  V center{};
  R length = 1, radius = 1, skin = .02L, kn = .001L, mu = .5L, kt = .001L;
  NormalizedSnapshot::Cell history;
};
struct SphereChartResult {
  bool active = false;
  MaterialDerivative elastic, normal;
  R capacity = 0, capacityFirst = 0, capacitySecond = 0, normalForce = 0;
};
inline SphereChartResult sphereHistoryChart(const SphereChartInput &in, R x) {
  regrip3d::validate(in.left);
  regrip3d::validate(in.right);
  finite(in.center);
  for (R value : in.center)
    if (!std::isfinite(double(value)))
      throw std::invalid_argument("representable center");
  if (!std::isfinite(in.history.lo) || !std::isfinite(in.history.hi) ||
      in.history.hi <= in.history.lo)
    throw std::invalid_argument("finite ordered material cell");
  if (!(x > in.history.lo && x < in.history.hi) || x <= -1 || x >= 1)
    throw std::domain_error(
        "open material cell required for sphere chart derivative");
  for (R v : {in.length, in.radius, in.skin, in.kn, in.mu, in.kt})
    if (!std::isfinite(v) || !std::isfinite(double(v)) || v < 0)
      throw std::invalid_argument("sphere chart physical parameters");
  if (double(in.length) == 0 || double(in.radius) == 0 || double(in.kt) == 0)
    throw std::invalid_argument("positive length/radius/kt");
  using J = regrip_beam::Jet;
  J s{double(x)};
  s = s + J::variable(0);
  J t = J(.5) * (s + J(1)), u = J(1) - t;
  J weights[4] = {u * u * u, J(3) * t * u * u, J(3) * t * t * u, t * t * t};
  std::array<V, 4> controls{};
  for (int a = 0; a < 3; ++a) {
    controls[0][a] = in.left.p[a];
    controls[3][a] = in.right.p[a];
  }
  auto director0 = regrip3d::rotate(in.left.q, {1, 0, 0}),
       director1 = regrip3d::rotate(in.right.q, {1, 0, 0});
  for (int a = 0; a < 3; ++a) {
    controls[1][a] = controls[0][a] + in.length / 3 * director0[a];
    controls[2][a] = controls[3][a] - in.length / 3 * director1[a];
  }
  std::array<J, 3> position{};
  for (int a = 0; a < 3; ++a) {
    for (int j = 0; j < 4; ++j)
      position[a] =
          position[a] + weights[j] * J(double(controls[j][a] - in.center[a]));
  }
  J squared;
  for (auto v : position)
    squared = squared + v * v;
  J distance = regrip_beam::root(squared),
    gap = J(double(in.radius + in.skin)) - distance;
  if (gap.v == 0)
    throw std::domain_error(
        "contact boundary has no undeclared classical derivative");
  SphereChartResult out;
  if (gap.v < 0)
    return out;
  out.active = true;
  auto unpack = [](const std::array<J, 3> &v) {
    MaterialDerivative r;
    for (int a = 0; a < 3; ++a) {
      r.value[a] = v[a].v;
      r.first[a] = v[a].g[0];
      r.second[a] = v[a].h[0];
    }
    return r;
  };
  J inverseDistance = regrip_beam::inverse(distance);
  std::array<J, 3> normal;
  for (int a = 0; a < 3; ++a)
    normal[a] = position[a] * inverseDistance;
  out.normal = unpack(normal);
  J cap = J(double(in.mu * in.kn)) * gap;
  out.capacity = cap.v;
  out.capacityFirst = cap.g[0];
  out.capacitySecond = cap.h[0];
  out.normalForce = double(in.kn) * gap.v;
  const NormalizedSnapshot::Node *ns[4] = {
      &in.history.left, &in.history.control1, &in.history.control2,
      &in.history.right};
  J v = (s - J(double(in.history.lo))) *
        J(1 / double(in.history.hi - in.history.lo)),
    w = J(1) - v;
  J basis[4] = {w * w * w, J(3) * v * w * w, J(3) * v * v * w, v * v * v};
  J historyGap;
  std::array<J, 3> p{};
  for (int j = 0; j < 4; ++j) {
    if (!std::isfinite(ns[j]->gap) || ns[j]->gap < 0 || ns[j]->gap > 1)
      throw std::invalid_argument("admissible history gap controls required");
    for (R value : ns[j]->direction)
      if (!std::isfinite(value) || !std::isfinite(double(value)))
        throw std::invalid_argument("finite history direction");
    historyGap = historyGap + basis[j] * J(double(ns[j]->gap));
    for (int a = 0; a < 3; ++a)
      p[a] = p[a] + basis[j] * J(double(ns[j]->direction[a]));
  }
  if (in.mu == 0 || in.kn == 0 ||
      (ns[0]->gap == 1 && ns[1]->gap == 1 && ns[2]->gap == 1 &&
       ns[3]->gap == 1))
    return out;
  J normalComponent;
  double originalLength2 = 0;
  for (auto value : p)
    originalLength2 += value.v * value.v;
  for (int a = 0; a < 3; ++a)
    normalComponent = normalComponent + p[a] * normal[a];
  for (int a = 0; a < 3; ++a)
    p[a] = p[a] - normal[a] * normalComponent;
  J length2;
  for (auto value : p)
    length2 = length2 + value * value;
  if (length2.v <= .25 * originalLength2 || originalLength2 == 0)
    throw std::domain_error("unresolved tangent-direction chart;refine "
                            "material cell rather than choose an axis");
  J inverseLength = regrip_beam::inverse(regrip_beam::root(length2));
  J amplitude =
      cap * J(1 / double(in.kt)) * (J(1) - historyGap) * inverseLength;
  for (int a = 0; a < 3; ++a)
    p[a] = p[a] * amplitude;
  out.elastic = unpack(p);
  return out;
}
} // namespace regrip_vector_history
