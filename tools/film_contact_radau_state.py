"""Independent nonlinear coupled FEM from actual post-impact state;not SOFA."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--modes',required=True);p.add_argument('--reference',required=True);p.add_argument('--lobatto',action='store_true');p.add_argument('--horizon',type=float,default=.000009765625);p.add_argument('--base-steps',type=int,default=1);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.modes);ref=ROOT/'results'/('autonomous_film_'+a.reference)
 if not 1<=a.base_steps<=4 or not 0<a.horizon<=.000625 or a.horizon/a.base_steps>1e-5:raise ValueError('unprofiled reference budget4 base steps/<=10us perstep;do not launch long refinement blindly')
 if json.loads((src/'summary.json').read_text())['status']!='PASS' or json.loads((ref/'summary.json').read_text())['status']!='PASS':raise ValueError('completed modal input and collocation unit reference required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');(archive/'models/film_coupled_collocation').mkdir()
 # Explicit new stage-journal result interface;physical original kernels stay
 # archived byte-for-byte. This is NOT replay of an old compiled owner.
 for name in ('CoupledSphere.h','CoupledOwnerClass.h'):shutil.copy2(ROOT/'models/film_coupled_contact'/name,archive/'models/film_coupled_contact'/name)
 shutil.copy2(ROOT/'models/film_coupled_collocation/SystemRadau.h',archive/'models/film_coupled_collocation/SystemRadau.h')
 header=ROOT/'models/film_coupled_collocation/SingleRowRadau.h'
 if sha(header)!=sha(ref/'sources/models/film_coupled_collocation/SingleRowRadau.h'):raise ValueError('independent qualified collocation header drift')
 shutil.copy2(header,archive/'models/film_coupled_collocation/SingleRowRadau.h');cpp=archive/'diagnostics/film_coupled_reintegrated/RadauActualState.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_coupled_reintegrated/RadauActualState.cpp',cpp);shutil.copy2(src/'input.txt',out/'input.txt')
 binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.txt',str(a.horizon),out/'states.csv',str(int(a.lobatto)),str(a.base_steps)],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent nonlinear actual-state FEM ONE contact branch,9.765625us;NOT actual SOFA/time certification',compile=compile,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_sha256=sha(out/'input.txt'),modal_input=a.modes,unit_reference=a.reference)
 result.update(lobatto=a.lobatto,horizon=a.horizon,base_steps=a.base_steps,scope='independent nonlinear actual-state FEM ONE persistent branch;NOT actual SOFA/time certification')
 if binary.exists():result['binary_sha256']=sha(binary)
 if result['status']=='PASS':
  rows=list(csv.DictReader((out/'states.csv').open()));comparisons=[]
  for i,j in ((0,1),(1,2),(0,2)):
   vi=np.fromstring(rows[i]['v'],sep=' ');vj=np.fromstring(rows[j]['v'],sep=' ');fi=float(rows[i]['normal_force']);fj=float(rows[j]['normal_force']);comparisons.append(dict(steps=[int(rows[i]['steps']),int(rows[j]['steps'])],velocity_relative=float(np.linalg.norm(vi-vj)/np.linalg.norm(vj)),endpoint_force_relative=abs(fi-fj)/abs(fj)))
  result['comparisons']=comparisons;result['time_gate']='NOT ASSESSED:only one short persistent branch,no complete event/time observables'
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','comparisons')}))
if __name__=='__main__':main()
