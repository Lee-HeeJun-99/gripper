"""Bounded independent three-film C2 pilot; preserves raw failures."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,default=.01);p.add_argument('--steps',type=int,default=4);p.add_argument('--maximum',type=float,default=.0001);p.add_argument('--reuse');p.add_argument('--adaptive',action='store_true');p.add_argument('--profile');p.add_argument('--exact-order',action='store_true');p.add_argument('--public-mass-case');a=p.parse_args()
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));source='diagnostics/film_three_finger/DrivenContact.cpp';(archive/source).parent.mkdir(parents=True);shutil.copy2(ROOT/source,archive/source)
 sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};binary=out/'reference'
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);meta=json.loads((prior/'summary.json').read_text())
  compiled=lambda values:{k:v for k,v in values.items() if k.endswith('.h') or k==source}
  if meta['status']!='PASS' or compiled(meta['sources'])!=compiled(sources) or sha(prior/'reference')!=meta['binary_sha256']:raise ValueError('immutable same compiled headers/driver/binary reuse required;unlinked CPP/docs excluded')
  binary=prior/'reference';compile=dict(exit_code=0,reused=a.reuse)
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',archive/source,'-o',binary],out/'compile',120)
 estimate=None
 if a.steps>8:
  if not a.profile:raise ValueError('measured same-physics runtime profile required above8steps')
  prior=json.loads((ROOT/'results'/('autonomous_film_'+a.profile)/'summary.json').read_text())
  if prior['status']!='PASS' or prior['duration']!=a.duration or prior['maximum_tension_N']!=a.maximum or prior.get('adaptive_gap_control',False)!=a.adaptive:raise ValueError('runtime profile physics differ')
  estimate=2*prior['run']['runtime_s']*a.steps/prior['steps']
  if estimate>480:write_json(out/'summary.json',dict(status='BLOCKED',predicted_runtime_s=estimate,reason='measured child runtime policy,NOT OS exhaustion'));return
 mass_args=[];mass_identity=None
 if a.public_mass_case:
  recorded=ROOT/'results'/('autonomous_film_'+a.public_mass_case);ms=json.loads((recorded/'summary.json').read_text());mi=json.loads((recorded/'identity.json').read_text());path=recorded/'public_mass.txt'
  if ms['status']!='PASS' or not mi.get('mass_journal') or not path.exists() or mi['sources']['models/film_three_finger/FrameLayout.h']!=sources['models/film_three_finger/FrameLayout.h']:raise ValueError('completed actual matching-geometry public mass journal required')
  shutil.copy2(path,out/'public_mass.txt');mass_args=['mass='+str(out/'public_mass.txt')];mass_identity=dict(case=a.public_mass_case,sha256=sha(path),kind='actual public getElementMass nodal/rigid API;not model-default reconstruction')
 run=guarded([binary,str(a.steps),str(a.duration),str(a.maximum),out/'states.csv',*(['adaptive'] if a.adaptive else []),*(['exact'] if a.exact_order else []),*mass_args],out/'run',480 if a.steps>8 else 120) if compile['exit_code']==0 else None
 result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent nonlinear three-film common C2 pilot;NOT actual SOFA or grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=sources,steps=a.steps,duration=a.duration,maximum_tension_N=a.maximum,control='existing ControlProfile,C2 ramp=duration,release=2duration,end=3duration;NEW input,NOT original4s C2 closing',initial='REST,already touching,externalFz=-.001N',compile=compile,run=run)
 if binary.exists():result['binary_sha256']=sha(binary)
 result['adaptive_gap_control']=a.adaptive
 result['exact_order_fallback']=a.exact_order
 result['public_mass_identity']=mass_identity
 result['predicted_runtime_s']=estimate
 if (out/'states.csv').exists():result['states_sha256']=sha(out/'states.csv')
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','run')}))
if __name__=='__main__':main()
