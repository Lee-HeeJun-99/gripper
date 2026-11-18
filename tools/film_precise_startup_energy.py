"""Offline stage-power audit of immutable actual SOFA four-stage states."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_precise_attachment/Force.h"
#include "../../models/film_rail_aspect/Design.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);std::ifstream in(argv[2]);unsigned count;in>>count;std::cout<<std::setprecision(17)<<"sample,tendon_power_Nmm_s,damping_power_Nmm_s,U_skin,U_rails,U_attachment,K,reduced_force\n";for(unsigned k=0;k<count;++k){double T;in>>T;std::vector<Point>q(m.size()),v(m.size());for(auto*p:{&q,&v})for(auto&x:*p)for(auto&d:x)in>>d;if(!in)throw std::runtime_error("complete archived stage state required");auto map=mechanics(m,q,v,.000025,0,mass);auto part=regrip_precise_attachment::parts(map,q,T,6.);auto velocity=map.pack(v);double mv=velocity.dot(filmMass(map)*velocity);std::cout<<k<<','<<part.tendon.dot(velocity)<<','<<2*mv<<','<<part.skin<<','<<part.rails<<','<<part.bond<<','<<.5*mv<<",\"";for(double x:part.force)std::cout<<x<<' ';std::cout<<"\"\n";}}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=['20261119_precise_startup_base1688','20261119_precise_startup_half1689','20261119_precise_startup_quarter1690'];parents=[ROOT/'results'/('autonomous_film_'+n) for n in names];meta=[json.loads((f/'summary.json').read_text()) for f in parents]
 for f,m in zip(parents,meta):
  if m['status']!='PASS' or m['source_hashes']!=meta[0]['source_hashes'] or m['binary_sha256']!=meta[0]['binary_sha256']:raise ValueError('same qualified actual model required')
  for name,d in m['raw_hashes'].items():
   if sha(f/name)!=d:raise ValueError('immutable actual raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(parents[0]/'sources',archive);cpp=archive/'diagnostics/film_three_finger/PreciseStageEnergy.cpp';cpp.parent.mkdir(parents=True,exist_ok=True);cpp.write_text(CPP);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120);r=dict(status='FAIL',scope='offline actual stage-power and endpoint energy audit ONLY;NOT whole-energy/contact/grasp',compile=compile,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},actual_summary_hashes={n:sha(f/'summary.json') for n,f in zip(names,parents)},root_reaction_work=None,external_work=0,impact_loss=0,contact_work=0,relative_gate=.001,absolute_floor='NONE',trials={})
 if compile['exit_code']==0:
  r['observer_binary_sha256']=sha(out/'observer')
  for parent,m in zip(parents,meta):
   folder=out/str(m['steps']);folder.mkdir();stages=list(csv.DictReader((parent/'actual.csv.gauss4.csv').open()));accepted=list(csv.DictReader((parent/'actual.csv').open()));fields=list(csv.DictReader((parent/'film.csv').open()));samples=[(s['T'],s['q'],s['v']) for s in stages]+[('0',accepted[-1]['q'],accepted[-1]['v'])];text=str(len(samples))+'\n'+'\n'.join(' '.join(x) for x in samples)+'\n';(folder/'states.txt').write_text(text);mass=ROOT/'results/autonomous_film_20261119_rail_aspect_peak1652/public_mass.txt';run=guarded([out/'observer',mass,folder/'states.txt'],folder/'process',180);trial=dict(process=run);r['trials'][str(m['steps'])]=trial
   if run['exit_code']!=0:continue
   rows=list(csv.DictReader((folder/'process/stdout.log').open()));weights=np.array([float(s['weight_s']) for s in stages]);work=float(weights@np.array([float(x['tendon_power_Nmm_s']) for x in rows[:-1]]));damping=float(weights@np.array([float(x['damping_power_Nmm_s']) for x in rows[:-1]]));force=max(float(np.max(abs(np.fromstring(x['reduced_force'],sep=' ')-np.fromstring(y['reduced_physical_force_N'],sep=' ')))) for x,y in zip(rows,stages));end=rows[-1];u=sum(float(end[k]) for k in ('U_skin','U_rails','U_attachment'));kinetic=float(end['K']);field=fields[-1];identity=work-damping-u-kinetic;match=max(abs(float(field['U_shell'])-float(end['U_skin'])-float(end['U_rails'])),abs(float(field['U_attachment'])-float(end['U_attachment'])),abs(float(field['K'])-kinetic));trial.update(status='PASS' if len(rows)==len(samples) and force<=1e-12 and match<=1e-12 else 'FAIL',Tendon_work_Nmm=work,Damping_loss_Nmm=damping,U_skin=float(end['U_skin']),U_rails=float(end['U_rails']),U_attachment=float(end['U_attachment']),K=kinetic,partial_signed_defect_Nmm=identity,actual_stage_force_max_abs_N=force,actual_Field_energy_max_abs_Nmm=match,warning='signed defect is NOT heat;root work NULL;no full energy claim')
  if all(x.get('status')=='PASS' for x in r['trials'].values()) and len(r['trials'])==3:
   errors={}
   for lo,hi in (('8','16'),('16','32'),('8','32')):
    left,right=r['trials'][lo],r['trials'][hi];pair={}
    for key in ('Tendon_work_Nmm','Damping_loss_Nmm','U_skin','U_rails','U_attachment','K','partial_signed_defect_Nmm'):
     absolute=abs(left[key]-right[key]);scale=max(abs(left[key]),abs(right[key]));relative=absolute/scale if scale else None;pair[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'UNDEFINED' if relative is None else 'FAIL')
    errors[lo+'_'+hi]=pair
   r.update(status='PASS' if all(x['status']=='PASS' for pair in errors.values() for x in pair.values()) else 'FAIL',observer_validation='PASS',time_errors=errors)
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','raw_hashes')}))
if __name__=='__main__':main()
