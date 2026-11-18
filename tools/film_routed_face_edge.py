"""Reuse existing face/edge transfer with the SAME new routed coupled forces."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_routed_drift_probe1319';proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='EXPERIMENTAL' or not proof['accepted_prefix_qv_time_exact'] or sha(src/'input.checkpoint')!=proof['source_checkpoint_sha256']:raise ValueError('exact matched accepted prefix required;failed parents remain FAIL')
 for f,d in proof['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('routed source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(src/'input.checkpoint',out/'input.checkpoint');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True)
 for name in ('RoutedCheckpoint.h','RoutedFaceEdgeReference.cpp'):shutil.copy2(ROOT/'diagnostics/film_three_finger'/name,diag/name)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',diag/'RoutedFaceEdgeReference.cpp','-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'states.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='existing smooth-face→edge event transfer with new quadratic route,isolated24.2..24.4ms reference;NOT actual SOFA/full time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,prefix_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(out/'input.checkpoint'),compile=compile,process=run,root_reaction_work=None,old_horizon_status='FAIL remains')
 if (out/'reference').exists():r['binary_sha256']=sha(out/'reference')
 if run and run['exit_code']==0:r.update(json.loads((out/'process/stdout.log').read_text()));r['raw_hashes']={'states.csv':sha(out/'states.csv')}
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
