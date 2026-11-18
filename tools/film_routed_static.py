"""Fixed routed amplitude4.5,independent no-object force equilibrium only."""
import csv,json,shutil,subprocess,argparse
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--design',choices=('quadratic','lateral'),default='quadratic');p.add_argument('--load-stages',type=int,choices=(16,32),default=16);a=p.parse_args();provider=ROOT/'results'/('autonomous_film_20261118_lateral_api_build1356' if a.design=='lateral' else 'autonomous_film_20261118_routed_math_api1240');proof=json.loads((provider/'summary.json').read_text());out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources/models',out/'sources/models');folder=out/'sources/diagnostics/film_three_finger';folder.mkdir(parents=True)
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('routed physical source archive changed')
 for name in ('RoutedStatic.cpp','TransmissionStatic.cpp'):shutil.copy2(ROOT/'diagnostics/film_three_finger'/name,folder/name)
 if a.design=='lateral':
  cpp=folder/'RoutedStatic.cpp';text=cpp.read_text();old='regrip_routed_tendon::parts(m,q,T,4.5)'
  if text.count(old)!=1:raise ValueError('static mechanical adapter changed')
  cpp.write_text(text.replace('film_routed_tendon/Step.h','film_lateral_tendon/Step.h').replace(old,'regrip_lateral_tendon::parts(m,q,T,6)'))
 mass=ROOT/'results/autonomous_film_20261118_routed_candidate_full1244/public_mass.txt';parent=json.loads((mass.parent/'summary.json').read_text())
 if parent['status']!='PASS' or sha(mass)!=parent['raw_hashes']['public_mass.txt']:raise ValueError('actual public mass guard')
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',folder/'RoutedStatic.cpp','-o',out/'reference'],out/'compile',120);run=guarded([out/'reference','.001','5',str(a.load_stages),mass,out/'equilibrium','hybrid'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent routed static force equilibrium;NOT actual SOFA/contact/stability/dynamic arrival',load_stages=a.load_stages,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),provider_summary_sha256=sha(provider/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},compile=compile,process=run,physical_input='same core/bond.001/offset5;quadratic amplitude4.5;Tmax.0001N/rail',force_gate_N=1e-12,root_work=None,matched_work=False)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'equilibrium.states.csv').open()));r.update(status='PASS' if len(rows)==a.load_stages and max(float(i['residual_N']) for i in rows)<=1e-12 else 'FAIL',endpoint={k:float(v) for k,v in rows[-1].items() if k!='q'},shape=shape(np.fromstring(rows[-1]['q'],sep=' ')))
 r['design']=a.design
 if a.design=='lateral':r['physical_input']='same core/bond.001/normal offset5;outboard lateral6;Tmax.0001N/rail;no object'
 r['failure_reason']=(out/'process/stderr.log').read_text() if run and run['exit_code'] else None;r['raw_hashes']={f.name:sha(f) for f in out.glob('equilibrium.*')};r['binary_sha256']=sha(out/'reference') if (out/'reference').exists() else None;write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
