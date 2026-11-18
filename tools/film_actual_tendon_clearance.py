"""Actual stored moving-sphere/tendon path screen;wire radius/solid guides unknown."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_three_finger/SharedFilmSystem.h"
#include "../../models/film_lateral_tendon/Route.h"
#include <fstream>
#include <iomanip>
#include <iostream>
int main(int argc,char**argv){try{using namespace regrip_three_finger;SharedFilmSystem s(Layout(),{0,0,0},true,true);std::ifstream in(argv[1]);unsigned count;in>>count;if(!in||!count||count>32)throw std::runtime_error("bounded actual snapshot count required");std::ofstream out(argv[2]);out<<std::setprecision(17)<<"time,finger,wire_physical_sphere_gap_mm,guide_support_centreline_gap_mm,combined_wire_length_mm\n";
 auto distance=[](const Eigen::Vector3d&a,const Eigen::Vector3d&b,const Eigen::Vector3d&center,double radius){auto d=b-a;double length=d.squaredNorm();if(!(length>0))throw std::runtime_error("degenerate physical path segment");double u=std::max(0.,std::min(1.,(center-a).dot(d)/length));return (a+u*d-center).norm()-radius;};
 for(unsigned row=0;row<count;++row){double time;Eigen::VectorXd q(s.initial.size());in>>time;for(double&x:q)in>>x;if(!in||!q.allFinite())throw std::runtime_error("finite actual snapshot required");Eigen::Vector3d center=q.segment<3>(3*s.shared.nf);
  for(unsigned f=0;f<3;++f){auto local=s.local(q,f);const auto&m=s.shared.films[f].film.model;auto actual=m.rest();for(unsigned i=0;i<actual.size();++i)actual[i]=add(actual[i],local.q[i]);double wire=1e9,arm=1e9,L=0;
   for(unsigned part:{1u,2u}){std::vector<Eigen::Vector3d>points;for(unsigned k=0;k<=m.guideIntervals;++k){unsigned i=(m.nx-1)*k/m.guideIntervals;Assembly::Local map(m.guideIds(part,i),actual);auto p=regrip_lateral_tendon::guide(m,map,part,i,6.),base=m.guide(map,part,i,0);Eigen::Vector3d x(p[0].v,p[1].v,p[2].v),b(base[0].v,base[1].v,base[2].v);x=s.layout.mount[f].origin+s.layout.mount[f].R*x;b=s.layout.mount[f].origin+s.layout.mount[f].R*b;arm=std::min(arm,distance(b,x,center,s.layout.bodyRadius));points.push_back(x);}for(unsigned k=1;k<points.size();++k){wire=std::min(wire,distance(points[k-1],points[k],center,s.layout.bodyRadius));L+=(points[k]-points[k-1]).norm();}}
   out<<time<<','<<f<<','<<wire<<','<<arm<<','<<L<<'\n';
  }
 }
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors'] or sha(src/'scene.scn')!=m['scene_sha256']:raise ValueError('complete actual snapshot source required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual model archive changed')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 scene=ET.parse(src/'scene.scn');fields=list(scene.iter('FilmLateralTendon'))
 if len(fields)!=3 or any(float(f.get('lateralOffset'))!=6 or float(f.get('guideOffset'))!=5 for f in fields):raise ValueError('actual6mm outboard/5mm normal routing required')
 states=list(csv.DictReader((src/'three.states.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/ActualWire.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP);(out/'samples.txt').write_text(str(len(states))+'\n'+'\n'.join(x['time']+' '+x['q'] for x in states)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'geometry'],out/'compile',120);run=guarded([out/'geometry',out/'samples.txt',out/'geometry.csv'],out/'process',180) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='read-only ACTUAL moving-sphere tendon CENTRELINE/assumed support-line geometry screen ONLY;NOT wire collision dynamics or solid clearance certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,wire_radius=None,guide_support_solid_geometry=None,wire_skin_self_collision='NOT RUN',contact_pressure=None,holding_load=None,warning='guide support segment is inferred centreline,not an implemented solid;finite thickness/continuous path clearance remain unqualified')
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'geometry.csv').open()));ff=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];length=max(abs(float(row['combined_wire_length_mm'])-float(ff[int(row['finger'])][i//3]['cable_length'])) for i,row in enumerate(rows));wire=min(float(x['wire_physical_sphere_gap_mm']) for x in rows);support=min(float(x['guide_support_centreline_gap_mm']) for x in rows);r.update(status='PASS' if len(rows)==3*len(states) and length<=1e-12 else 'FAIL',actual_field_length_max_abs_mm=length,minimum_actual_wire_centreline_gap_mm=wire,minimum_assumed_support_centreline_gap_mm=support,sampled_centreline_screen='PASS' if wire>=0 and support>=0 else 'FAIL',binary_sha256=sha(out/'geometry'),raw_hashes={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
