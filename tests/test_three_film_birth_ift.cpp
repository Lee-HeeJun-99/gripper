#include "../models/film_three_finger_event/BracketedBirth.h"
#include <iostream>
#include <iomanip>
using namespace regrip_three_event;
int main(){try{
 SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;auto q=s.initial;unsigned body=3*s.shared.nf;q.segment<3>(body)+=Eigen::Vector3d(.0003,.00023,.002);Eigen::VectorXd v=Eigen::VectorXd::Zero(q.size());v(body+2)=-10;EventControl c{.0001,.01,.02,.03,true};
 auto event=bracketedBirth(s,q,v,0,.00005,.0002,c);double eps=1e-6;auto qp=q,qm=q;qp(body+2)+=eps;qm(body+2)-=eps;auto plus=bracketedBirth(s,qp,v,0,.00005,.0002,c),minus=bracketedBirth(s,qm,v,0,.00005,.0002,c);
 if(event.rows.size()!=1||plus.rows.size()!=1||minus.rows.size()!=1||event.rows[0].finger!=plus.rows[0].finger||event.rows[0].finger!=minus.rows[0].finger||event.rows[0].feature!=plus.rows[0].feature||event.rows[0].feature!=minus.rows[0].feature||event.rows[0].triangle!=plus.rows[0].triangle||event.rows[0].triangle!=minus.rows[0].triangle)throw std::domain_error("IFT requires same unique smooth entering branch;no derivative assigned to simultaneous minima");
 // Before contact films do not depend on sphere translation. The body force,
 // mass and velocity are independent of its initial z. Thus dq(h)/dz0=e_z.
 double denominator=event.J.row(0).dot(event.before.positionFamilyRate);if(!(denominator<0))throw std::domain_error("non-transverse event;no epsilon denominator");double analytic=-event.J(0,body+2)/denominator,fd=(plus.time-minus.time)/(2*eps),relative=std::abs(analytic-fd)/std::abs(analytic);
 std::cout<<std::setprecision(17)<<"analytic_s_per_mm="<<analytic<<" FD_s_per_mm="<<fd<<" relative="<<relative<<" rows="<<event.rows.size()<<" finger="<<event.rows[0].finger<<" triangle="<<event.rows[0].triangle<<" feature="<<event.rows[0].feature<<'\n';if(relative>1e-6)throw std::runtime_error("event-time IFT FD gate1e-6");std::cout<<"PASS unique-branch initial-body-z event-time IFT;NOT simultaneous/minimum derivative,full tangent or SOFA sensitivity\n";
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
