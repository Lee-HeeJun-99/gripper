"""Independent three-film/one-sphere nonlinear fixed-contact-branch coupon."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--force-z',type=float,default=-.001);p.add_argument('--dt',type=float,default=.0001);p.add_argument('--reuse');p.add_argument('--rescan',action='store_true');p.add_argument('--precise-ties',action='store_true');a=p.parse_args()
 if not 0<a.dt<=.0001 or abs(a.force_z)>.001:raise ValueError('explicit bounded100us/1mN independent IVP only')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));(archive/'tests').mkdir();name='tests/test_three_film_persistent.cpp';shutil.copy2(ROOT/name,archive/name);sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};binary=out/'test'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);pm=json.loads((prior/'summary.json').read_text());binary=prior/'test'
  if pm['status']!='PASS' or any(sources.get(k)!=v for k,v in pm['sources'].items() if k.endswith('.h') or k==name):raise ValueError('independent reused compiled source identity differs')
  if pm.get('binary_sha256') and sha(binary)!=pm['binary_sha256']:raise ValueError('independent reference binary changed')
  compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/name,'-o',binary],out/'compile',120)
 run=guarded([binary,str(a.force_z),str(a.dt),out/'state.csv',*(['precise'] if a.precise_ties else ['rescan'] if a.rescan else [])],out/'run',120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent nonlinear3film/ONE free sphere,fixed3row,rest,T0;NOT SOFA/closing/active-set/grasp',external_force_N=[0,0,a.force_z],dt=a.dt,root_center_radius_mm=50,object_radius_mm=30,material_parameters='SharedFilmSystem/FrameLayout archived research assumptions,NOT measured PET',compile=compile,run=run,sources=sources,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
 result['whole_trial_rescan']=a.rescan or a.precise_ties;result['precise_ties']=a.precise_ties
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'state.csv').exists():result['state_sha256']=sha(out/'state.csv')
 if (out/'state.csv.rejected.csv').exists():result['rejected_state_sha256']=sha(out/'state.csv.rejected.csv')
 write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],run=run)))
if __name__=='__main__':main()
