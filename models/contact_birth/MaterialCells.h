#pragma once
#include <cmath>
#include <limits>
#include <algorithm>
#include <stdexcept>
namespace regrip_birth {
// A discrete identifier must not jump by one under an ULP-scale rigid transform.
// Only near-INTEGER ratios are canonicalized; no force denominator or physical
// convergence threshold is regularized. Other ratios retain strict ceil.
inline unsigned materialCells(double length,double spacing){
 if(!std::isfinite(length)||!std::isfinite(spacing)||length<=0||spacing<=0)throw std::invalid_argument("material cell dimensions");
 double ratio=length/spacing,nearest=std::round(ratio);if(ratio>1000000)throw std::invalid_argument("material cell bound");double representationBound=32*std::numeric_limits<double>::epsilon()*std::max(1.,std::abs(ratio));
 return unsigned(nearest>=1&&std::abs(ratio-nearest)<=representationBound?nearest:std::ceil(ratio));
}
}
