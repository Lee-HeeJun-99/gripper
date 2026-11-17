"""Fresh bounded independent energy-aware temporal controller;not SOFA."""
import argparse,json,shutil,subprocess,re
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--trace',action='store_true');p.add_argument('--horizon',action='store_true');p.add_argument('--actual21',action='store_true');p.add_argument('--trials',type=int,default=256);p.add_argument('--runtime',type=int,choices=(120,480),default=120);p.add_argument('--profile');a=p.parse_args()
    if not 1<=a.trials<=384:raise ValueError('bounded trial count<=384')
    if (a.trials>256 or a.runtime>120) and not a.profile:raise ValueError('extended reference needs measured profile')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('adaptive_ref_'+a.tag);build.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');sources=[]
    for directory in ('film_coupled_adaptive','film_coupled_contact','film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):sources+=list((ROOT/'models'/directory).glob('*.h'))
    sources+=[ROOT/'tests/test_coupled_adaptive.cpp']
    for f in sources:
        target=out/'sources'/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(ROOT)):sha(f) for f in sources},scope='independent adaptive time/energy controller;NOT actual SOFA'))
    if a.profile:
        prior=ROOT/'results'/('autonomous_film_'+a.profile);meta=json.loads((prior/'identity.json').read_text());measured=json.loads((prior/'summary.json').read_text());counts=[int(n) for n in re.findall(r'^trial (\d+) ',(prior/'run/stderr.log').read_text(),re.M)]
        if not a.actual21 or measured.get('nx')!=21 or not a.horizon or not counts:raise ValueError('explicit actual21 horizon trace profile required')
        for f in sources:
            key=str(f.relative_to(ROOT))
            if f.suffix=='.h' and meta['sources'].get(key)!=sha(f):raise ValueError('profiled mechanical/controller header changed')
        prediction=1.5*measured['run']['runtime_s']*a.trials/max(counts);write_json(out/'runtime_prediction.json',dict(profile=a.profile,observed_trials=max(counts),observed_s=measured['run']['runtime_s'],upper_trials=a.trials,margin=1.5,prediction_s=prediction,child_limit_s=a.runtime,physical_tolerance=1e-4,gate_unchanged=.001,scope='execution budget only;NOT physical acceptance'))
        if prediction>a.runtime:write_json(out/'summary.json',dict(status='BLOCKED',scope='prelaunch cost policy;NOT OS exhaustion',predicted_runtime_s=prediction));print(json.dumps(dict(status='BLOCKED')));return
    binary=build/'adaptive';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',out/'sources/tests/test_coupled_adaptive.cpp','-o',binary],out/'compile',120);result=dict(status='FAIL',compile=compile)
    if compile['exit_code']==0:
        run=guarded([binary]+(['--trace'] if a.trace else [])+(['--horizon'] if a.horizon else [])+(['--actual21'] if a.actual21 else [])+['--trials',str(a.trials)],out/'run',a.runtime);result.update(status='PASS' if run['exit_code']==0 else 'FAIL',run=run,binary_sha256=sha(binary),nx=21 if a.actual21 else 5,controller_norm='fixed physical macro-horizon scale with time budget' if a.horizon else 'instantaneous relative',scope='independent controller;old global .1% gate unchanged and NOT certified')
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'])))
if __name__=='__main__':main()
