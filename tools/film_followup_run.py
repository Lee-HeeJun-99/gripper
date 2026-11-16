"""Reuse an immutable qualified build for a bounded, new contact experiment.

Never resumes a dynamical state; starts from rest. End-time ramp keys are
recomputed with dt, rather than retaining the source scene's time offset.
"""
import argparse,csv,json,re,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--duration',type=float,required=True)
    p.add_argument('--contact-stiffness',type=float,help='One-variable physical control, not same-model qualification')
    a=p.parse_args()
    for name in (a.tag,a.source):
        if not name.replace('_','').isalnum():raise ValueError('tag')
    if not 1<=a.steps<=12800 or not 0<a.duration<=2:raise ValueError('bounded rest-start follow-up')
    source=ROOT/'results'/('autonomous_film_'+a.source);build=ROOT/'build'/('film_shell_'+a.source)
    compiled=json.loads((source/'compiled.json').read_text());plugin=build/'libReGripFilmShell.so'
    budget=None
    if a.steps>1600:
        benchmark=json.loads((source/'summary.json').read_text())
        if benchmark.get('process_status')!='PASS' or '4' not in benchmark.get('rows',{}):raise RuntimeError('high-resolution run requires completed profiled campaign')
        measured=benchmark['stages']['4']['runtime_s'];count=benchmark['rows']['4']['steps']
        budget=dict(measured_steps=count,measured_seconds=measured,projected_seconds=measured*a.steps/count,hard_limit=480)
        if budget['projected_seconds']*1.05>480:raise RuntimeError('profile projection exceeds bounded budget')
    if sha(plugin)!=compiled['binary_sha256']:raise RuntimeError('binary drift')
    for rel,digest in compiled['sources'].items():
        if sha(source/'sources'/rel)!=digest:raise RuntimeError('immutable source snapshot drift')
    scene=(source/'1/scene.scn').read_text();dt=a.duration/a.steps
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);case=out/'1';case.mkdir()
    scene=scene.replace(str(source/'1'),str(case));scene=re.sub(r' dt="[^"]+"',f' dt="{dt:.17g}"',scene,count=1)
    scene=re.sub(r'times="[^"]+"',f'times="{-dt:.17g} {10-dt:.17g} {20-dt:.17g}"',scene,count=1)
    if a.contact_stiffness is not None:
        if not __import__('math').isfinite(a.contact_stiffness) or a.contact_stiffness<0:raise ValueError('contact stiffness')
        scene,count=re.subn(r'contactStiffness="[^"]+"',f'contactStiffness="{a.contact_stiffness:.17g}"',scene,count=1)
        if count!=1:raise RuntimeError('contact stiffness override not applied')
    (case/'scene.scn').write_text(scene)
    sdk=ROOT/'build/grasp_20261115/sofa_patched'
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_campaign=a.source,
        source_identity=json.loads((source/'identity.json').read_text()),compiled=compiled,plugin=str(plugin),driver_sha256=sha(sdk/'bin/graph_probe'),
        scene_sha256=sha(case/'scene.scn'),tool_sha256=sha(__file__),steps=a.steps,dt=dt,command=__import__('sys').argv,
        profile_budget=budget,contact_stiffness_override=a.contact_stiffness,
        scope='rest start; explicit contact-stiffness override changes physical model; shorter observation window is not a full-cycle gate'))
    process=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(a.steps),'0',plugin],case/'process',480)
    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
    rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    result=dict(process=process,rows=len(rows),expected_rows=a.steps,newton_failed_steps=log.count('Newton-Raphson method failed to converge'),
        process_status='PASS' if process['exit_code']==0 and len(rows)==a.steps and '[ERROR]' not in log else 'FAIL',
        time_convergence='NOT ASSESSED',full_grasp='NOT RUN',energy_closure='BLOCKED')
    if rows:result['last']={k:v for k,v in rows[-1].items() if k!='x'}
    write_json(out/'summary.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
