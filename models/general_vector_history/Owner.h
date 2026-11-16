#pragma once
#include "../contact_birth/BirthLaw.h"
#include "../yield_front_history/SphereHistoryChart.h"
#include <functional>
#include <memory>
#include <optional>

namespace regrip_general_history {
using History = regrip_history::History;
using Pose = regrip3d::Pose;
using V = regrip3d::V;
// Exact, uncompressed functional reference. No quadrature index is a state ID.
// A finite replay budget is intentional: this is NOT the production adaptive
// fitter and cannot silently discard old operators on exhaustion.
class Owner {
public:
  using Field = std::function<History(double)>;
  using Geometry = std::function<Pose(double)>;
  struct Physics {
    unsigned shape = 0;
    double radius = 1, height = 5, skin = .02, kn = .001, kt = .001, mu = .3;
    bool operator==(const Physics &b)const{return shape==b.shape&&radius==b.radius&&height==b.height&&skin==b.skin&&kn==b.kn&&kt==b.kt&&mu==b.mu;}
  };
  struct Trial {
    std::size_t epoch;
    const Owner *owner;
    Field next;
    Physics physics;
  };
  explicit Owner(std::size_t budget = 128) : budget_(budget) {
    if (!budget) throw std::invalid_argument("positive replay budget");
  }
  History at(double s) const {
    if (!std::isfinite(s) || s < 0 || s > 1)
      throw std::invalid_argument("reference material coordinate outside [0,1]");
    return state_ ? state_(s) : History{};
  }
  Trial trial(Geometry before, Geometry after, Pose oldObject, Pose object,
              Physics p) const {
    if (epoch_ >= budget_)
      throw std::length_error("exact general history replay budget; fit or subdivide campaign");
    auto prior = state_;auto oldPhysics=physics_;
    return {epoch_, this, [prior, oldPhysics, before, after, oldObject, object, p](double s) {
      auto point0 = before(s);
      auto local0 = regrip3d::rotate(
          regrip3d::Q{-oldObject.q[0], -oldObject.q[1], -oldObject.q[2], oldObject.q[3]},
          regrip3d::sub(point0.p, oldObject.p));
      auto old = prior ? prior(s) : History{};
      auto current=after(s);
      auto local1=regrip3d::rotate(regrip3d::Q{-object.q[0],-object.q[1],-object.q[2],object.q[3]},regrip3d::sub(current.p,object.p));
      // Exact zero-increment identity, not a tolerance or small-loss cutoff.
      // Capacity/shape changes must still undergo the actual return map.
      if(old.active&&oldPhysics&&*oldPhysics==p&&local1==old.local)return old;
      return regrip_birthlaw::value(current, object, old, local0, p.shape,
          p.radius, p.height, p.skin, p.kn, p.kt, p.mu).next;
    },p};
  }
  void commit(const Trial &t) {
    if (t.owner != this || t.epoch != epoch_ || !t.next)
      throw std::invalid_argument("foreign/stale/repeated history commit");
    state_ = t.next;
    physics_=t.physics;
    ++epoch_;
  }
  std::size_t epoch() const { return epoch_; }
  // Optional immutable chart seed. The chart supplies material derivatives;
  // this reference owner only consumes values at FIXED material abscissae.
  // No claim of mechanical derivatives of a moving abscissa is made.
  void seedSphereChart(regrip_vector_history::SphereChartInput chart) {
    if (epoch_ || state_) throw std::invalid_argument("seed only before first commit");
    if (!(chart.kn > 0)) throw std::invalid_argument("chart seed requires positive kn");
    state_ = [chart](double s) {
      auto r = regrip_vector_history::sphereHistoryChart(chart, 2*s-1);
      History h;
      if (!r.active) return h;
      h.active = true;
      for (int j=0;j<3;++j) {
        h.normal[j] = double(r.normal.value[j]);
        h.elastic[j] = double(r.elastic.value[j]);
        h.local[j] = h.normal[j] * double(chart.radius+chart.skin-r.normalForce/chart.kn);
      }
      return h;
    };
  }
private:
  Field state_;
  std::size_t epoch_ = 0, budget_;
  std::optional<Physics> physics_;
};
} // namespace regrip_general_history
