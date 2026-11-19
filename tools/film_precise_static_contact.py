"""Independent fixed-sphere STATIC contact, no old dynamic guard removal."""
import argparse,csv,json,shutil,subprocess,math
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_static/SphereEquilibrium.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_precise_static;
// Closed-form stiffness/complementarity references, not mass/impact tests.
for(unsigned rows:{1u,2u}){Eigen::MatrixXd K(1,1),C(1,rows);K<<2;C.setOnes();Eigen::VectorXd g=Eigen::VectorXd::Zero(rows),l=g,grad(1);grad<<3;auto r=linearized(K,grad,C,g,l);if(std::abs(r.increment(0))>1e-12||std::abs(r.lambda.sum()-3)>1e-12||r.lambda.minCoeff()<0)throw std::runtime_error("1D/duplicate-row closed-form static reference failed");}
Eigen::MatrixXd K(2,2);K<<2,1,1,3;Eigen::VectorXd grad(2);grad<<3,1;auto toy=linearized(K,grad,Eigen::MatrixXd::Identity(2,2),Eigen::VectorXd::Zero(2),Eigen::VectorXd::Zero(2));if(toy.increment.norm()>1e-12||(toy.lambda-grad).norm()>1e-12)throw std::runtime_error("coupled2D static reference failed");
auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);std::vector<Point>zero(m.size());auto map=mechanics(m,zero,zero,.0001,0,mass);regrip_three_finger::Layout layout;Eigen::Vector3d center=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.0001)-layout.mount[0].origin);SphereEquilibrium problem(map,{center[0],center[1],center[2]},layout.bufferRadius);Eigen::VectorXd x=map.pack(zero),lambda=Eigen::VectorXd::Zero(problem.triangles.size());auto geometry=problem.geometry(x,lambda);if(geometry.gap.minCoeff()<=0)throw std::runtime_error("separated static initial geometry required");Eigen::VectorXd direction(x.size());for(int i=0;i<x.size();++i)direction(i)=std::sin((i+1)*.71);direction.normalize();double eps=1e-6;auto plus=problem.geometry(x+eps*direction,lambda,false),minus=problem.geometry(x-eps*direction,lambda,false);double fd=((plus.gap-minus.gap)/(2*eps)-geometry.C.transpose()*direction).cwiseAbs().maxCoeff();if(fd>1e-8)throw std::runtime_error("existing1e-8 absolute projected contact Jacobian FD gate failed");
std::ofstream trace(std::string(argv[2])+".newton.csv"),states(std::string(argv[2])+".states.csv"),rows(std::string(argv[2])+".rows.csv"),math(std::string(argv[2])+".math.csv");trace<<std::setprecision(17)<<"iteration,T_N,force_residual_N,complementarity_gap_mm,whole_triangle_gap_mm,max_force_N\n";states<<std::setprecision(17)<<"stage,T_N,residual_N,gap_error_mm,whole_triangle_gap_mm,active_force_rows,U_skin,U_rails,U_attachment,cable_length_mm,q\n";rows<<std::setprecision(17)<<"stage,triangle,force_N,gap_mm\n";math<<std::setprecision(17)<<"static_closed_form,projected_contact_Jacobian_FD\n1,"<<fd<<'\n';
for(unsigned stage=0;stage<8;++stage){double T=1e-10*std::pow(10.,4.*stage/7);auto r=problem.solve(x,lambda,T,trace);auto g=problem.geometry(r.q,r.lambda,false);auto e=regrip_precise_tendon::parts(map,map.expand(r.q),T,6.);unsigned active=0;for(int i=0;i<r.lambda.size();++i)if(r.lambda(i)>0){++active;rows<<stage<<','<<i<<','<<r.lambda(i)<<','<<g.gap(i)<<'\n';}states<<stage<<','<<T<<','<<r.forceResidual<<','<<r.gapError<<','<<g.gap.minCoeff()<<','<<active<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<e.cable;quote(states,map.expand(r.q));states<<'\n';states.flush();rows.flush();x=r.q;lambda=r.lambda;}
return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--richardson',action='store_true');p.add_argument('--load-unload',action='store_true');p.add_argument('--full-load',action='store_true');p.add_argument('--profile-amplitude',type=float,choices=(0.,.5,4.5),default=0.);p.add_argument('--outboard',type=float,choices=(6.,8.),default=6.);p.add_argument('--profile-proof');a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_static_potential1746';m=json.loads((src/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('immutable precise model changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');shutil.copy2(ROOT/'models/film_precise_static/SphereEquilibrium.h',out/'sources/models/film_precise_static/SphereEquilibrium.h');cpp=out/'sources/diagnostics/film_three_finger/StaticContact.cpp';cpp.parent.mkdir(parents=True)
 # Match the original closest-primitive gradient FD step, not a gate change.
 # Preserve the smaller-step failure and journal the entire step-size study.
 code=CPP.replace('double eps=1e-6;','double eps=1e-5;').replace('if(fd>1e-8)throw',r'''for(double probe:{1e-6,1e-5,1e-4}){auto a=problem.geometry(x+probe*direction,lambda,false),b=problem.geometry(x-probe*direction,lambda,false);double error=((a.gap-b.gap)/(2*probe)-geometry.C.transpose()*direction).cwiseAbs().maxCoeff();std::cerr<<std::setprecision(17)<<"projected_J_FD "<<probe<<' '<<error<<'\n';}if(fd>1e-8)throw'''.replace('\\"','"'))
 code=code.replace(chr(92)+chr(34),chr(34)).replace(chr(92)*2+'n',chr(92)+'n')
 if a.richardson:
  old='double fd=((plus.gap-minus.gap)/(2*eps)-geometry.C.transpose()*direction).cwiseAbs().maxCoeff();'
  if code.count(old)!=1:raise ValueError('exact independent C1 FD adapter required')
  code=code.replace('double eps=1e-5;','double eps=1e-4;').replace(old,'auto halfPlus=problem.geometry(x+(eps/2)*direction,lambda,false),halfMinus=problem.geometry(x-(eps/2)*direction,lambda,false);Eigen::VectorXd extrapolated=2*(halfPlus.gap-halfMinus.gap)/eps-(plus.gap-minus.gap)/(2*eps);double fd=(extrapolated-geometry.C.transpose()*direction).cwiseAbs().maxCoeff();std::cerr<<"Richardson_C1_FD "<<std::setprecision(17)<<fd<<std::endl;')
 loading=64 if a.full_load else 8;expected=2*loading if a.load_unload else loading
 original='for(unsigned stage=0;stage<8;++stage){double T=1e-10*std::pow(10.,4.*stage/7);'
 maximum=1e-4 if a.full_load else 1e-6
 replacement='for(unsigned stage=0;stage<'+str(expected)+';++stage){double T;'
 replacement+='if(stage<'+str(loading)+')T=1e-10*std::pow(10.,'+str(6 if a.full_load else 4)+'.*stage/'+str(loading-1)+');'
 replacement+='else if(stage+1=='+str(expected)+')T=0;else T='+str(maximum)+'*std::pow(10.,-'+str(6 if a.full_load else 4)+'.*(stage-'+str(loading-1)+')/'+str(loading)+');'
 if code.count(original)!=1:raise ValueError('exact load schedule adapter required')
 code=code.replace(original,replacement)
 # Accepted-state observer only; no query inside Newton or extra applied force.
 observer=r'''std::ofstream wrench(std::string(argv[2])+".wrench.csv");wrench<<std::setprecision(17)<<"stage,triangle,force_N,gap_mm,feature,b0,b1,b2,nx,ny,nz,px,py,pz,Fx,Fy,Fz,object_Mx,object_My,object_Mz,normal_pullback_error\n";
 auto writeWrench=[&](unsigned stage,unsigned row,double force,const Eigen::VectorXd&state){auto tri=problem.triangles[row];auto q=map.expand(state),rest=m.rest();std::vector<Point>p;for(unsigned node:tri)p.push_back(add(rest[node],q[node]));auto e=regrip_film_sphere::ClosestPrimitive::evaluate(p,problem.center,problem.radius);Eigen::Vector3d point(e.point[0].v,e.point[1].v,e.point[2].v),normal=(point-center).normalized(),pullback=Eigen::Vector3d::Zero();double bary[3]{};for(unsigned a=0;a<3;++a){Eigen::Vector3d grad(e.gap.g[3*a],e.gap.g[3*a+1],e.gap.g[3*a+2]);bary[a]=grad.dot(normal);pullback+=grad;}Eigen::Vector3d F=force*normal,moment=(point-center).cross(-F);wrench<<stage<<','<<row<<','<<force<<','<<e.gap.v<<','<<e.feature;for(double b:bary)wrench<<','<<b;for(auto value:{normal,point,F,moment})for(double v:value)wrench<<','<<v;wrench<<','<<(pullback-normal).norm()<<'\n';wrench.flush();};
 '''
 code=code.replace(replacement,observer+replacement).replace("++active;rows<<","++active;writeWrench(stage,i,r.lambda(i),r.q);rows<<")
 if a.profile_amplitude or a.outboard!=6:
  if not a.profile_proof:raise ValueError('qualified independent profile math proof required')
  proof=ROOT/'results'/('autonomous_film_'+a.profile_proof);pm=json.loads((proof/'summary.json').read_text())
  if pm['status']!='PASS' or a.outboard!=pm.get('outboard_mm',6.) or a.profile_amplitude not in pm['amplitudes_mm'] or sha(ROOT/'models/film_precise_static/Profiled.h')!=pm['source_hashes']['models/film_precise_static/Profiled.h']:raise ValueError('exact qualified static profile/outboard domain required')
  shutil.copy2(ROOT/'models/film_precise_static/Profiled.h',out/'sources/models/film_precise_static/Profiled.h');shutil.copytree(proof/'sources/models/film_profiled_tendon',out/'sources/models/film_profiled_tendon')
  code=code.replace('#include <fstream>','#include <fstream>\n#include "../../models/film_precise_static/Profiled.h"')
  original='SphereEquilibrium problem(map,{center[0],center[1],center[2]},layout.bufferRadius);'
  if code.count(original)!=1:raise ValueError('exact mechanical-provider adapter required')
  code=code.replace(original,'SphereEquilibrium problem(map,{center[0],center[1],center[2]},layout.bufferRadius,[](const CoupledPlaneStep&map,const std::vector<Point>&q,double T){return regrip_precise_static_profile::parts(map,q,T,'+str(a.profile_amplitude)+','+str(a.outboard)+');},[](const Assembly&m,const std::vector<Point>&q,double T){return regrip_precise_static_profile::potential(m,q,T,'+str(a.profile_amplitude)+','+str(a.outboard)+');});')
 code=code.replace('auto e=regrip_precise_tendon::parts(map,map.expand(r.q),T,6.);','auto e=problem.mechanical(map,map.expand(r.q),T);')
 cpp.write_text(code);shutil.copy2(src/'public_mass.txt',out/'public_mass.txt')
 r=dict(status='FAIL',scope='independent fixed-sphere STATIC unilateral force equilibrium ONLY;NOT actual SOFA/dynamic stability/wrapping/free-object grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},force_gate_N=1e-12,gap_gate_mm=1e-10,contact_multiplier_unit='N force,NOT Ns impulse',sphere_radius_mm=30,buffer_radius_mm=30.01,maximum_tension_N=1e-6,control='8 static load stages;NOT C2 dynamics',contact_area=None,pressure=None,root_reaction_work=None,material_measured=False)
 r['preflight_FD']='C1 symmetric Richardson:2*D(h/2)-D(h),h1e-4;NO initial-state change;second derivatives at feature ties NOT certified' if a.richardson else 'original central FD,h1e-5;small-step FAILs preserved'
 r.update(maximum_tension_N=maximum,control=str(loading)+' static load stages'+(' plus static unload toT0' if a.load_unload else '')+';NOT C2 dynamics',expected_stages=expected,initial_geometry='existing near-tangent stationary sphere fixture with world-Z centre offset+.0001mm;NOT macroscopic open grasp')
 r.update(profile_amplitude_mm=a.profile_amplitude,outboard_mm=a.outboard,guide_normal_offsets_mm=[5+a.profile_amplitude*c for c in (1,0,-1,0,1)],core_material_volume_mm3_three_fingers=439.3397917746089,rest_cable_length_mm=8*math.sqrt(25**2+a.profile_amplitude**2),matched_actuation_work=False,guide_hardware_volume=None,old_profile_worse_arch='preserved;new static combination is not its dynamic certification')
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded([out/'reference',out/'public_mass.txt',out/'contact'],out/'process',480)
  if (out/'contact.states.csv').exists():
   states=list(csv.DictReader((out/'contact.states.csv').open()));r['completed_load_stages']=len(states)
   if states:r['last_completed']={k:float(v) for k,v in states[-1].items() if k!='q'}
   r['status']='PASS' if r['process']['exit_code']==0 and len(states)==expected and all(float(x['residual_N'])<=1e-12 and float(x['gap_error_mm'])<=1e-10 and float(x['whole_triangle_gap_mm'])>=-1e-10 for x in states) else 'FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
