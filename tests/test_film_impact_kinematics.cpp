#include <cmath>
#include <iostream>
#include <stdexcept>
// Independent 1D fixed-plane counterexample, NOT a replacement impact law.
int main(){try{
 const double h=.001,m=1,incoming=-1;
 unsigned rebound=0,inward=0;
 for(double alpha:{.05,.2,.5,.9}){
  double previousGap=alpha*h,olderGap=previousGap-h*incoming,acceptedGap=0;
  double acceptedVelocity=(3*acceptedGap-4*previousGap+olderGap)/(2*h);
  double expected=(1-3*alpha)/2;
  if(std::abs(acceptedVelocity-expected)>1e-14)throw std::runtime_error("BDF position identity");
  double impulse=m*(3*acceptedVelocity-4*incoming+incoming)/2;
  if(impulse<0||acceptedGap!=0)throw std::runtime_error("unilateral endpoint consistency");
  rebound+=acceptedVelocity>0;inward+=acceptedVelocity<0;
  // An explicit perfectly inelastic instantaneous reference instead has
  // v+=0, I=-m*v-, D=.5*m*v-^2. It is a MODEL ASSUMPTION, not our SOFA law.
  std::cout<<"alpha "<<alpha<<" gap "<<acceptedGap<<" normal_velocity "<<acceptedVelocity<<" BDF_impulse "<<impulse<<" plastic_impact_reference_impulse "<<-m*incoming<<'\n';
 }
 if(!rebound||!inward)throw std::runtime_error("counterexample did not expose both branches");
 std::cout<<"PASS independent counterexample:position complementarity alone is NOT an instantaneous impact law;NOT an integrated remedy\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
