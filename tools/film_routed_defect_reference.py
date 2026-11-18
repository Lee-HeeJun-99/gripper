"""Constraint-defect bisection of isolated rejected24.2..24.4ms interval."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--refinement',type=int,choices=(1,2,4),default=1);p.add_argument('--reuse');a=p.parse_args();prefix=ROOT/'results/autonomous_film_20261118_routed_drift_probe1319';pm=json.loads((prefix/'summary.json').read_text());src=ROOT/'results/autonomous_film_20261118_routed_unload_to276_reference1313';m=json.loads((src/'summary.json').read_text());checkpoint=prefix/'input.checkpoint'
 if pm['status']!='EXPERIMENTAL' or not pm['accepted_prefix_qv_time_exact'] or sha(checkpoint)!=pm['source_checkpoint_sha256'] or m['status']!='FAIL':raise ValueError('matched accepted prefix of preserved failures required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('fixed physical source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copy2(ROOT/'models/film_routed_contact/DefectStep.h',archive/'models/film_routed_contact/DefectStep.h');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True)
 for name in ('RoutedCheckpoint.h','RoutedDefectReference.cpp'):shutil.copy2(ROOT/'diagnostics/film_three_finger'/name,diag/name)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};forecast=None
 if a.reuse:
  oldpath=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((oldpath/'summary.json').read_text())
  if old['source_hashes']!=sources or sha(oldpath/'reference')!=old['binary_sha256'] or old['input_checkpoint_sha256']!=sha(checkpoint):raise ValueError('same compiled diagnostic and physical IVP required')
  shutil.copy2(oldpath/'reference',out/'reference');compile=dict(exit_code=0,reused_from=a.reuse);forecast=2*old['process']['runtime_s']*a.refinement/old['refinement']+30
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',diag/'RoutedDefectReference.cpp','-o',out/'reference'],out/'compile',120)
 result=dict(status='BLOCKED',scope='isolated saved24.2..24.4ms constraint-defect-controlled reference ONLY;NOT state-error-adaptive/full time/actual SOFA/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,prefix_summary_sha256=sha(prefix/'summary.json'),input_checkpoint_sha256=sha(checkpoint),refinement=a.refinement,compile=compile,predicted_child_runtime_s=forecast,old_full_horizon_status='FAIL remains',root_reaction_work=None)
 if forecast and forecast>480:result['failure_reason']='measured policy forecast>480s;NOT OS exhaustion';write_json(out/'summary.json',result);return
 run=guarded([out/'reference',out/'input.checkpoint',str(a.refinement),out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;result.update(status='FAIL',process=run)
 if (out/'reference').exists():result['binary_sha256']=sha(out/'reference')
 if run and run['exit_code']==0:result.update(json.loads((out/'process/stdout.log').read_text()))
 result['raw_hashes']={f:sha(out/f) for f in ('states.csv',) if (out/f).exists()};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
