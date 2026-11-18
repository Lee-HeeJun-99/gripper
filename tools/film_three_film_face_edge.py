"""Independent event-aligned face-edge remainder from an actual saved IVP."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--step',type=int,required=True);p.add_argument('--continuation-steps',type=int,choices=(0,1,2,3,4),default=0);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text());checkpoint=src/f'three.checkpoint_{a.step}.txt'
 if sha(checkpoint)!=meta['raw_hashes'][checkpoint.name]:raise ValueError('saved actual state changed')
 previous=ROOT/'results/autonomous_film_20261118_three_film_face_alias1054';profile=json.loads((previous/'summary.json').read_text());forecast=2*profile['run']['runtime_s']+30+20*a.continuation_steps
 if profile['status']!='PASS' or forecast>480:raise ValueError('measured face-root forecast not within480s')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(checkpoint,out/'input.checkpoint');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/FaceEdgeTransfer.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/FaceEdgeTransfer.cpp',cpp);binary=out/'reference';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'input.checkpoint',out/'transfer']+([str(a.continuation_steps)] if a.continuation_steps else []),out/'run',480) if compile['exit_code']==0 else None;result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent event-aligned Face->Edge and continuous velocity remainder;NO actual SOFA/global CCD/fullcycle qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,run=run,predicted_runtime_s=forecast,profile_summary_sha256=sha(previous/'summary.json'),checkpoint_sha256=sha(checkpoint),physics='same M/C2/material/normal law,no impulse or velocity clamp at a C1 feature transition',root_reaction_work=None,continuation_steps=a.continuation_steps)
 if binary.exists():result['binary_sha256']=sha(binary)
 if (out/'transfer.metrics.csv').exists():result['metrics']=next(csv.DictReader((out/'transfer.metrics.csv').open()))
 if run:result['failure_reason']=(out/'run/stderr.log').read_text().strip() or None
 result['raw_hashes']={f.name:sha(f) for f in out.glob('transfer.*')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','run')}))
if __name__=='__main__':main()
