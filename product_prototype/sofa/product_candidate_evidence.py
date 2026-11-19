"""Append-only product campaign evidence;prior immutable hashes must still match."""
import argparse,json,shutil,subprocess
from pathlib import Path
from analyse import BASE,sha
from observer_identity import compiled_alarm_window
ROOT=BASE.parent

def immutable(name):
    return name.startswith(('product_prototype/results/','product_prototype/reports/evidence_','product_prototype/cad/build_','product_prototype/meshes/','product_prototype/drawings/','/home/ubuntu/SOFA/'))

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--prior',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();prior=BASE/'reports'/a.prior/'manifest.json';old=json.loads(prior.read_text());files={k:v for k,v in old['files'].items() if immutable(k)};bad=[k for k,v in files.items() if not (ROOT/k).is_file() or sha(ROOT/k)!=v]
    if bad:raise ValueError('prior immutable evidence mismatch:'+str(bad))
    out=BASE/'reports'/a.name;out.mkdir(exist_ok=False);cases={}
    for case in a.cases:
        folder=BASE/'results'/case;summary=folder/'summary.json'
        if not summary.exists():raise ValueError('Missing final summary;do not archive partial run as complete:'+case)
        shutil.copy2(summary,out/(case+'.json'));cases[case]=dict(raw=str(folder.relative_to(ROOT)),summary_sha256=sha(summary))
        for f in folder.rglob('*'):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    for name in ('guide_motion_clearance.py','guide_sector_candidate.py','guide_clearance_event.py','product_candidate_evidence.py','mechanism_candidates.py','guide_pair_coupon.py','run_alarm_window.py','b3_clearance_comparison.py','guide_chord_audit.py','guide_pair_time_assess.py','b3_clearance_plot.py','guide_route_identity.py','observer_identity.py','run_native.py'):
        shutil.copy2(BASE/'sofa'/name,out/name)
    for f in compiled_alarm_window():files[str(f.relative_to(ROOT))]=sha(f)
    physical=BASE/'cad/build_default_control332/libReGripProductSequence.so'
    if sha(physical)!='3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0':raise ValueError('physical controller binary changed')
    files[str(physical.relative_to(ROOT))]=sha(physical)
    for category in ('meshes','drawings'):
        for f in (BASE/category/'precurve_distal40_route_audit_v10').rglob('*'):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    for f in out.iterdir():
        if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
    result=dict(scope='Product functionality/clearance diagnostics,NOT final physics/fabrication qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),prior_manifest_sha256=sha(prior),prior_immutable_audit=dict(checked=sum(immutable(k) for k in old['files']),mismatches=bad),cases=cases,files=files)
    (out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(files=len(files),cases=len(cases),prior_checked=result['prior_immutable_audit']['checked'],mismatches=bad)))

if __name__=='__main__':main()
