"""Passive next-trial observation from the exact prefix of failed1458/1459."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 actual=ROOT/'results/autonomous_film_20261118_lateral_unload_boundary1458';ref=ROOT/'results/autonomous_film_20261118_lateral_unload_boundary_ref1459';m=json.loads((actual/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text())
 if m['status']!='FAIL' or r['status']!='FAIL':raise ValueError('preserved failed horizons required')
 for path,meta in ((actual,m),(ref,r)):
  for f,d in meta.get('raw_hashes',{}).items():
   if sha(path/f)!=d:raise ValueError('failed evidence changed')
 x=list(csv.DictReader((actual/'three.states.csv').open()));y=list(csv.DictReader((ref/'states.csv').open()))
 if len(x)!=len(y) or len(x)!=1:raise ValueError('exact one-state accepted prefix required')
 if x[0]['time']!=y[0]['time'] or any(not np.array_equal(np.fromstring(x[0][k],sep=' '),np.fromstring(y[0][k],sep=' ')) for k in ('q','v')):raise ValueError('accepted prefix differs')
 checkpoint=actual/'three.checkpoint_115.txt';tokens=checkpoint.read_text().split()
 if tokens[0]!='REGRIP_LATERAL_PERSISTENT_V1' or float(tokens[1])!=float(x[0]['time']):raise ValueError('actual latest checkpoint differs')
 for k,start in (('q',5),('v',1958)):
  if not np.array_equal(np.array(tokens[start:start+1953],float),np.fromstring(x[0][k],sep=' ')):raise ValueError('checkpoint q/v differs')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');shutil.copytree(ref/'sources',out/'sources');cpp=out/'sources/diagnostics/film_three_finger/RoutedHoldReference.cpp';text=cpp.read_text()
 anchor='for(unsigned k=0;k<3;++k){const auto&x=k?result.stages[k-1].q:q;'
 observer='''{std::ofstream obs(std::string(argv[4])+".trial.csv");obs<<std::setprecision(17)<<"stage,time,whole_gap,momentum,velocity,finger,triangle,feature,selected_gap,normal_velocity,force\\n";for(unsigned k=0;k<3;++k){const auto&xx=k?result.stages[k-1].q:q;const auto&vv=k?result.stages[k-1].v:v;auto g=s.geometry(xx);for(unsigned f=0;f<3;++f){auto row=s.selected(xx,f);obs<<k<<','<<time+h*(k==0?0:k==1?.5:1)<<','<<s.clearance(xx)<<','<<result.momentumResidual<<','<<result.velocityResidual<<','<<f<<','<<row.triangle<<','<<row.feature<<','<<row.gap<<','<<g.J.row(f).dot(vv)<<','<<(k?result.stages[k-1].force[f]:result.initialForce[f])<<'\\n';}}}'''
 if text.count(anchor)!=1:raise ValueError('passive observation anchor differs')
 cpp.write_text(text.replace(anchor,observer+anchor));compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe',out/'input.checkpoint','8','1',out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None
 observed=out/'states.csv.trial.csv';result=dict(status='EXPERIMENTAL' if run and run['exit_code']!=0 and observed.exists() else 'FAIL',scope='passive rejected trial;old horizons FAIL,NO rejected-state commit',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(actual/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),checkpoint_sha256=sha(checkpoint),accepted_prefix_qv_time_exact=True,source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},compile=compile,process=run,rejected_state_committed=False)
 if observed.exists():result.update(rows=list(csv.DictReader(observed.open())),raw_sha256=sha(observed),binary_sha256=sha(out/'probe'))
 write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
