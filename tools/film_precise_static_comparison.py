"""New precise-law equal-core-volume static comparison, not a grasp test."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--geometric',action='store_true');p.add_argument('--thickness',type=float,nargs='+',choices=(.075,.1,.125),default=(.1,.075,.125));a=p.parse_args()
 provider=ROOT/'results/autonomous_film_20261119_precise_tendon_gauss1715';m=json.loads((provider/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('immutable precise-law sources changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources/models',out/'sources/models');shutil.copy2(provider/'public_mass.txt',out/'public_mass.txt')
 code=(ROOT/'diagnostics/film_three_finger/TransmissionStatic.cpp').read_text()
 code=code.replace('#include "../../models/film_transmission/Kernel.h"','#include "../../models/film_rail_aspect/Design.h"\n#include "../../models/film_precise_tendon/Force.h"')
 code=code.replace('auto m=model(std::stod(argv[1]),std::stod(argv[2]));','auto m=regrip_rail_aspect::design(std::stod(argv[1]));')
 code=code.replace('auto e=parts(map,map.expand(x),T);','auto e=regrip_precise_tendon::parts(map,map.expand(x),T,6.);').replace('auto candidate=parts(map,map.expand(trial),T);','auto candidate=regrip_precise_tendon::parts(map,map.expand(trial),T,6.);')
 # Residual merit only: do not use rounded legacy cable length as precise potential.
 code=code.replace('bool hybrid=argc==7&&std::string(argv[6])=="hybrid";bool energy=hybrid||(argc==7&&std::string(argv[6])=="energy");','bool hybrid=false,energy=false;')
 if a.geometric:code=code.replace('double T=.0001*stage/stages;','double T=.0001*std::pow(10.,-6.*(stages-stage)/(stages-1));')
 cpp=out/'sources/diagnostics/film_three_finger/PreciseStatic.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(code)
 r=dict(status='INCOMPLETE',scope='independent precise-law free static force equilibrium and one-factor rail-aspect comparison ONLY;NOT contact/wrapping/dynamic stability/actual SOFA',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},maximum_tension_N_per_rail=.0001,core_volume_mm3_three_fingers=439.3397917746089,material_measured=False,force_gate_N=1e-12,relative_time_gate='NOT APPLICABLE:static',contact_area=None,pressure=None,root_reaction_work=None,trials={})
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference')
  r['continuation']='64 logarithmic load stages from1e-10N to1e-4N' if a.geometric else '16 linear load stages to1e-4N'
  for thickness in a.thickness:
   count=64 if a.geometric else 16
   folder=out/str(thickness);folder.mkdir();run=guarded([out/'reference',str(thickness),'5',str(count),out/'public_mass.txt',folder/'equilibrium'],folder/'process',480)
   rows=list(csv.DictReader((folder/'equilibrium.states.csv').open()));trial=dict(process=run,status='PASS' if run['exit_code']==0 and len(rows)==count else 'FAIL',accepted_stages=len(rows),actuation_work='NOT MATCHED:equal tension only;no design superiority claimed')
   if rows:
    last=rows[-1];trial.update(last_accepted_tension_N=float(last['T']),last_accepted_residual_N=float(last['residual_N']),last_accepted_shape=shape(np.fromstring(last['q'],sep=' ')),last_accepted_energy={k:float(last[k]) for k in ('U_skin','U_rails','U_attachment')})
   r['trials'][str(thickness)]=trial;write_json(out/'progress.json',r)
  r['status']='PASS' if all(x['status']=='PASS' for x in r['trials'].values()) else 'FAIL'
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','trials')}))
if __name__=='__main__':main()
