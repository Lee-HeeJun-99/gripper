"""Existing isolated6-row law on ACTUAL lateral23.4ms state,not global CCD."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_lateral_controlled_actual_two1472';m=json.loads((src/'summary.json').read_text());checkpoint=src/'three.checkpoint_117.txt'
 if m['status']!='PASS' or not m['all_micro_clocks_exact'] or sha(checkpoint)!=m['raw_hashes'][checkpoint.name]:raise ValueError('strict actual controlled23.4ms checkpoint required')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual model archive changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True)
 loader=(ROOT/'diagnostics/film_three_finger/RoutedCheckpoint.h').read_text().replace('REGRIP_ROUTED_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1');(diag/'RoutedCheckpoint.h').write_text(loader)
 path=archive/'models/film_three_finger_resume/IsolatedContactTransfer.h';text=path.read_text();changes={'#include "ContactRows.h"':'#include "FaceBranch.h"','auto geo=[&](const auto&x){return ownedGeometry(s,x,out.old);};':'auto geo=[&](const auto&x){return faceBranchGeometry(s,x,out.old);};','out.pre=advance(out.fractionTime);++out.rootEvaluations;auto ng=':'out.pre=advance(out.fractionTime);++out.rootEvaluations;if(minimumFaceParameter(s,out.pre.q,out.old)<=0)throw std::runtime_error("birth outside old face");for(const auto&stage:out.pre.stages)if(minimumFaceParameter(s,stage.q,out.old)<=0)throw std::runtime_error("accepted pre-event stage outside old face");auto ng='}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('existing isolated continuation anchor differs')
  text=text.replace(old,new)
 path.write_text(text)
 old=(ROOT/'diagnostics/film_three_finger/DetectedBirthTransfer.cpp').read_text();tail=old[old.index('std::string prefix=argv[2];'):];cpp=diag/'LateralBirth.cpp';cpp.write_text('#include "RoutedCheckpoint.h"\n#include "../../models/film_three_finger_resume/IsolatedContactTransfer.h"\n#include <iomanip>\n#include <iostream>\nusing namespace regrip_three_resume;\nint main(int argc,char**argv){try{if(argc!=3)throw std::runtime_error("checkpoint,prefix required");SharedFilmSystem s(Layout(),{0,0,-.001},true,true);s.exactUnresolved=true;Eigen::VectorXd q,v;double time,h;regrip_routed_checkpoint::read(argv[1],s,q,v,time,h);auto r=isolatedContactTransfer(s,q,v,time,h);'+tail)
 profile=json.loads((ROOT/'results/autonomous_film_20261118_routed_birth_transfer1327/summary.json').read_text());forecast=2*profile['process']['runtime_s']+2*json.loads((ROOT/'results/autonomous_film_20261118_lateral_controlled_rows1468/summary.json').read_text())['process']['runtime_s']+30
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);run=guarded([out/'reference',out/'input.checkpoint',out/'transfer'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='existing isolated124-to117 simultaneous birth/impact law on same actual lateral IVP;NOT actual SOFA/global CCD/whole time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),input_checkpoint_sha256=sha(checkpoint),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,predicted_child_runtime_s=forecast,analytic_extension='ONLY root bracketing;accepted stages must lie inside old face',root_work=None)
 if r['status']=='PASS':r.update(event_metrics=next(csv.DictReader((out/'transfer.metrics.csv').open())),binary_sha256=sha(out/'reference'))
 else:r['failure_reason']=(out/'process/stderr.log').read_text() if run else 'compile failed'
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
