#include "../../models/film_rail_tendon/ControlProfile.h"
extern "C" double regripTransmissionTension(double time){
 return regrip_film_rail::ControlProfile::evaluate(time,.0001,.01,.05,.06,true).tension;
}
