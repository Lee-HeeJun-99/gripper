"""Archive measured evidence; integrity success is NOT physical certification."""
import argparse,json,subprocess,sys
from pathlib import Path
import numpy as np
from research_common import ROOT,OUT,BUILD,identity,sha,write_json
BASE='63970172ad196e0add3ad42a67ccaee4c7a8975e'
DEST=ROOT/'reports/autonomous_evidence'
MANIFEST=ROOT/'reports/AUTONOMOUS_RESEARCH_EVIDENCE_MANIFEST.json'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def resources():
    rows={}
    for p in sorted((OUT/'grasp').glob('*/resource_samples.json')):
        samples=json.loads(p.read_text())['samples']
        if not samples:continue
        row={'sample_count':len(samples),'sampled_wall_s':samples[-1]['wall_s']}
        for key in ('rss_kib','pss_kib','private_dirty_kib','fd'):
            pairs=[(s['wall_s'],s[key])for s in samples if s.get(key)is not None]
            if not pairs:continue
            t,y=np.array(pairs).T
            row[key]=dict(first=float(y[0]),last=float(y[-1]),maximum=float(y.max()),minimum=float(y.min()),ordinary_least_squares_per_wall_s=float(np.polyfit(t,y,1)[0])if len(t)>1 else None)
        rows[p.parent.name]=row
    result=dict(scope='bounded runs,2second proc samples; no live-allocation traceback or long-soak/no-leak certificate',status='EXPERIMENTAL',cases=rows)
    write_json(DEST/'resources.json',result)
def plot():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d=json.loads((OUT/'assessment.json').read_text());names=[];motion=[];loss=[];limits=[]
    for n,r in d['comparisons'].items():
        if 'relative_difference'not in r:continue
        names.append(n);motion.append(100*r['relative_difference']['hold_displacement_mm']);loss.append(100*r['same_hold_observables']['friction_dissipation']['relative_difference']);limits.append(100*r['limit'])
    fig,axes=plt.subplots(2,1,figsize=(10,7),sharex=True)
    for ax,y,title in zip(axes,[motion,loss],['SOFA hold displacement relative difference','Same-hold cumulative friction-loss difference']):
        ax.bar(np.arange(len(names)),y,color=['#a33'if v>lim else'#367'for v,lim in zip(y,limits)]);ax.plot(np.arange(len(names)),limits,'k_',markersize=24,label='unchanged limit');ax.set_ylabel('percent');ax.set_title(title);ax.legend();ax.grid(axis='y',alpha=.2)
    axes[-1].set_xticks(np.arange(len(names)));axes[-1].set_xticklabels(names,rotation=35,ha='right');fig.tight_layout();fig.savefig(DEST/'convergence.png',dpi=140);plt.close(fig)
def create():
    DEST.mkdir(exist_ok=True);resources();plot();ident=identity();write_json(DEST/'compiled_identity.json',ident)
    original=['models/conservative_beam','models/contact_history','models/contact_birth','models/closure','models/closure_frame','models/grasp','models/stabilization','tools/research_trial.py']
    changes=git('diff','--name-only',BASE,'--',*original).splitlines()
    if changes:raise ValueError('historical code changed: '+repr(changes))
    write_json(DEST/'preservation.json',dict(status='PASS',baseline=BASE,paths=original,tracked_content_diff=changes,warning='current content preservation; temporary runner filename collision was restored,see report'))
    files=[p for p in OUT.rglob('*')if p.is_file()]
    files+=list(BUILD.glob('*.so'))+list(BUILD.glob('*.inc'))+[BUILD/'build_manifest.json']
    for folder in ('models/material_point_contact','models/contact_kinematics','diagnostics/autonomous'):
        files +=[p for p in(ROOT/folder).rglob('*')if p.is_file()and'__pycache__'not in p.parts]
    files+=[p for p in(ROOT/'tools').glob('research_*.py')]+[ROOT/'tools/autonomous_trial.py',ROOT/'tests/test_material_point.cpp',ROOT/'tests/test_hermite_map.cpp',ROOT/'tests/test_autonomous_guards.py']
    files +=[p for p in DEST.iterdir()if p.is_file()]
    unique=sorted(set(p.resolve()for p in files))
    hashes={str(p.relative_to(ROOT)):sha(p)for p in unique}
    write_json(MANIFEST,dict(schema=1,baseline=BASE,source_checkpoint_commit=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status='integrity index only; physical research FAIL/EXPERIMENTAL',campaign=str(OUT.relative_to(ROOT)),compiled_identity=ident,files=hashes,raw_bytes=sum(p.stat().st_size for p in OUT.rglob('*')if p.is_file()),scope='all campaign raw and selected compiled/source/evidence; report prose excluded to avoid final-commit self reference'))
    print('indexed',len(hashes),'artifacts')
def verify():
    d=json.loads(MANIFEST.read_text());errors=[]
    for name,digest in d['files'].items():
        p=ROOT/name
        if not p.is_file()or sha(p)!=digest:errors.append(name)
    result=dict(status='FAIL'if errors else'PASS',checked=len(d['files']),errors=errors,scope='SHA256 integrity only,not physics')
    print(json.dumps(result));return bool(errors)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--verify',action='store_true');args=parser.parse_args()
    if args.verify:sys.exit(verify())
    create()
