#pragma once
#include "ExactInterval.h"
#include "OutwardPolynomial.h"
#include "VectorField.h"
namespace regrip_vector_history {
// Independent phase-preserving contrast:gap=1-|ke|/c is stored separately
// from direction. A yielded interval has gap EXACTLY0,not a noisy norm test.
// Fixed normal/parabolic positive capacity only. No moving3Dcontact claim.
class NormalizedSnapshot {
public:
  struct Node {
    R gap = 1;
    V direction{};
  };
  struct Cell {
    R lo, hi;
    Node left, right;
    bool phaseUncertain = false;
    Node control1, control2;
  };
  R k, C;
  V normal{0, 0, 1};
  std::vector<Cell> cells;
  R phaseUncertainWidth = 0;
  std::size_t queries = 0;
  static Node interpolate(const Cell &cell, R x) {
    if (cell.left.gap == 1 && cell.control1.gap == 1 &&
        cell.control2.gap == 1 && cell.right.gap == 1)
      return Node{};
    R u = (x - cell.lo) / (cell.hi - cell.lo);
    Node n;
    R w[4] = {(1 - u) * (1 - u) * (1 - u), 3 * u * (1 - u) * (1 - u),
              3 * u * u * (1 - u), u * u * u};
    const Node *nodes[4] = {&cell.left, &cell.control1, &cell.control2,
                            &cell.right};
    n.gap = 0;
    V p{};
    for (int j = 0; j < 4; ++j) {
      n.gap += w[j] * nodes[j]->gap;
      p = add(p, scale(nodes[j]->direction, w[j]));
    }
    if (n.gap == 1)
      return n;
    R length = norm(p);
    if (length < .5L)
      throw std::domain_error(
          "unresolved normalized direction;no fallback axis");
    n.direction = scale(p, 1 / length);
    return n;
  }
  V elastic(const Node &n, R x) const {
    return n.gap == 1 ? V{}
                      : scale(n.direction, C * (1 - x * x) / k * (1 - n.gap));
  }
  VectorField::MaterialValue at(R x) const {
    if (!std::isfinite(x) || x < -1 || x > 1)
      throw std::invalid_argument("normalized material coordinate");
    auto c =
        std::lower_bound(cells.begin(), cells.end(), x,
                         [](const Cell &cell, R p) { return cell.hi < p; });
    if (c == cells.end())
      throw std::logic_error("normalized partition");
    auto n = interpolate(*c, x);
    return {elastic(n, x), n.gap == 0 && std::abs(x) < 1, true, n.gap};
  }
  std::vector<R> knots() const {
    std::vector<R> r{-1};
    for (auto &c : cells)
      r.push_back(c.hi);
    return r;
  }
  R localBound(R lo, R hi) const {
    R bound = 0;
    auto begin = std::upper_bound(cells.begin(), cells.end(), lo,
                                  [](R p, const Cell &c) { return p < c.hi; });
    for (auto it = begin; it != cells.end() && it->lo < hi; ++it) {
      const auto &c = *it;
      R width = c.hi - c.lo;
      const Node *nodes[4] = {&c.left, &c.control1, &c.control2, &c.right};
      R gapDerivative = 0, directionDerivative = 0;
      for (int j = 1; j < 4; ++j) {
        gapDerivative =
            std::max(gapDerivative,
                     3 * std::abs(nodes[j]->gap - nodes[j - 1]->gap) / width);
        directionDerivative =
            std::max(directionDerivative,
                     3 *
                         norm(add(nodes[j]->direction,
                                  scale(nodes[j - 1]->direction, -1))) /
                         width);
      }
      bound = std::max(
          bound, 2 * C / k + C / k * (gapDerivative + 2 * directionDerivative));
    }
    return bound;
  }
  R lipschitzBound() const { return localBound(-1, 1); }
  const Cell &cellAt(R x) const {
    auto c = std::lower_bound(cells.begin(), cells.end(), x,
                              [](const Cell &c, R p) { return c.hi < p; });
    if (c == cells.end() || x < -1 || !std::isfinite(x))
      throw std::invalid_argument("normalized certificate coordinate");
    return *c;
  }
  int loadingSide(R x, V velocity) const {
    if (norm(velocity) == 0)
      return 0;
    const auto &c = cellAt(x);
    const Node *nodes[4] = {&c.left, &c.control1, &c.control2, &c.right};
    R a = INFINITY, b = -INFINITY, maxNorm = 0;
    for (auto n : nodes) {
      R d = dot(n->direction, velocity);
      a = std::min(a, d);
      b = std::max(b, d);
      maxNorm = std::max(maxNorm, norm(n->direction));
    }
    R epsilon = std::numeric_limits<R>::epsilon(),
      bound =
          16 * epsilon / (1 - 16 * epsilon) * (4 * maxNorm) * norm(velocity);
    if (std::min(a, b) > bound)
      return 1;
    if (std::max(a, b) < -bound)
      return -1;
    Q u = (binaryRational(x) - binaryRational(c.lo)) /
          (binaryRational(c.hi) - binaryRational(c.lo)),
      rate = 0;
    for (int j = 0; j < 3; ++j)
      rate +=
          ((1 - u) * (1 - u) * (1 - u) * binaryRational(c.left.direction[j]) +
           3 * u * (1 - u) * (1 - u) * binaryRational(c.control1.direction[j]) +
           3 * u * u * (1 - u) * binaryRational(c.control2.direction[j]) +
           u * u * u * binaryRational(c.right.direction[j])) *
          binaryRational(velocity[j]);
    return rate > 0 ? 1 : rate < 0 ? -1 : 0;
  }
  std::vector<R> tangentKnots(V velocity) const {
    auto result = knots();
    for (const auto &c : cells)
      if (c.left.gap == 0 && c.control1.gap == 0 && c.control2.gap == 0 &&
          c.right.gap == 0) {
        QP p(4);
        const Node *nodes[4] = {&c.left, &c.control1, &c.control2, &c.right};
        for (int axis = 0; axis < 3; ++axis) {
          QP q = power(binaryRational(nodes[0]->direction[axis]),
                       binaryRational(nodes[1]->direction[axis]),
                       binaryRational(nodes[2]->direction[axis]),
                       binaryRational(nodes[3]->direction[axis]));
          for (int j = 0; j < 4; ++j)
            p[j] += q[j] * binaryRational(velocity[axis]);
        }
        std::size_t visited = 0;
        auto split = [&](auto &&self, Q lo, Q hi) -> void {
          if (++visited > 200000)
            throw std::length_error("normalized tangent root budget");
          if (bernsteinSign(p, lo, hi) != PolynomialSign::Mixed)
            return;
          Q origin = binaryRational(c.lo),
            width = binaryRational(c.hi) - origin;
          if (width * (hi - lo) <= binaryRational(1e-12L)) {
            Q left = origin + width * lo, right = origin + width * hi;
            R l = left.convert_to<R>(), r = right.convert_to<R>();
            if (binaryRational(l) > left)
              l = std::nextafter(l, -INFINITY);
            if (binaryRational(r) < right)
              r = std::nextafter(r, INFINITY);
            result.push_back(l);
            result.push_back(r);
            return;
          }
          Q mid = (lo + hi) / 2;
          self(self, lo, mid);
          self(self, mid, hi);
        };
        split(split, 0, 1);
      }
    std::sort(result.begin(), result.end());
    result.erase(std::unique(result.begin(), result.end()), result.end());
    return result;
  }
  static QP power(Q a, Q b, Q c, Q d) {
    return {a, 3 * (b - a), 3 * (a - 2 * b + c), -a + 3 * b - 3 * c + d};
  }
  R stickRoundoffBound(const Step &step, R lo, R hi) const {
    if (step.capacity != C || step.increment[1] != V{} ||
        step.increment[2] != V{})
      return -1;
    if (!certificateKeyValid || certificateIncrement != step.increment[0]) {
      certificateMemo.clear();
      certificateIncrement = step.increment[0];
      certificateKeyValid = true;
    }
    auto key = std::make_pair(lo, hi);
    auto found = certificateMemo.find(key);
    if (found != certificateMemo.end())
      return found->second;
    R result = uncachedStickRoundoffBound(step, lo, hi);
    if (certificateMemo.size() < 65536)
      certificateMemo.emplace(key, result);
    return result;
  }
  mutable bool certificateKeyValid = false;
  mutable V certificateIncrement{};
  mutable std::map<std::pair<R, R>, R> certificateMemo;
  bool outwardPrefilter = false;
  bool outwardStick(const Step &step, R lo, R hi) const {
    if (!Outward::supported() || step.capacity != C ||
        step.increment[1] != V{} || step.increment[2] != V{} || lo <= -1 ||
        hi >= 1)
      return false;
    const auto &c = cellAt(lo);
    if (hi > c.hi)
      return false;
    try {
      Outward origin(c.lo), width = Outward(c.hi) - origin, kk(k), cc(C);
      OP cap{cc * (Outward(1) - origin * origin),
             Outward(-2) * cc * origin * width,
             Outward(0) - cc * width * width};
      OP rho = outwardPower(Outward(1) - Outward(c.left.gap),
                            Outward(1) - Outward(c.control1.gap),
                            Outward(1) - Outward(c.control2.gap),
                            Outward(1) - Outward(c.right.gap)),
         norm2(7), pd(4);
      Outward du2;
      for (int j = 0; j < 3; ++j) {
        OP p = outwardPower(c.left.direction[j], c.control1.direction[j],
                            c.control2.direction[j], c.right.direction[j]);
        Outward d(step.increment[0][j]);
        norm2 = outwardSum(norm2, outwardProduct(p, p), 1);
        for (int z = 0; z < 4; ++z)
          pd[z] = pd[z] + p[z] * d;
        du2 = du2 + d * d;
      }
      OP rm = outwardProduct(rho, rho);
      rm[0] = rm[0] - Outward(1);
      OP A = outwardProduct(outwardProduct(cap, cap), rm);
      A[0] = A[0] + kk * kk * du2;
      OP B = outwardProduct(outwardProduct(cap, rho), pd);
      for (auto &v : B)
        v = Outward(2) * kk * v;
      Outward l = (Outward(lo) - origin) / width,
              r = (Outward(hi) - origin) / width;
      bool an = outwardNegative(A, l, r), bn = outwardNegative(B, l, r);
      if (an && bn)
        return true;
      if (bn && outwardPositive(A, l, r))
        return outwardPositive(
            outwardSum(outwardProduct(B, B),
                       outwardProduct(outwardProduct(A, A), norm2), -1),
            l, r);
      if (an && outwardPositive(B, l, r))
        return outwardPositive(
            outwardSum(outwardProduct(outwardProduct(A, A), norm2),
                       outwardProduct(B, B), -1),
            l, r);
      return false;
    } catch (const std::exception &) {
      return false;
    }
  }
  R uncachedStickRoundoffBound(const Step &step, R lo, R hi) const {
    if (step.capacity != C || step.increment[1] != V{} ||
        step.increment[2] != V{} || lo <= -1 || hi >= 1)
      return -1;
    const auto &c = cellAt(lo);
    if (hi > c.hi)
      return -1;
    if (outwardPrefilter && outwardStick(step, lo, hi)) {
      R epsilon = std::numeric_limits<R>::epsilon(),
        gamma = 65536 * epsilon / (1 - 65536 * epsilon),
        capError = 64 * epsilon / (1 - 64 * epsilon) * C;
      return (C + capError) * gamma * (C / k + norm(step.increment[0]));
    }
    Q kq = binaryRational(k), Cq = binaryRational(C),
      origin = binaryRational(c.lo), width = binaryRational(c.hi) - origin;
    QP cap{Cq * (1 - origin * origin), -2 * Cq * origin * width,
           -Cq * width * width};
    QP rho = power(
           1 - binaryRational(c.left.gap), 1 - binaryRational(c.control1.gap),
           1 - binaryRational(c.control2.gap), 1 - binaryRational(c.right.gap)),
       norm2(7), pd(4);
    Q du2 = 0;
    for (int j = 0; j < 3; ++j) {
      QP p = power(binaryRational(c.left.direction[j]),
                   binaryRational(c.control1.direction[j]),
                   binaryRational(c.control2.direction[j]),
                   binaryRational(c.right.direction[j]));
      Q d = binaryRational(step.increment[0][j]);
      norm2 = sum(norm2, product(p, p), 1);
      for (int z = 0; z < 4; ++z)
        pd[z] += p[z] * d;
      du2 += d * d;
    }
    QP rhoMinus = product(rho, rho);
    rhoMinus[0] -= 1;
    QP A = product(product(cap, cap), rhoMinus);
    A[0] += kq * kq * du2;
    QP B = product(product(cap, rho), pd);
    for (auto &v : B)
      v *= 2 * kq;
    Q left = (binaryRational(lo) - origin) / width,
      right = (binaryRational(hi) - origin) / width;
    auto as = bernsteinSign(A, left, right), bs = bernsteinSign(B, left, right);
    bool stick = false;
    auto negative = [](PolynomialSign s) {
      return s == PolynomialSign::Nonpositive || s == PolynomialSign::Zero;
    };
    auto positive = [](PolynomialSign s) {
      return s == PolynomialSign::Nonnegative || s == PolynomialSign::Zero;
    };
    if (negative(as) && negative(bs))
      stick = true;
    else if (as == PolynomialSign::Nonnegative &&
             bs == PolynomialSign::Nonpositive) {
      auto squared = sum(product(B, B), product(product(A, A), norm2), -1);
      stick = positive(bernsteinSign(squared, left, right));
    } else if (as == PolynomialSign::Nonpositive &&
               bs == PolynomialSign::Nonnegative) {
      auto squared = sum(product(product(A, A), norm2), product(B, B), -1);
      stick = positive(bernsteinSign(squared, left, right));
    }
    if (!stick || std::fegetround() != FE_TONEAREST)
      return -1;
    R epsilon = std::numeric_limits<R>::epsilon(),
      gamma = 65536 * epsilon / (1 - 65536 * epsilon),
      capError = 64 * epsilon / (1 - 64 * epsilon) * C;
    // Unit interpolation has norm>=.5 by the constructor's cone guard.
    return (C + capError) * gamma * (C / k + norm(step.increment[0]));
  }
  NormalizedSnapshot(const std::function<VectorField::MaterialValue(R)> &source,
                     const std::function<V(R)> &endpointIncrement, R stiffness,
                     R capacity, R stateTolerance, const std::vector<V> &probes,
                     R lossDensityTolerance, bool zeroState = false,
                     V fixedNormal = {0, 0, 1})
      : k(stiffness), C(capacity), normal(fixedNormal) {
    radialReturn({}, {}, normal, k, C);
    if (C <= 0 || stateTolerance <= 0 || lossDensityTolerance <= 0)
      throw std::invalid_argument("normalized reference parameters");
    auto node = [&](R x) {
      if (++queries > 1000000)
        throw std::length_error("normalized source-query budget");
      Node n;
      if (zeroState)
        return n;
      if (x == -1 || x == 1) {
        V d = endpointIncrement(x);
        R length = norm(d);
        if (length == 0)
          throw std::domain_error(
              "undefined endpoint direction limit;no arbitrary axis");
        n.gap = 0;
        n.direction = scale(d, 1 / length);
        return n;
      }
      auto state = source(x);
      R length = norm(state.elastic), cap = C * (1 - x * x);
      if (length == 0)
        throw std::domain_error(
            "interior zero-direction event needs a separate chart");
      n.gap = state.onYield ? 0
                            : (state.gapKnown ? state.normalizedGap
                                              : (cap - k * length) / cap);
      if (n.gap < 0 || n.gap > 1)
        throw std::domain_error("nonadmissible source gap");
      n.direction = scale(state.elastic, 1 / length);
      return n;
    };
    auto build = [&](auto &&self, R lo, R hi, unsigned depth) -> void {
      Node l = node(lo), r = node(hi);
      bool transition = (l.gap == 0) != (r.gap == 0);
      if (transition && hi - lo > 1e-12L) {
        R a = lo, b = hi;
        bool leftYield = l.gap == 0;
        for (unsigned j = 0; j < 100 && b - a > 1e-12L; ++j) {
          R m = (a + b) / 2;
          if (m == a || m == b)
            break;
          if ((node(m).gap == 0) == leftYield)
            a = m;
          else
            b = m;
        }
        if (a > lo)
          self(self, lo, a, depth + 1);
        self(self, a, b, depth + 1);
        if (b < hi)
          self(self, b, hi, depth + 1);
        return;
      }
      Node n1 = node(lo + (hi - lo) / 3), n2 = node(lo + 2 * (hi - lo) / 3), b1,
           b2;
      auto controls = [](R a, R b, R c, R d) {
        R A = 27 * b - 8 * a - d, B = 27 * c - a - 8 * d;
        return std::array<R, 2>{(2 * A - B) / 18, (2 * B - A) / 18};
      };
      auto gaps = controls(l.gap, n1.gap, n2.gap, r.gap);
      b1.gap = gaps[0];
      b2.gap = gaps[1];
      if (b1.gap < 0 || b1.gap > 1 || b2.gap < 0 || b2.gap > 1) {
        b1.gap = (2 * l.gap + r.gap) / 3;
        b2.gap = (l.gap + 2 * r.gap) / 3;
      }
      for (int j = 0; j < 3; ++j) {
        auto ds = controls(l.direction[j], n1.direction[j], n2.direction[j],
                           r.direction[j]);
        b1.direction[j] = ds[0];
        b2.direction[j] = ds[1];
      }
      Cell cell{lo, hi, l, r, transition, b1, b2};
      // Convex Bezier controls certify gap admissibility and a common
      // direction hemisphere,so no clipping or invented direction is needed.
      bool accept =
          zeroState || (dot(l.direction, r.direction) >= .5L &&
                        dot(l.direction, b1.direction) >= .5L &&
                        dot(l.direction, b2.direction) >= .5L && b1.gap >= 0 &&
                        b1.gap <= 1 && b2.gap >= 0 && b2.gap <= 1);
      for (int j = 0; j < 13 && accept; ++j) {
        R x = lo + (hi - lo) * (R(j) + .5L) / 13;
        Node truth = node(x), fit = interpolate(cell, x);
        V actual = elastic(truth, x), approx = elastic(fit, x);
        if (norm(add(actual, scale(approx, -1))) > stateTolerance / 2)
          accept = false;
        if (!transition && (truth.gap == 0) != (fit.gap == 0))
          accept = false;
        for (V du : probes) {
          R cap = C * (1 - x * x);
          auto a = radialReturn(actual, du, normal, k, cap),
               b = radialReturn(approx, du, normal, k, cap);
          if (std::abs(a.loss - b.loss) > lossDensityTolerance)
            accept = false;
        }
      }
      if (accept) {
        if (cells.size() >= 8192)
          throw std::length_error("normalized cell budget");
        cells.push_back(cell);
        if (transition)
          phaseUncertainWidth += hi - lo;
        return;
      }
      R mid = (lo + hi) / 2;
      if (depth >= 60 || mid == lo || mid == hi) {
        std::ostringstream message;
        message.precision(20);
        message << "unresolved normalized phase/direction lo=" << lo
                << " hi=" << hi << " gaps=" << l.gap << ',' << b1.gap << ','
                << b2.gap << ',' << r.gap << " transition=" << transition;
        throw std::runtime_error(message.str());
      }
      self(self, lo, mid, depth + 1);
      self(self, mid, hi, depth + 1);
    };
    build(build, -1, 1, 0);
  }
  NormalizedSnapshot transformed(const M &Q) const {
    for (R q : Q)
      if (!std::isfinite(q))
        throw std::invalid_argument("finite proper rotation");
    auto multiply = [&](V v) {
      V r{};
      for (int i = 0; i < 3; ++i)
        for (int j = 0; j < 3; ++j)
          r[i] += Q[3 * i + j] * v[j];
      return r;
    };
    for (int i = 0; i < 3; ++i)
      for (int j = 0; j < 3; ++j) {
        R q = 0;
        for (int z = 0; z < 3; ++z)
          q += Q[3 * z + i] * Q[3 * z + j];
        if (std::abs(q - (i == j ? 1.L : 0.L)) >
            128 * std::numeric_limits<R>::epsilon())
          throw std::invalid_argument("orthonormal history frame required");
      }
    R determinant = Q[0] * (Q[4] * Q[8] - Q[5] * Q[7]) -
                    Q[1] * (Q[3] * Q[8] - Q[5] * Q[6]) +
                    Q[2] * (Q[3] * Q[7] - Q[4] * Q[6]);
    if (determinant <= 0)
      throw std::invalid_argument("history frame reflection forbidden");
    auto result = *this;
    result.normal = multiply(normal);
    result.certificateMemo.clear();
    result.certificateKeyValid = false;
    for (auto &c : result.cells) {
      c.left.direction = multiply(c.left.direction);
      c.control1.direction = multiply(c.control1.direction);
      c.control2.direction = multiply(c.control2.direction);
      c.right.direction = multiply(c.right.direction);
    }
    return result;
  }
};
} // namespace regrip_vector_history
