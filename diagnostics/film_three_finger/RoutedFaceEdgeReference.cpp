#include "RoutedCheckpoint.h"
#include "../../models/film_three_finger_resume/FaceEdgeTransfer.h"
#include <iomanip>
#include <iostream>
using namespace regrip_routed_checkpoint;
int main(int argc,char**argv){try{
 if(argc!=3)throw std::runtime_error("actual checkpoint,exclusive result CSV required");SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;read(argv[1],s,q,v,time,h);
 auto r=regrip_three_resume::faceEdgeTransfer(s,q,v,time,h);
 if(std::ifstream(argv[2]))throw std::runtime_error("result exists");std::ofstream out(argv[2]);out<<std::setprecision(17)<<"state,time,q,v\n";
 for(unsigned i=0;i<2;++i){const auto&z=i?r.post:r.pre;out<<(i?"post":"event")<<','<<time+(i?h:r.eventH);for(const auto*x:{&z.q,&z.v}){out<<',';for(int j=0;j<x->size();++j)out<<(j?" ":"")<<(*x)[j];}out<<'\n';}
 std::cout<<std::setprecision(17)<<"{\"status\":\"PASS\",\"event_h_s\":"<<r.eventH<<",\"bracket_width_s\":"<<r.bracketWidth<<",\"minimum_gap_mm\":"<<r.minimumGap<<",\"minimum_face_parameter\":"<<r.minimumFaceParameter<<",\"minimum_independent_gap_mm\":"<<r.minimumIndependentGap<<",\"J_continuity_error\":"<<r.Jcontinuity<<",\"edge_normal_velocity_mm_s\":"<<r.edgeNormalVelocity<<",\"evaluations\":"<<r.evaluations<<"}\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
