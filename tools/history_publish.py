"""Publish small evidence, stream hashes, preserve all historical manifests."""
import json,hashlib,subprocess
from pathlib import Path
from history_common import ROOT,OUT,BUILD,PLUGIN,write_json,identity
def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def old_audit():
    old=json.loads((ROOT/'reports/CONSERVATIVE_BEAM_EVIDENCE_MANIFEST.json').read_text());changes=[];checked=0
    for group in ('source_sha256','report_sha256','binary_sha256','runtime_sha256','evidence_sha256','raw_files'):
        for name,r in old[group].items():
            checked+=1;expected=r['sha256'] if isinstance(r,dict) else r;p=ROOT/name
            if not p.is_file() or digest(p)!=expected:changes.append(dict(group=group,path=name))
    allowed={'.gitignore','README.md','AGENTS.md','PROGRESS.md','VALIDATION.md'};unexpected=[r for r in changes if r['path'] not in allowed]
    return dict(original_verifier_status='FAIL' if changes else 'PASS',original_physics_raw_integrity='PASS' if not unexpected else 'FAIL',checked=checked,changes=changes,unexpected=unexpected,policy='original manifest never rewritten; documentation/ignore deltas explicit')
def main():
    ident=identity();evidence=ROOT/'reports/history_evidence';evidence.mkdir(exist_ok=True)
    auxiliary={}
    for name in ('structural_interface','prescribed_reference_final','energy_partial','sanitizer_final','replay','validation_unit_history_final','validation_golden_history'):
        p=OUT/name;file=p/'metrics.json' if (p/'metrics.json').exists() else p/'summary.json'
        if file.exists():auxiliary[name]=json.loads(file.read_text())
    write_json(evidence/'auxiliary.json',auxiliary);write_json(evidence/'historical_integrity.json',old_audit())
    compact={}
    for p in sorted((OUT/'grasp').iterdir()):
        f=p/'metrics.json' if (p/'metrics.json').exists() else p/'recovered_metrics.json'
        if f.exists():
            r=json.loads(f.read_text());compact[p.name]={k:v for k,v in r.items() if k not in ('identity','artifacts')};compact[p.name]['compiled_binary_sha256']=r['identity']['history_build']['binary_sha256'];compact[p.name]['raw_metrics_path']=str(f.relative_to(ROOT));compact[p.name]['raw_metrics_sha256']=digest(f)
    write_json(evidence/'actual_cases.json',compact)
    sources=[p for folder in ('models/contact_history','models/contact_birth','diagnostics/contact_history','tests/contact_history_extra') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]+list((ROOT/'tools').glob('history_*.py'))+[ROOT/'tests/test_contact_history.cpp',ROOT/'tests/test_history_assess.py']
    reports=list((ROOT/'reports').glob('HISTORY_*.md'))+list((ROOT/'reports').glob('CONTACT_HISTORY_*.md'))
    binaries=[PLUGIN,ROOT/'build/history_20261115/extra/history_prescribed',ROOT/'build/history_20261115/history_stored_energy',ROOT/'build/history_20261115/history_kernel_sanitized_final']
    raw={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in OUT.rglob('*') if p.is_file() and not p.name.endswith('.partial') and not any(part.startswith('.') or part=='__pycache__' for part in p.relative_to(OUT).parts)}
    manifest=dict(base_commit='5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa',code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),full_grasp_certified=False,grasp_optimization='BLOCKED',compiled_build_manifest=str((BUILD/'build_manifest.json').relative_to(ROOT)),compiled_build_manifest_sha256=digest(BUILD/'build_manifest.json'),source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},report_sha256={str(p.relative_to(ROOT)):digest(p) for p in reports},binary_sha256={str(p.relative_to(ROOT)):digest(p) for p in binaries if p.exists()},evidence_sha256={str(p.relative_to(ROOT)):digest(p) for p in evidence.iterdir() if p.is_file()},raw_files=raw,readme='raw/build/env remain on external disk and are Git-ignored; metadata/source versions are not silently pooled; final docs commit may follow this code commit')
    write_json(ROOT/'reports/CONTACT_HISTORY_EVIDENCE_MANIFEST.json',manifest);print('published',len(raw),'raw files; overall grasp remains blocked')
if __name__=='__main__':main()
