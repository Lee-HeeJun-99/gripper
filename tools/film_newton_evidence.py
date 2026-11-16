"""New immutable Newton evidence ledger; integrity is not physical approval."""
import argparse,hashlib,json,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--verify',action='store_true');a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    manifest=ROOT/'reports'/('FILM_NEWTON_EVIDENCE_'+a.tag+'.json')
    if a.verify:
        data=json.loads(manifest.read_text());bad=[f for f,h in data['files'].items() if not (ROOT/f).is_file() or sha(ROOT/f)!=h]
        print(json.dumps(dict(integrity='FAIL' if bad else 'PASS',count=len(data['files']),bad=bad)));raise SystemExit(bool(bad))
    if manifest.exists():raise FileExistsError('immutable ledger')
    out=ROOT/'results'/('autonomous_film_newton_evidence_'+a.tag);out.mkdir(exist_ok=False)
    tests={}
    py='/home/ubuntu/miniconda3/envs/robot_ws/bin/python';build=ROOT/'build/film_shell_20261116_final30'
    for name,command in [('design',[py,'-m','unittest','discover','-s','tests','-p','test_film_design.py','-v']),('old_design',[py,'-m','unittest','discover','-s','tests','-p','test_design_regrip.py','-v']),('kernel',[build/'test_film_shell']),('api',[build/'test_film_shell_api']),('mapping',[build/'test_film_slope_mapping']),('ldd',['ldd',build/'libReGripFilmShell.so'])]:tests[name]=logged(command,out/name,120)
    old=json.loads((ROOT/'reports/FILM_RESEARCH_EVIDENCE_20261116_v1.json').read_text());historical=[];unexpected=[]
    for f,h in old['files'].items():
        if (ROOT/f).is_file() and sha(ROOT/f)==h:continue
        found=False
        if not f.startswith('results/'):
            for commit in dict.fromkeys([old.get('source_commit','421cbea'),'421cbea','b86e305','099847b']):
                result=subprocess.run(['git','show',commit+':'+f],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
                if result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==h:found=True;break
        (historical if found else unexpected).append(f)
    write_json(out/'historical_audit.json',dict(old_manifest_unchanged_sha256=sha(ROOT/'reports/FILM_RESEARCH_EVIDENCE_20261116_v1.json'),intentional_current_tree_drift_verified_historically=historical,unexpected_changes=unexpected,raw_status='FAIL' if any(f.startswith('results/') for f in unexpected) else 'PASS',current_old_ledger='Current-source drift is expected and is not represented as current-byte identity'))
    files={}
    roots=[ROOT/'models/film_shell',ROOT/'diagnostics/film_shell',ROOT/'designs/visualizations/film_newton_20261116_v1',ROOT/'reports/film_newton_experiments']+list((ROOT/'results').glob('autonomous_film_*'))
    for folder in roots:
        for f in folder.rglob('*'):
            if f.is_file() and not f.is_symlink():files[str(f.relative_to(ROOT))]=sha(f)
    for pattern in ('tools/film_*.py','tests/test_film*','reports/AUTONOMOUS_RESEARCH_*.md','reports/FILM_SHELL_PHYSICS.md','reports/REGRIP*.md'):
        for f in ROOT.glob(pattern):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    files['build/film_shell_20261116_final30/libReGripFilmShell.so']=sha(build/'libReGripFilmShell.so')
    write_json(manifest,dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='Actual nonlinear-stage evidence and immutable raw; NOT full transient/grasp/energy approval',test_exit_codes={k:v['exit_code'] for k,v in tests.items()},unexpected_historical_changes=unexpected,files=dict(sorted(files.items()))))
    print(json.dumps(dict(manifest=str(manifest),count=len(files),unexpected_historical_changes=unexpected)))

if __name__=='__main__':main()
