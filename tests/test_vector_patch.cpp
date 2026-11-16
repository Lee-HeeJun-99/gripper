#include "../models/yield_front_history/VectorPatchBenchmark.cpp"
#include <iostream>
#include <sofa/component/statecontainer/MechanicalObject.h>
void require(bool b, const char *s) {
  if (!b)
    throw std::runtime_error(s);
}
template <class Parent> struct Accumulator : Parent {
  double a[3][3]{};
  void add(sofa::SignedIndex r, sofa::SignedIndex c, double v) override {
    a[r][c] += v;
  }
  void add(sofa::SignedIndex r, sofa::SignedIndex c, float v) override {
    add(r, c, double(v));
  }
};
int main(int argc, char **argv) {
  try {
    using F = VectorPatchBenchmark;
    using State = sofa::component::statecontainer::MechanicalObject<F::Types>;
    auto s = sofa::core::objectmodel::New<State>();
    s->resize(1);
    F::VecCoord x(1);
    s->write(sofa::core::vec_id::write_access::position)->setValue(x);
    auto f = sofa::core::objectmodel::New<F>(s.get());
    require(f->findData("capacity") == &f->capacity &&
                f->findData("velocityDirectedTangent") ==
                    &f->velocityDirectedTangent &&
                f->findData("compressionEvery") == &f->compressionEvery,
            "actual Data registration");
    require(f->capacity.read("0.000003") &&
                f->velocityDirectedTangent.read("1"),
            "actual Data parsing");
    if (argc == 2) {
      require(f->compressionEvery.read("1") &&
                  f->snapshotTolerance.read("0.00000000001"),
              "snapshot Data parsing");
    }
    f->prepare(x);
    if (argc == 2 && (std::string(argv[1]) == "normalized" ||
                      std::string(argv[1]) == "outward")) {
      require(f->normalizedRepresentation.read("1"), "normalized Data parsing");
      if (std::string(argv[1]) == "outward")
        require(f->outwardCertificates.read("1"), "outward Data parsing");
      f->prepare(x);
    }
    for (int i = 0; i < 5; ++i) {
      x[0][0] += .0002;
      x[0][1] += .00013;
      auto a = f->trial(x), b = f->trial(x);
      require(a.integral.v == b.integral.v && f->commits == unsigned(i),
              "pure SDK query");
      f->commit(x);
    }
    x[0][0] += .0003;
    x[0][1] -= .0001;
    s->write(sofa::core::vec_id::write_access::position)->setValue(x);
    auto base = f->trial(x);
    double fd = 0;
    for (int j = 0; j < 2; ++j) {
      auto p = x, m = x;
      p[0][j] += 1e-6;
      m[0][j] -= 1e-6;
      auto a = f->trial(p), b = f->trial(m);
      for (int i = 0; i < 2; ++i)
        fd = std::max(
            fd,
            std::abs(double((a.integral.v[5 + i] - b.integral.v[5 + i]) / 2e-6 -
                            base.integral.v[8 + 3 * i + j])));
    }
    require(fd < 1e-8, "actual reference API Jacobian FD");
    F::DataVecCoord pos;
    pos.setValue(x);
    F::DataVecDeriv force, velocity, dx, df;
    force.setValue(F::VecDeriv(1));
    velocity.setValue(F::VecDeriv(1));
    F::VecDeriv delta(1);
    delta[0] = {.3, -.4, .1};
    dx.setValue(delta);
    sofa::core::MechanicalParams mp;
    f->addForce(&mp, force, pos, velocity);
    for (int i = 0; i < 3; ++i)
      require(std::abs(force.getValue()[0][i] +
                       double(base.integral.v[5 + i])) < 1e-16,
              "SDK force");
    for (double factor : {0., 2.5, -.25}) {
      mp.setKFactor(factor);
      df.setValue(F::VecDeriv(1));
      f->addDForce(&mp, df, dx);
      for (int i = 0; i < 3; ++i) {
        double expected = 0;
        for (int j = 0; j < 3; ++j)
          expected -=
              factor * double(base.integral.v[8 + 3 * i + j]) * delta[0][j];
        require(std::abs(df.getValue()[0][i] - expected) < 1e-16, "SDK dforce");
      }
    }
    Accumulator<sofa::core::behavior::StiffnessMatrixAccumulator> acc;
    sofa::core::behavior::StiffnessMatrix matrix;
    matrix.setMatrixAccumulator(&acc, s.get());
    f->buildStiffnessMatrix(&matrix);
    for (int i = 0; i < 3; ++i)
      for (int j = 0; j < 3; ++j)
        require(std::abs(acc.a[i][j] + double(base.integral.v[8 + 3 * i + j])) <
                    1e-16,
                "SDK assembled matrix");
    auto epoch = f->field->epoch();
    auto e = f->getPotentialEnergy(&mp, pos);
    require(e >= 0 && f->field->epoch() == epoch, "energy query purity");
    require(f->trial(x).integral.v == f->uncachedTrial(x).integral.v,
            "same-pose query cache must be bitwise exact");
    auto rest = x;
    for (int j = 0; j < 3; ++j)
      rest[0][j] = f->previous[j];
    F::VecDeriv vel(1);
    vel[0] = {.001, .00065, 0};
    s->write(sofa::core::vec_id::write_access::velocity)->setValue(vel);
    auto loading = f->trial(rest);
    vel[0] *= -1;
    s->write(sofa::core::vec_id::write_access::velocity)->setValue(vel);
    auto unloading = f->trial(rest);
    double directedDifference = 0;
    for (int j = 8; j < 17; ++j)
      directedDifference = std::max(
          directedDifference,
          std::abs(double(loading.integral.v[j] - unloading.integral.v[j])));
    require(directedDifference > 0 &&
                loading.integral.v[5] == unloading.integral.v[5] &&
                loading.integral.v[2] == 0 && unloading.integral.v[2] == 0,
            "cache must honor direction without changing zero-increment "
            "forces/history");
    require(unloading.integral.v == f->uncachedTrial(rest).integral.v,
            "directed query exact cache");
    std::cout
        << std::setprecision(18) << "VECTOR_PATCH_API {\"fd_absolute\":" << fd
        << ",\"epoch\":" << epoch
        << ",\"directed_matrix_difference\":" << directedDifference
        << ",\"scope\":\"fixed-normal Vec3 benchmark,not collision/grasp\"}\n";
  } catch (const std::exception &e) {
    std::cerr << "FAIL " << e.what() << '\n';
    return 1;
  }
}
