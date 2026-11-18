"""Separate routed-tendon VALUE vs its verified smooth-branch derivative."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../models/film_transmission/Kernel.h"
#include "../models/film_lateral_tendon/Route.h"
#include <iostream>
#include <iomanip>
int main(){try{using namespace regrip_transmission;auto m=model();unsigned j=3*m.id(1,10,0)+2;std::cout<<std::setprecision(17)<<"delta_mm,force_N,baseline_force_N,Hjj_N_mm,linearized_force_increment_N\n";double baseline=0;for(double delta:{0.,1e-10,1e-14,1e-18,1e-24,1e-30}){std::vector<Point>q(m.size());q[j/3][j%3]=delta;double force=0,H=0;regrip_lateral_tendon::route(m,q,.0001,6.,[&](const Element&e){for(unsigned a=0;a<3*e.ids.size();++a)if(3*e.ids[a/3]+a%3==j){force-=e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b)if(3*e.ids[b/3]+b%3==j)H+=e.energy.h[N*a+b];}});if(delta==0)baseline=force;std::cout<<delta<<','<<force<<','<<baseline<<','<<H<<','<<-H*delta<<'\n';}}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--precise-tendon',action='store_true');a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_precise_window_actual1702';m=json.loads((parent/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('qualified actual source required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('frozen source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(parent/'sources',archive);cpp=archive/'tests/TendonValue.cpp';code=CPP
 if a.precise_tendon:
  shutil.copytree(ROOT/'models/film_precise_tendon',archive/'models/film_precise_tendon');code=code.replace('#include "../models/film_lateral_tendon/Route.h"','#include "../models/film_precise_tendon/Route.h"').replace('regrip_lateral_tendon::route','regrip_precise_tendon::route')
 cpp.write_text(code);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe'],out/'process',60) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent tiny tendon force-value directional derivative consistency ONLY;NOT full cause/solver/SOFA/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(parent/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,relative_gate=.001,absolute_floor='NONE',reference='smooth flat branch directional derivative;linearized increment,not exact finite-deformation solution',physical_parameters='sameT100uN,offset5mm,lateral6mm,mid-guide left Rail node z perturbation')
 if run and run['exit_code']==0:
  rows=[{k:float(v) for k,v in x.items()} for x in csv.DictReader((out/'process/stdout.log').open())];records=[]
  for row in rows:
   expected=row['linearized_force_increment_N'];row['relative_increment_error']=abs(row['force_N']-row['baseline_force_N']-expected)/abs(expected) if expected else None;records.append(row)
  with (out/'precision.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  worst=max(x['relative_increment_error'] for x in records if x['relative_increment_error'] is not None);r.update(status='PASS' if worst<=.001 else 'FAIL',maximum_relative_increment_error=worst,binary_sha256=sha(out/'probe'),raw_hashes={'precision.csv':sha(out/'precision.csv')},metrics=records,warning='does not establish sole cause of all-time failure;historical absolute FD gates are preserved')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','metrics')}))
if __name__=='__main__':main()
