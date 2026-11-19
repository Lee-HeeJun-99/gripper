"""Fresh deformed-state Lagrangian force/Jacobian consistency, no state update."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_static/SphereEquilibrium.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include <fstream>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_precise_static;
 auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);std::vector<Point>q(m.size()),zero(m.size());double T;std::ifstream input(argv[2]);input>>T;for(auto&p:q)for(double&v:p)input>>v;auto map=mechanics(m,zero,zero,.0001,0,mass);regrip_three_finger::Layout layout;Eigen::Vector3d c=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.2)-layout.mount[0].origin);SphereEquilibrium problem(map,{c[0],c[1],c[2]},layout.bufferRadius);problem.setThicknessEnvelope();Eigen::VectorXd lambda(problem.triangles.size());for(double&v:lambda)input>>v;if(!input||lambda.minCoeff()<0)throw std::runtime_error("complete owned static seed required");auto x=map.pack(q);if(map.expand(x)!=q)throw std::runtime_error("exact root map required");auto e=problem.mechanical(map,q,T);auto g=problem.geometry(x,lambda);Eigen::MatrixXd H=e.stiffness-g.H;Eigen::VectorXd d(x.size());for(int i=0;i<d.size();++i)d(i)=std::sin(.71*(i+1));d.normalize();double worst=0;
 auto feature=[&](const Eigen::VectorXd&z,unsigned row){auto p=m.rest(),u=map.expand(z);for(unsigned i=0;i<p.size();++i)p[i]=add(p[i],u[i]);auto tri=problem.triangles[row];return regrip_film_sphere::ClosestPrimitive::evaluate({p[tri[0]],p[tri[1]],p[tri[2]]},problem.center,problem.rowRadius(row)).feature;};
 for(double h:{1e-4,1e-5,1e-6}){Eigen::VectorXd xp=x+h*d,xm=x-h*d;for(unsigned row=0;row<lambda.size();++row)if(lambda(row)>0&&(feature(xp,row)!=feature(x,row)||feature(xm,row)!=feature(x,row)))throw std::runtime_error("active feature transition:classical Hessian FD undefined;NOT certified");auto gp=problem.geometry(xp,lambda,false),gm=problem.geometry(xm,lambda,false);Eigen::VectorXd rp=-problem.mechanical(map,map.expand(xp),T).force-gp.C*lambda,rm=-problem.mechanical(map,map.expand(xm),T).force-gm.C*lambda;double error=((rp-rm)/(2*h)-H*d).norm()/(H*d).norm();worst=std::max(worst,error);std::cerr<<h<<','<<error<<'\n';}
 double residual=(-e.force-g.C*lambda).norm(),asym=(H-H.transpose()).norm()/H.norm();if(worst>1e-5||asym>1e-12||residual>1e-12||g.gap.minCoeff()<-1e-10)throw std::runtime_error("unchanged static force/tangent/geometry gates failed");std::cout.precision(17);std::cout<<"{\"status\":\"PASS\",\"force_residual_N\":"<<residual<<",\"worst_Lagrangian_H_direction_FD_relative\":"<<worst<<",\"H_asymmetry_relative\":"<<asym<<"}\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or not m['thickness_envelope']:raise ValueError('qualified static envelope state required')
 for key in ('source_hashes','raw_hashes'):
  for f,d in m[key].items():
   if sha(src/('sources' if key=='source_hashes' else '')/f)!=d:raise ValueError('immutable source/raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/ThicknessTangent.cpp';cpp.parent.mkdir(parents=True);code=CPP
 if m['profile_amplitude_mm'] or m['outboard_mm']!=6:
  code=code.replace('#include <fstream>','#include <fstream>\n#include "../../models/film_precise_static/Profiled.h"');code=code.replace('problem.setThicknessEnvelope();','problem.mechanical=[](const CoupledPlaneStep&map,const std::vector<Point>&q,double T){return regrip_precise_static_profile::parts(map,q,T,'+str(m['profile_amplitude_mm'])+','+str(m['outboard_mm'])+');};problem.setThicknessEnvelope();')
 cpp.write_text(code);shutil.copy2(src/'public_mass.txt',out/'public_mass.txt');rows=list(csv.DictReader((src/'contact.states.csv').open()));last=rows[-1];lam=['0']*320
 for row in csv.DictReader((src/'contact.rows.csv').open()):
  if row['stage']==last['stage']:lam[int(row['triangle'])]=row['force_N']
 (out/'seed.txt').write_text(last['T_N']+' '+last['q']+' '+' '.join(lam)+'\n');r=dict(status='FAIL',scope='fresh deformed static Lagrangian tangent on smooth active branch ONLY;NOT dynamic/mesh/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},seed_sha256=sha(out/'seed.txt'))
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded([out/'reference',out/'public_mass.txt',out/'seed.txt'],out/'process',120)
  if r['process']['exit_code']==0:r['metrics']=json.loads((out/'process/stdout.log').read_text());r['status']=r['metrics']['status']
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='source_hashes'}))
if __name__=='__main__':main()
