"""Same-law reduced force/Hessian replay at ALL common actual output clocks."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_precise_tendon/Force.h"
#include "../../models/film_rail_aspect/Design.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);std::ifstream in(argv[2]);unsigned count;in>>count;std::cout<<std::setprecision(17)<<"sample,quantity,absolute,norm1,norm2\n";std::ofstream raw(std::string(argv[3])+".forces.csv");raw<<std::setprecision(17)<<"sample,time,T,force1,force2\n";auto input=control();
for(unsigned sample=0;sample<count;++sample){double t;in>>t;std::vector<Point>q1(m.size()),v1(m.size()),q2(m.size()),v2(m.size());for(auto*values:{&q1,&v1,&q2,&v2})for(auto&p:*values)for(double&x:p)in>>x;if(!in)throw std::runtime_error("complete actual/interpolated q/v pair required");auto map=mechanics(m,q1,v1,.000025,0,mass);if(map.expand(map.pack(q1))!=q1||map.expand(map.pack(q2))!=q2||map.expand(map.pack(v1))!=v1||map.expand(map.pack(v2))!=v2)throw std::runtime_error("exact root mapping required;NO interpolation projection");double T=input.sample(t).tension;auto a=regrip_precise_tendon::parts(map,q1,T,6.),b=regrip_precise_tendon::parts(map,q2,T,6.);auto metric=[&](const char*name,const auto&a,const auto&b){std::cout<<sample<<','<<name<<','<<(a-b).norm()<<','<<a.norm()<<','<<b.norm()<<'\n';};metric("all_physical_force_N",a.force,b.force);metric("Skin_physical_force_N",a.force.head(295),b.force.head(295));metric("Rails_physical_force_N",a.force.tail(354),b.force.tail(354));metric("Hessian_N_mm",a.stiffness,b.stiffness);Eigen::VectorXd f1=a.force-2*filmMass(map)*map.pack(v1),f2=b.force-2*filmMass(map)*map.pack(v2);metric("total_with_Rayleigh_N",f1,f2);raw<<sample<<','<<t<<','<<T;for(auto*force:{&a.force,&b.force}){raw<<",\"";for(double x:*force)raw<<x<<' ';raw<<'"';}raw<<'\n';}return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261119_plan_actual1743','20261119_plan_actual_half1744','20261119_plan_actual_quarter1745');parents=[ROOT/'results'/('autonomous_film_'+n) for n in names];meta=[json.loads((p/'summary.json').read_text()) for p in parents];data=[]
 for parent,m in zip(parents,meta):
  if m['status']!='PASS' or m['binary_sha256']!=meta[0]['binary_sha256'] or m['source_hashes']!=meta[0]['source_hashes']:raise ValueError('completed SAME actual binary/model required')
  if sha(parent/'actual.csv')!=m['raw_hashes']['actual.csv']:raise ValueError('actual raw changed')
  data.append(list(csv.DictReader((parent/'actual.csv').open())))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(parents[0]/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/ForceTime.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP);samples=[];origins=[]
 for lo,hi in ((0,1),(1,2),(0,2)):
  times=np.array([float(x['time']) for x in data[hi]])
  for row in data[lo]:
   t=float(row['time']);j=int(np.argmin(abs(times-t)));other=data[hi][j];distance=abs(times[j]-t)
   if distance:
    right=int(np.searchsorted(times,t));left=right-1
    if left<0 or right>=len(times):raise ValueError('no force replay extrapolation')
    alpha=(t-times[left])/(times[right]-times[left]);other={k:' '.join(format(x,'.17g') for x in ((1-alpha)*np.fromstring(data[hi][left][k],sep=' ')+alpha*np.fromstring(data[hi][right][k],sep=' '))) for k in ('q','v')}
   samples.append(' '.join((row['time'],row['q'],row['v'],other['q'],other['v'])));origins.append(dict(pair=str(lo)+'_'+str(hi),time_s=t,nearest_clock_distance_s=float(distance)))
 (out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(samples)+'\n');mass=ROOT/'results/autonomous_film_20261119_precise_solver_plan1737/public_mass.txt';shutil.copy2(mass,out/'public_mass.txt');r=dict(status='FAIL',scope='offline shared-model reduced force/Hessian replay of actual1ms common-clock states ONLY;NOT a fresh native SOFA ForceField API call/whole contact/energy/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256={n:sha(p/'summary.json') for n,p in zip(names,parents)},source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},relative_gate=.001,absolute_floor='NONE',root_reaction_work=None,root_reaction_force='NOT MEASURED;reduced forces only',control='original C++ control().sample(actual coarse physical time);NO Python control reimplementation',interpolation='same explicit fine-state physical-clock interpolation as1747;raw unchanged;no rigorous interpolation-error bound')
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'observer');r['process']=guarded([out/'observer',out/'public_mass.txt',out/'samples.txt',out/'actual'],out/'process',180)
  if r['process']['exit_code']==0:
   records=[]
   for row in csv.DictReader((out/'process/stdout.log').open()):
    absolute=float(row['absolute']);scale=max(float(row['norm1']),float(row['norm2']));relative=absolute/scale if scale else None;records.append(dict(**origins[int(row['sample'])],quantity=row['quantity'],absolute=absolute,relative=relative,status='EXACT_ZERO' if not scale and not absolute else 'PASS' if relative is not None and relative<=.001 else 'FAIL'))
   with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
   r.update(status='PASS' if not any(x['status']=='FAIL' for x in records) else 'FAIL',worst=max((x for x in records if x['relative'] is not None),key=lambda x:x['relative']),compared_observables=len(records))
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
