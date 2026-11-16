#include "../models/yield_front_history/SphereHistoryChart.h"
#include <iomanip>
#include <iostream>
using namespace regrip_vector_history;
int main() {
  try {
    SphereChartInput in;
    // The original1.005fixture was outside the intended active branch once
    // Hermite director sag was included;its FAILED campaign is preserved.
    // This independently prescribed fixture has positive gap throughout.
    in.left.p = {-.3, .98, -.025};
    in.right.p = {.3, .98, .025};
    in.left.q = regrip3d::exp({0, .2, .1});
    in.right.q = regrip3d::exp({.1, -.1, -.1});
    in.length = .6L;
    in.history.lo = -.4L;
    in.history.hi = .4L;
    in.history.left = {.1L, {0, 0, 1}};
    in.history.control1 = {.3L, {.1L, 0, 1}};
    in.history.control2 = {.2L, {-.1L, 0, 1}};
    in.history.right = {0, {0, 0, 1}};
    R first = 0, second = 0, normalError = 0, capacityError = 0,
      objectivity = 0, forceLimit = 0;
    unsigned count = 0;
    for (unsigned j = 0; j < 129; ++j) {
      R x = -.35L + .7L * (R(j) + .5L) / 129, h = 1e-5L;
      auto v = sphereHistoryChart(in, x), p = sphereHistoryChart(in, x + h),
           m = sphereHistoryChart(in, x - h);
      if (!v.active)
        throw std::runtime_error("manufactured active patch lost");
      for (int a = 0; a < 3; ++a) {
        first =
            std::max(first, std::abs((p.elastic.value[a] - m.elastic.value[a]) /
                                         (2 * h) -
                                     v.elastic.first[a]));
        second = std::max(
            second,
            std::abs((p.elastic.first[a] - m.elastic.first[a]) / (2 * h) -
                     v.elastic.second[a]));
      }
      normalError =
          std::max(normalError, std::abs(dot(v.elastic.value, v.normal.value)));
      capacityError =
          std::max(capacityError, std::abs((p.capacity - m.capacity) / (2 * h) -
                                           v.capacityFirst));
      forceLimit =
          std::max(forceLimit, in.kt * norm(v.elastic.value) - v.capacity);
      auto Q = regrip3d::exp({.8, -.3, .4});
      SphereChartInput moved = in;
      regrip3d::V shift{2, -1, .5};
      auto transform = [&](regrip3d::Pose pose) {
        pose.p = regrip3d::add(regrip3d::rotate(Q, pose.p), shift);
        pose.q = regrip3d::multiply(Q, pose.q);
        return pose;
      };
      moved.left = transform(in.left);
      moved.right = transform(in.right);
      for (int a = 0; a < 3; ++a)
        moved.center[a] = shift[a];
      NormalizedSnapshot::Node *ns[4] = {
          &moved.history.left, &moved.history.control1, &moved.history.control2,
          &moved.history.right};
      for (auto n : ns) {
        auto d = regrip3d::rotate(Q, {double(n->direction[0]),
                                      double(n->direction[1]),
                                      double(n->direction[2])});
        for (int a = 0; a < 3; ++a)
          n->direction[a] = d[a];
      }
      auto rotated = sphereHistoryChart(moved, x);
      auto expected = regrip3d::rotate(Q, {double(v.elastic.value[0]),
                                           double(v.elastic.value[1]),
                                           double(v.elastic.value[2])});
      for (int a = 0; a < 3; ++a)
        objectivity = std::max(
            objectivity, std::abs(rotated.elastic.value[a] - expected[a]));
      ++count;
    }
    auto inactive = in;
    inactive.left.p[1] += 1;
    inactive.right.p[1] += 1;
    if (sphereHistoryChart(inactive, 0).active)
      throw std::runtime_error("inactive patch invented contact");
    auto zero = in;
    zero.mu = 0;
    if (sphereHistoryChart(zero, 0).elastic.value != V{})
      throw std::runtime_error("zero friction invents elastic history");
    auto expectReject = [](const SphereChartInput &v, const char *reason) {
      bool rejected = false;
      try {
        sphereHistoryChart(v, 0);
      } catch (const std::exception &) {
        rejected = true;
      }
      if (!rejected)
        throw std::runtime_error(reason);
    };
    auto bad = in;
    bad.history.left.gap = std::numeric_limits<R>::quiet_NaN();
    expectReject(bad, "NaN gap accepted");
    auto pole = in;
    V n = sphereHistoryChart(in, 0).normal.value;
    pole.history.left.direction = n;
    pole.history.control1.direction = n;
    pole.history.control2.direction = n;
    pole.history.right.direction = n;
    expectReject(pole, "undefined tangent direction assigned an axis");
    auto boundary = in;
    boundary.left.p = {-.25, 1, 0};
    boundary.right.p = {.25, 1, 0};
    boundary.left.q = {0, 0, 0, 1};
    boundary.right.q = {0, 0, 0, 1};
    boundary.length = .5L;
    boundary.skin = 0;
    expectReject(boundary,
                 "contact event assigned an undeclared classical derivative");
    std::cout << std::setprecision(18) << "SPHERE_CHART {\"states\":" << count
              << ",\"first_FD\":" << first << ",\"second_FD\":" << second
              << ",\"normal_orthogonality\":" << normalError
              << ",\"capacity_first_FD\":" << capacityError
              << ",\"rigid_covariance\":" << objectivity
              << ",\"max_Coulomb_excess\":" << forceLimit << "}\n";
    if (first > 1e-10L || second > 1e-9L || normalError > 1e-16L ||
        capacityError > 1e-10L || objectivity > 1e-16L || forceLimit > 1e-16L)
      throw std::runtime_error("general sphere-history chart gate");
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
