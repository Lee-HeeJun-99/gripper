"""Publish small evidence plus hashes; never copies raw states/builds into Git."""
import json,subprocess
from pathlib import Path
from closure_common import ROOT,OUT,BUILD,SOFA,sha,write_json,provenance
def main():
    evidence=ROOT/'reports/closure_evidence';evidence.mkdir(exist_ok=True)
    paths=['gate.json','threefinger/gate.json','threefinger/retry_plan.json','threefinger/retry_result.json','threefinger/field_balance/summary.json','balance_audit.json','native_audit.json','energy_audit.json','memory_audit.json','legacy_integrity.json','optimization_guard.json','environment/summary.json','validation_unit_final/summary.json','validation_golden/summary.json','legacy_units/summary.json','python_recovery/summary.json','python_xml_compare/summary.json','threefinger/wrench/pilot_Tz.json','wrench/convergence_n11q8.json','threefinger/replay/result.json','sanitizers/run_unrestricted/result.json','reference/summary.json','prototype_recovery/result.json']
    for name in paths:
        p=OUT/name
        if p.is_file():write_json(evidence/name.replace('/','__'),json.loads(p.read_text()))
    logs=['validation_unit_final/python_command/stderr.log','validation_unit_final/active/stdout.log','validation_unit_final/invariants/stdout.log','validation_unit_final/frame/stdout.log','sanitizers/run_unrestricted/stdout.log','sdk_memory/stdout.log','energy_v3/stdout.log','environment/frame_linkage/stdout.log','threefinger/field_balance/stdout.log']
    for name in logs:
        p=OUT/name
        if p.is_file():
            text=p.read_text()
            if len(text.encode())<200000:(evidence/name.replace('/','__')).write_text(text)
    binaries={};roots=[BUILD/'release/libReGripClosure.so',BUILD/'matched/libReGripClosure.so',BUILD/'frame/libReGripFrameClosure.so',BUILD/'prototype/libReGripClosure.so',BUILD/'clean/test_closure',BUILD/'invariants/test_closure_invariants',BUILD/'frame/test_closure_frame',ROOT/'build/grasp_20261115/sofa_patched/bin/graph_probe',SOFA/'bin/runSofa-26.06.00',ROOT/'.runtime/python312/lib/libpython3.12.so.1.0',SOFA/'plugins/SofaPython3/lib/libSofaPython3.so']
    for p in roots:
        if p.is_file():binaries[str(p)]=sha(p)
    runtime={}
    for p in roots[:3]+roots[7:9]:
        if not p.exists():continue
        r=subprocess.run(['ldd',str(p)],capture_output=True,text=True,check=False)
        for line in r.stdout.splitlines():
            candidate=line.split('=>',1)[1].strip().split(' ',1)[0] if '=>' in line else ''
            q=Path(candidate)
            if q.is_absolute() and q.is_file():runtime[str(q.resolve())]=sha(q)
    write_json(evidence/'binary_runtime_sha256.json',dict(binaries=binaries,linked_runtime=runtime))
    source_files=set()
    for folder in ('models/closure','models/closure_frame','diagnostics/closure'):
        source_files.update(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for pattern in ('tools/closure_*.py','scenes/closure_*.py','tests/test_closure*'):source_files.update(ROOT.glob(pattern))
    source_files.update(ROOT/n for n in ('AGENTS.md','README.md','.gitignore'))
    source_files.update(ROOT/p for p in json.loads((ROOT/'reports/GRASP_EVIDENCE_MANIFEST.json').read_text())['source_sha256'] if p not in ('AGENTS.md','README.md','.gitignore'))
    sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(source_files) if p.is_file()}
    syntax={}
    for name in sources:
        if name.endswith('.py'):compile((ROOT/name).read_text(),name,'exec');syntax[name]='PASS'
    write_json(evidence/'python_syntax.json',syntax)
    raw={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file()}
    reports={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'reports').glob('CLOSURE*.md'))}
    small={str(p.relative_to(ROOT)):sha(p) for p in sorted(evidence.glob('*')) if p.is_file()}
    write_json(ROOT/'reports/CLOSURE_EVIDENCE_MANIFEST.json',dict(schema=1,start_commit='20249c953a7eef30f5574e4e7d1ce7cb098505f6',evidence_code_commit=provenance()['git_commit'],branch='development/regrip-contact-closure-optimization',raw_root=str(OUT),raw_files=raw,source_sha256=sources,binary_sha256=binaries,runtime_sha256=runtime,report_sha256=reports,evidence_sha256=small,full_grasp_certified=False,grasp_optimization='BLOCKED',scope='measured new campaign plus separately identified historical checks; raw includes failures/timeouts, not only passing selections'))
    print('manifest',len(raw),'raw files',len(sources),'sources',len(small),'small evidence files')
if __name__=='__main__':main()
