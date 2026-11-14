"""Read-only archive verification and historical result provenance audit."""
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile
from verification_common import ROOT,RUN,sha,write_json


def main():
    findings=[]
    originals=ROOT/'handover/20261114'
    outer=list(ROOT.parent.glob('ReGrip_*.zip'))
    count=0
    for archive in outer+sorted(originals.glob('*.zip')):
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():continue
                data=(originals/info.filename).read_bytes()
                if data!=z.read(info):findings.append(str(originals/info.filename))
                count+=1
    gate=json.loads((ROOT/'results/physics_validation/gate.json').read_text())
    source_checks={}
    for path,digest in gate['source_sha256'].items():
        data=subprocess.check_output(['git','-C',str(ROOT),'show','68e5acc:'+path])
        source_checks[path]=hashlib.sha256(data).hexdigest()==digest
    old=[]
    for path in sorted((ROOT/'results/physics_validation').glob('*/metrics.json')):
        value=json.loads(path.read_text())
        old.append(dict(path=str(path.relative_to(ROOT)),git_commit=value.get('git_commit'),
                        dirty=value.get('working_tree_dirty'),status=value['status'],plugin_sha256=value.get('plugin_sha256'),
                        diagnostics_sha256=value.get('diagnostics_sha256'),per_trial_source_hashes_present='source_sha256' in value))
    report=dict(archive_members=count,originals_match=not findings,mismatches=findings,
                source_checks_at_68e5acc=source_checks,legacy_gate_checks=len(gate['checks']),legacy_results=old,
                legacy_binaries=dict(plugin=sha(ROOT/'build/plugin/bin/libSofaTangentialV110.so')==gate['plugin_sha256'],
                                     diagnostics=sha(ROOT/'build/diagnostics/libReGripDiagnostics.so')==gate['diagnostics_sha256']),
                caveat='Legacy runs record 519bd5e+dirty; gate source hashes bind the later 68e5acc snapshot, not a clean per-trial source commit')
    write_json(RUN/'source_audit.json',report)
    print('source audit: original members',count,'preserved=',not findings)


if __name__=='__main__':main()
