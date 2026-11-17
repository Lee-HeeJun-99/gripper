#pragma once
#include "ProjectedImpact.h"
#include "../film_native_contact/CoupledPlaneStep.h"
namespace regrip_film_impact {
// Same B used by the actual film mechanical kernel, including .25 root slaves.
// No stiffness, damping, dt or BDF multiplier enters an instantaneous mass law.
inline Eigen::MatrixXd filmMass(const regrip_film_native::CoupledPlaneStep&mechanics){
 Eigen::MatrixXd M=Eigen::MatrixXd::Zero(mechanics.freeSize,mechanics.freeSize);
 for(unsigned a=0;a<mechanics.index.size();++a){int i=mechanics.index[a];
  double mass=mechanics.mass.at(a/3),weight=mechanics.weight[a];
  if(!(mass>0)||!std::isfinite(mass))throw std::invalid_argument("film impact nodal mass");
  if(i>=0)M(i,i)+=weight*weight*mass;
 }return M;
}
inline Eigen::RowVectorXd filmRow(const regrip_film_native::CoupledPlaneStep&mechanics,
 const std::vector<regrip_film_rail::Point>&nodalGradient){
 if(nodalGradient.size()!=mechanics.model.size())throw std::invalid_argument("film impact Jacobian size");
 Eigen::RowVectorXd row=Eigen::RowVectorXd::Zero(mechanics.freeSize);
 for(unsigned a=0;a<mechanics.index.size();++a)if(mechanics.index[a]>=0)
  row(mechanics.index[a])+=mechanics.weight[a]*nodalGradient[a/3][a%3];
 return row;
}
}
