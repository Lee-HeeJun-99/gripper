"""Fresh force/FD and whole-triangle VIRTUAL sphere overlay of free static states."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_tendon/Force.h"
#include "../../models/film_precise_static/Potential.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitiveValue.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[2]);std::ifstream in(argv[1]);unsigned count;in>>count;regrip_three_finger::Layout layout;Eigen::Vector3d center=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.0001)-layout.mount[0].origin);Point C{center[0],center[1],center[2]};std::cout<<std::setprecision(17)<<"stage,T,force_residual_N,virtual_buffer_gap_mm,virtual_actual_radius_gap_mm,overlapping_triangles,force_FD_N,Hessian_FD_N_mm\n";
for(unsigned sample=0;sample<count;++sample){unsigned stage;double T;std::vector<Point>q(m.size()),zero(m.size());in>>stage>>T;for(auto&p:q)for(double&x:p)in>>x;if(!in)throw std::runtime_error("complete static state required");auto map=mechanics(m,q,zero,.0001,T,mass);auto e=regrip_precise_tendon::parts(map,q,T,6.);auto rest=m.rest();for(unsigned i=0;i<q.size();++i)rest[i]=add(rest[i],q[i]);double gap=1e99,actualGap=1e99;unsigned overlap=0;
for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<m.nx;++i)for(unsigned j=0;j+1<m.parts[part].ny;++j){unsigned a=m.id(part,i,j),b=m.id(part,i+1,j),c=m.id(part,i,j+1),d=m.id(part,i+1,j+1);for(auto tri:{std::array<unsigned,3>{a,b,c},std::array<unsigned,3>{b,d,c}}){std::vector<Point>points{rest[tri[0]],rest[tri[1]],rest[tri[2]]};double g=regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(points,C,layout.bufferRadius).gap.v;gap=std::min(gap,g);actualGap=std::min(actualGap,regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(points,C,layout.bodyRadius).gap.v);if(g<0)++overlap;}}
double fFD=0,hFD=0;if(sample+1==count){auto x=map.pack(q);for(unsigned full:{3*m.id(0,5,0)+2,3*m.id(1,5,0)+2,3*m.id(2,10,2)}){int j=map.index[full];if(j<0)throw std::runtime_error("explicit FD free coordinate required");auto xp=x,xm=x;double h=1e-6;xp(j)+=h;xm(j)-=h;auto qp=map.expand(xp),qm=map.expand(xm);auto plus=regrip_precise_tendon::parts(map,qp,T,6.),minus=regrip_precise_tendon::parts(map,qm,T,6.);double up=plus.skin+plus.rails+plus.bond+regrip_precise_static::tendonPotential(m,qp,T,6.),um=minus.skin+minus.rails+minus.bond+regrip_precise_static::tendonPotential(m,qm,T,6.);fFD=std::max(fFD,std::abs(-(up-um)/(2*h)-e.force(j)));hFD=std::max(hFD,((plus.force-minus.force)/(2*h)+e.stiffness.col(j)).cwiseAbs().maxCoeff());}}
std::cout<<stage<<','<<T<<','<<e.force.norm()<<','<<gap<<','<<actualGap<<','<<overlap<<','<<fFD<<','<<hFD<<'\n';}return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_static_potential1746';m=json.loads((src/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('compiled static sources changed')
 raw=src/'0.1/equilibrium.states.csv'
 if sha(raw)!=m['raw_hashes']['0.1/equilibrium.states.csv']:raise ValueError('immutable completed partial states changed')
 rows=list(csv.DictReader(raw.open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/StaticGeometry.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP);(out/'states.txt').write_text(str(len(rows))+'\n'+'\n'.join(' '.join((x['stage'],x['T'],x['q'])) for x in rows)+'\n');shutil.copy2(src/'public_mass.txt',out/'public_mass.txt')
 r=dict(status='FAIL',scope='fresh independent FREE static force/FD and VIRTUAL triangle/sphere overlay ONLY;NOT actual contact/wrapping/holding/actual SOFA',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},full_load_status='FAIL preserved',contact_area=None,pressure=None,holding_capacity=None,root_reaction_work=None)
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded([out/'reference',out/'states.txt',out/'public_mass.txt'],out/'process',180)
  if r['process']['exit_code']==0:
   values=list(csv.DictReader((out/'process/stdout.log').open()));last={k:float(v) for k,v in values[-1].items()};force=max(float(x['force_residual_N']) for x in values);r.update(status='ANALYZED_FREE_OVERLAY',fresh_force_gate='PASS' if force<=1e-12 else 'FAIL',maximum_force_residual_N=force,endpoint_original_coordinate_FD_gates='PASS' if last['force_FD_N']<=1e-8 and last['Hessian_FD_N_mm']<=1e-5 else 'FAIL',endpoint=last,virtual_contact_admissibility='FAIL' if last['virtual_buffer_gap_mm']< -1e-10 else 'CLEAR_VIRTUAL_OVERLAY_ONLY',actual_contact_solve='NOT RUN')
   shutil.copy2(out/'process/stdout.log',out/'geometry.csv')
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
