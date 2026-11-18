"""Same-mass nonlinear no-object coupon screen;not SOFA or grasp qualification."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_lateral_tendon/Step.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_lateral_tendon;auto m=regrip_rail_aspect::design(std::stod(argv[1]));auto mass=publicMass(argv[2]);std::vector<Point>q(m.size()),v(m.size());std::ofstream out(argv[3]);out<<std::setprecision(17)<<"time,T_per_rail_N,rail_thickness_mm,rail_width_mm,core_volume_three_mm3,U_skin,U_rails,U_attachment,K,cable_length_mm,momentum_residual,stage_tendon_work_Nmm,q,v\n";double time=0,h=.0002;long double work=0;auto c=control();for(unsigned k=0;k<std::stoul(argv[4]);++k){auto map=mechanics(m,q,v,h,0,mass);auto M=filmMass(map);std::array<Eigen::VectorXd,2>stageTendon,stagePosition;unsigned calls=0;auto r=gauss(M,map.pack(q),map.pack(v),time,h,[&](const Eigen::VectorXd&x,double t){auto e=parts(map,map.expand(x),c.sample(t).tension,6.);stageTendon[calls%2]=e.tendon;stagePosition[calls%2]=x;++calls;return e;});if(calls!=r.evaluations||stagePosition!=r.stageQ)throw std::runtime_error("actual accepted Gauss stage capture differs");for(unsigned j=0;j<2;++j)work+=static_cast<long double>(h/2)*stageTendon[j].dot(r.stageV[j]);time+=h;q=map.expand(r.q);v=map.expand(r.v);auto e=parts(map,q,c.sample(time).tension,6.);double K=.5*r.v.dot(M*r.v);out<<time<<','<<c.sample(time).tension<<','<<m.railT<<','<<m.railW<<','<<3*m.volume()<<','<<e.skin<<','<<e.rails<<','<<e.bond<<','<<K<<','<<e.cable<<','<<r.residual<<','<<work;quote(out,q);quote(out,v);out<<'\n';out.flush();}}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(5,50),default=5);p.add_argument('--profile');a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_rail_aspect_math1649';pm=json.loads((provider/'summary.json').read_text())
 if pm['status']!='PASS':raise ValueError('same design FD/objectivity qualification required')
 forecast=60.
 if a.steps==50:
  if not a.profile:raise ValueError('measured five-step cost required')
  prior=ROOT/'results'/('autonomous_film_'+a.profile);pr=json.loads((prior/'summary.json').read_text())
  if pr['steps']!=5 or pr['status']!='EXPERIMENTAL':raise ValueError('completed design profile required')
  forecast=2*max(x['process']['runtime_s'] for x in pr['trials'].values())*10+20
 if forecast>480:raise ValueError('profile forecast>480;NOT OS exhaustion')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('qualified design source changed')
 actual=ROOT/'results/autonomous_film_20261119_stationary_free_to50_chain1596_part12';am=json.loads((actual/'summary.json').read_text());cp=actual/'three.checkpoint_250.txt'
 if sha(cp)!=am['raw_hashes'][cp.name]:raise ValueError('actual common mass source changed')
 z=cp.read_text().split();offset=5+2*1953+4;mass=z[offset:offset+231];out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);cpp=diag/'RailAspectResponse.cpp';cpp.write_text(CPP);(out/'public_mass.txt').write_text('231\n'+' '.join(mass)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);trials={}
 if compile['exit_code']==0:
  for h in (.075,.1,.125):
   folder=out/('rail'+str(h));folder.mkdir();run=guarded([out/'reference',str(h),out/'public_mass.txt',folder/'states.csv',str(a.steps)],folder/'process',480);record=dict(process=run);trials[str(h)]=record
   if run['exit_code']==0:
    rows=list(csv.DictReader((folder/'states.csv').open()));last=rows[-1];record.update(completed_steps=len(rows),endpoint_shape=shape(np.fromstring(last['q'],sep=' ')),endpoint={k:float(last[k]) for k in last if k not in ('q','v')},states_sha256=sha(folder/'states.csv'))
 good=len(trials)==3 and all(x['process']['exit_code']==0 and x['completed_steps']==a.steps for x in trials.values());r=dict(status='EXPERIMENTAL' if good else 'FAIL',scope='independent nonlinear free no-object same-core/mass/T coupon screen ONLY;NOT actual SOFA/contact/wrapping or qualified time comparison',steps=a.steps,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),design_math_summary_sha256=sha(provider/'summary.json'),actual_mass_checkpoint_sha256=sha(cp),predicted_child_runtime_s=forecast,dt_s=.0002,material='unchanged research assumptions,NOT measured PET/TPU',root_boundary='existing649-DOF quadratic clamp',actuation='same C2T100uN/rise10ms/release20→30ms',object='NONE;no virtual gap/contact success inferred',time_convergence='NOT RUN for new designs',actual_SOFA='NOT RUN',selected_design=None,source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},public_mass_sha256=sha(out/'public_mass.txt'),binary_sha256=sha(out/'reference') if (out/'reference').exists() else None,compile=compile,trials=trials);write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','trials')}))
if __name__=='__main__':main()
