"""Read-only actual released IVP dense-path witness;never commits a state."""
import argparse,json,shutil,subprocess,csv
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
TAIL=r'''
 std::string label;unsigned active,count;in>>label>>active;if(label!="FREE_ACTIVE_COUNT"||active)throw std::runtime_error("not free");in>>label>>count;if(label!="RELEASED_EDGES"||count!=3)throw std::runtime_error("missing released inventory");
 for(unsigned i=0;i<count;++i){unsigned f,t,a,b;double born;in>>f>>t>>a>>b>>born;}
 double clock;in>>label>>clock;if(!in||label!="ACCUMULATED_TIME"||clock!=time)throw std::runtime_error("physical clock differs");
 regrip_film_impact::EventControl control{.0001,.01,.02,.03,true};auto after=regrip_three_event::freeMidpoint(s,q,v,time,h,control);auto dense=regrip_three_event::denseSurfacePath(s,q,v,after,h);
 std::ofstream out(argv[2]);out<<std::setprecision(17)<<"fraction,time,minimum_gap_mm,triangle,rate_per_fraction\n";
 for(unsigned k=0;k<=32;++k){double alpha=k/32.;auto x=dense.path.position(alpha),velocity=dense.path.derivative(alpha);double minimum=1e99,rate=0;unsigned owner=0;
  for(unsigned j=0;j<dense.triangles.size();++j){auto tri=dense.triangles[j];auto g=regrip_film_sphere::ClosestPrimitive::evaluate({x[tri[0]],x[tri[1]],x[tri[2]]},{0,0,0},s.layout.bufferRadius);if(g.gap.v<minimum){minimum=g.gap.v;owner=j;rate=0;for(unsigned a=0;a<9;++a)rate+=g.gap.g[a]*velocity[tri[a/3]][a%3];}}
  out<<alpha<<','<<time+h*alpha<<','<<minimum<<','<<owner<<','<<rate<<'\n';out.flush();
 }
 auto proof=regrip_routed_contact::separatedNumericalPath(dense.path,dense.triangles,{0,0,0},s.layout.bufferRadius);std::cout<<std::setprecision(17)<<"strict_clear="<<proof.clear<<" plane_queries="<<proof.planeQueries<<" subdivisions="<<proof.subdivisions<<" unresolved_triangle="<<proof.unresolvedTriangle<<" begin="<<proof.unresolvedBegin<<" end="<<proof.unresolvedEnd<<" midpoint_gap="<<proof.midpointGap<<'\n';
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();provider=ROOT/'results/autonomous_film_20261118_routed_separation_build1370';m=json.loads((provider/'summary.json').read_text());src=ROOT/'results/autonomous_film_20261118_routed_release_actual1360';sm=json.loads((src/'summary.json').read_text());checkpoint=src/'three.checkpoint_137.txt'
 if m['status']!='PASS' or sm['status']!='PASS' or sha(checkpoint)!=sm['raw_hashes'][checkpoint.name]:raise ValueError('completed actual released state required')
 # New read-only diagnostic witness depends on this local header too;
 # copied after the immutable physical archive,never changes force dynamics.
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');shutil.copy2(ROOT/'models/film_routed_contact/SeparatedPath.h',archive/'models/film_routed_contact/SeparatedPath.h');shutil.copy2(ROOT/'models/film_routed_contact/RotatingPlane.h',archive/'models/film_routed_contact/RotatingPlane.h');cpp=archive/'diagnostics/film_three_finger/FreePathProbe.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/EdgeRelease.cpp').read_text().split(' unsigned count;in>>count;')[0];text='#include "../../models/film_routed_contact/SeparatedPath.h"\n#include "../../models/film_three_finger_event/DenseSurfacePath.h"\n'+text.replace('"REGRIP_EDGE_V2"','"REGRIP_ROUTED_FREE_V3"')+TAIL;cpp.write_text(text);shutil.copy2(checkpoint,out/'input.checkpoint');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe',out/'input.checkpoint',out/'path.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='read-only reconstructed actual-IVP numerical midpoint path;sampled gaps NOT CCD or accepted dynamics',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_checkpoint_sha256=sha(checkpoint),actual_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'path.csv').open()));r.update(status='PASS' if len(rows)==33 else 'FAIL',sampled_minimum_gap_mm=min(float(x['minimum_gap_mm']) for x in rows),strict_geometry_result=(out/'process/stdout.log').read_text().strip(),raw_hashes={'path.csv':sha(out/'path.csv')})
 if (out/'probe').exists():r['binary_sha256']=sha(out/'probe')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
