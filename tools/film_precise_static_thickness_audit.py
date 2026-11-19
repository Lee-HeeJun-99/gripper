"""Sampled static thickness/straight-wire clearance;never changes contact forces."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_static/Profiled.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitiveValue.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);regrip_three_finger::Layout layout;Eigen::Vector3d centre=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.0001)-layout.mount[0].origin);Point C{centre[0],centre[1],centre[2]};std::ifstream input(argv[1]);unsigned count;input>>count;std::cout<<std::setprecision(17)<<"stage,T_N,Skin_envelope_gap_mm,Rail_envelope_gap_mm,Skin_facet_prism_gap_mm,Rail_facet_prism_gap_mm,wire_centreline_actual_sphere_gap_mm\n";auto gap=[&](const std::vector<Point>&p){return regrip_film_sphere_value::ClosestPrimitiveValue::evaluate(p,C,layout.bodyRadius).gap.v;};
for(unsigned sample=0;sample<count;++sample){unsigned stage;double T;std::vector<Point>q(m.size());input>>stage>>T;for(auto&p:q)for(double&v:p)input>>v;if(!input)throw std::runtime_error("complete archived static geometry required");auto x=m.rest();for(unsigned i=0;i<q.size();++i)x[i]=add(x[i],q[i]);double envelope[2]={1e99,1e99},prism[2]={1e99,1e99};
for(unsigned part=0;part<3;++part)for(unsigned i=0;i+1<m.nx;++i)for(unsigned j=0;j+1<m.parts[part].ny;++j){unsigned a=m.id(part,i,j),b=m.id(part,i+1,j),c=m.id(part,i,j+1),d=m.id(part,i+1,j+1);for(auto tri:{std::array<unsigned,3>{a,b,c},std::array<unsigned,3>{b,d,c}}){std::vector<Point>p{x[tri[0]],x[tri[1]],x[tri[2]]};unsigned kind=part?1:0;double half=m.parts[part].thickness/2;envelope[kind]=std::min(envelope[kind],gap(p)-half);auto n=cross(sub(p[1],p[0]),sub(p[2],p[0]));double norm=std::sqrt(dot(n,n));if(!(norm>0))throw std::runtime_error("degenerate thickness facet;NO epsilon");n=scale(n,1/norm);std::array<Point,6>v;for(unsigned k=0;k<3;++k){v[k]=sub(p[k],scale(n,half));v[k+3]=add(p[k],scale(n,half));}for(auto face:std::vector<std::array<unsigned,3>>{{0,1,2},{3,4,5},{0,1,4},{0,4,3},{1,2,5},{1,5,4},{2,0,3},{2,3,5}})prism[kind]=std::min(prism[kind],gap({v[face[0]],v[face[1]],v[face[2]]}));}}
double wire=1e99;for(unsigned part:{1u,2u}){std::vector<Point>p;for(unsigned k=0;k<5;++k){unsigned i=(m.nx-1)*k/4;Assembly::Local local(m.guideIds(part,i),x);auto g=regrip_precise_static_profile::guide(m,local,part,i,4.5,8.);p.push_back({g[0].v,g[1].v,g[2].v});}for(unsigned k=0;k<4;++k)wire=std::min(wire,gap({p[k],p[k+1]}));}std::cout<<stage<<','<<T<<','<<envelope[0]<<','<<envelope[1]<<','<<prism[0]<<','<<prism[1]<<','<<wire<<'\n';}return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_static_profile_wide1766';m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or m['profile_amplitude_mm']!=4.5 or m['outboard_mm']!=8:raise ValueError('completed exact wide static candidate required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('source snapshot changed')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('immutable raw changed')
 rows=list(csv.DictReader((src/'contact.states.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/ThicknessAudit.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP);(out/'states.txt').write_text(str(len(rows))+'\n'+'\n'.join(' '.join((x['stage'],x['T_N'],x['q'])) for x in rows)+'\n');r=dict(status='FAIL',scope='geometry-only audit of64 completed STATIC load states;NOT SOFA/thick-shell dynamics/continuous-load-path/self-collision/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},thickness_assumption='constant reference thickness Skin.05mm/Rails.1mm;facet prisms use current flat triangle normals,NOT a validated through-thickness deformation law',envelope='distance(mid-triangle,sphere)-half-thickness sufficient-clearance bound',wire_radius_measured=None,guide_hardware_clearance=None,contact_forces='unchanged;no correction applied',contact_area=None,pressure=None)
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'observer');r['process']=guarded([out/'observer',out/'states.txt'],out/'process',120)
  if r['process']['exit_code']==0:
   values=[{k:float(v) for k,v in row.items()} for row in csv.DictReader((out/'process/stdout.log').open())];minimum={k:min(x[k] for x in values) for k in values[0] if k not in ('stage','T_N')};r.update(status='FAIL' if minimum['Skin_envelope_gap_mm']<0 or minimum['Rail_envelope_gap_mm']<0 else 'CLEAR_SAMPLED_ENVELOPE_ONLY',sampled_states=len(values),minimum_gaps_mm=minimum,wire_centreline_sampled_status='CLEAR_CENTRELINE_ONLY' if minimum['wire_centreline_actual_sphere_gap_mm']>=0 else 'FAIL',wire_radius_geometric_upper_bound_mm=minimum['wire_centreline_actual_sphere_gap_mm'],interpretation='Negative facet-prism gap is penetration ONLY under the stated prism proxy,not a measured real-film failure. Negative envelope alone cannot prove penetration. Existing .01mm buffer does not qualify .025mm Skin half-thickness.')
   shutil.copy2(out/'process/stdout.log',out/'clearance.csv')
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
