"""Refresh documentation checksums after editorial review; never edits experiment data."""
import json
from pathlib import Path
import re
from verification_common import ROOT,RUN,SOFA,BUILD,sha,source_hashes,write_json


def main():
    reports=ROOT/'reports';evidence=reports/'revalidation_evidence'
    hashes=source_hashes();syntax={}
    for name in hashes:
        if name.endswith('.py'):
            compile((ROOT/name).read_text(),str(ROOT/name),'exec');syntax[name]='PASS'
    write_json(evidence/'final_source_sha256.json',hashes)
    write_json(evidence/'final_python_syntax.json',syntax)
    write_json(evidence/'engine_identity.json',dict(executable=str(SOFA/'bin/runSofa-26.06.00'),
        executable_sha256=sha(SOFA/'bin/runSofa-26.06.00'),build_manifest_sha256=sha(BUILD/'build_manifest.json')))
    check=reports/'10_FINAL_CODE_REVIEW.md'
    body=check.read_text();body=re.sub(r'Python \d+개 파일 syntax compile',f'Python {len(syntax)}개 파일 syntax compile',body)
    check.write_text(body)
    names=sorted(p for p in reports.glob('[0-9][0-9]_*.md'))+[reports/'FINAL_VERIFICATION_REPORT.md']
    write_json(reports/'REVALIDATION_EVIDENCE_MANIFEST.json',dict(run=str(RUN.relative_to(ROOT)),
        files={str(p.relative_to(ROOT)):sha(p) for p in evidence.rglob('*') if p.is_file()},
        report_sha256={p.name:sha(p) for p in names}))
    print('syntax PASS',len(syntax),'source files; evidence hashes refreshed')


if __name__=='__main__':main()
