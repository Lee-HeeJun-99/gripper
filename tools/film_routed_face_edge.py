"""Reuse existing face/edge transfer with the SAME new routed coupled forces."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('face-edge','detected-birth','smooth-birth'),default='face-edge');p.add_argument('--prefix',default='20261118_routed_drift_probe1319');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.prefix);proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='EXPERIMENTAL' or not proof['accepted_prefix_qv_time_exact'] or sha(src/'input.checkpoint')!=proof['source_checkpoint_sha256']:raise ValueError('exact matched accepted prefix required;failed parents remain FAIL')
 for f,d in proof['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('routed source archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(src/'input.checkpoint',out/'input.checkpoint');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True)
 name='RoutedFaceEdgeReference.cpp' if a.mode=='face-edge' else 'DetectedBirthTransfer.cpp'
 for file in ('RoutedCheckpoint.h',name):shutil.copy2(ROOT/'diagnostics/film_three_finger'/file,diag/file)
 if a.mode=='smooth-birth':
  # ONLY root bracketing uses analytic continuation of old feature6. The
  # accepted pre-impact stages must ALL remain strictly inside that face.
  # This is a new isolated numerical branch,not a waiver of feature validity.
  path=archive/'models/film_three_finger_resume/IsolatedContactTransfer.h';text=path.read_text()
  changes={'#include "ContactRows.h"':'#include "FaceBranch.h"','auto geo=[&](const auto&x){return ownedGeometry(s,x,out.old);};':'auto geo=[&](const auto&x){return faceBranchGeometry(s,x,out.old);};','out.pre=advance(out.fractionTime);++out.rootEvaluations;auto ng=':'out.pre=advance(out.fractionTime);++out.rootEvaluations;if(minimumFaceParameter(s,out.pre.q,out.old)<=0)throw std::runtime_error("birth not before old-face boundary;accepted continuation forbidden");for(const auto&stage:out.pre.stages)if(minimumFaceParameter(s,stage.q,out.old)<=0)throw std::runtime_error("accepted pre-birth stage outside physical face");auto ng='}
  for old,new in changes.items():
   if text.count(old)!=1:raise ValueError('isolated analytic bracketing anchor differs')
   text=text.replace(old,new)
  path.write_text(text);cpp=diag/name;text=cpp.read_text();old='auto r=detectedContactTransfer(s,q,v,time,h);'
  if text.count(old)!=1:raise ValueError('explicit isolated birth diagnostic anchor differs')
  cpp.write_text(text.replace(old,'auto r=isolatedContactTransfer(s,q,v,time,h);'))
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',diag/name,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/('states.csv' if a.mode=='face-edge' else 'transfer')],out/'process',480) if compile['exit_code']==0 else None;header=(out/'input.checkpoint').read_text().split();r=dict(status='FAIL',mode=a.mode,scope='existing restricted event transfer with new quadratic route,isolated supplied accepted interval;NOT actual SOFA/global CCD/full time/grasp',checkpoint_start_time_s=float(header[1]),nominal_dt_s=float(header[2]),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes=sources,prefix_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(out/'input.checkpoint'),compile=compile,process=run,root_reaction_work=None,old_horizon_status='FAIL remains')
 if (out/'reference').exists():r['binary_sha256']=sha(out/'reference')
 if run and run['exit_code']==0:
  if a.mode=='face-edge':r.update(json.loads((out/'process/stdout.log').read_text()));r['raw_hashes']={'states.csv':sha(out/'states.csv')}
  else:r.update(status='PASS',event_metrics=next(csv.DictReader((out/'transfer.metrics.csv').open())),raw_hashes={f:sha(out/f) for f in ('transfer.metrics.csv','transfer.rows.csv','transfer.states.txt')})
 elif run:r['failure_reason']=(out/'process/stderr.log').read_text().strip()
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
