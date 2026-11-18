#pragma once
#include "../film_transmission/Kernel.h"
namespace regrip_rail_aspect {
// One physical design factor:rail aspect ratio at fixed core cross-sectional
// area. Baseline is returned untouched. Not a stiffness multiplier or jamming.
inline regrip_film_rail::Assembly design(double thickness){
 auto m=regrip_transmission::model();if(thickness==.1)return m;
 if(thickness!=.075&&thickness!=.125)throw std::invalid_argument("declared75/100/125um rail design only");
 double area=m.railW*m.railT;m.railT=thickness;m.railW=area/thickness;
 if(!(m.railW>0&&2*m.railW<m.W))throw std::runtime_error("finite separated rail widths required");
 m.parts={{0,m.nx,5,m.W,m.skinT,0,0},{5*m.nx,m.nx,3,m.railW,m.railT,0,-(m.skinT+m.railT)/2},{8*m.nx,m.nx,3,m.railW,m.railT,m.W-m.railW,-(m.skinT+m.railT)/2}};
 if(std::abs(3*m.volume()-439.3397917746089)>1e-12)throw std::runtime_error("same three-finger core volume required");return m;
}
}
