"""Inspect reachable Git history for generated artifacts, large files and secrets.

Reports locations/rule names only; never prints suspected credential values.
This is a heuristic review, not a proof that every possible secret is absent.
"""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import zipfile

ROOT=Path(__file__).resolve().parents[1]
LIMIT=1024*1024  # Conservative publishing threshold for experiment CSV.
PATTERNS={
    'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'aws_access_key':rb'(?:AKIA|ASIA)[A-Z0-9]{16}',
    'github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})',
    'slack_token':rb'xox[baprs]-[A-Za-z0-9-]{20,}',
    'credential_assignment':rb'''(?im)^\s*(?:export\s+)?[A-Z_]*(?:TOKEN|PASSWORD|SECRET|API_KEY)\s*=\s*["']?[A-Za-z0-9/+_=.-]{16,}''',
}


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def main():
    objects={}
    for commit in git('rev-list','--all').decode().splitlines():
        for entry in git('ls-tree','-rz','--full-tree',commit).split(b'\0'):
            if not entry:continue
            meta,path=entry.split(b'\t',1)
            _,kind,sha=meta.decode().split()
            if kind=='blob':objects.setdefault((sha,path.decode()),commit)
    report=dict(csv_threshold_bytes=LIMIT,history_commits=git('rev-list','--count','--all').decode().strip(),
                large_csv_history=[],large_csv_head=[],large_blob_history=[],generated_history=[],
                credential_findings=[],archive_members_scanned=0)
    head_paths={entry.split(b'\t',1)[1].decode() for entry in git('ls-tree','-rz','HEAD').split(b'\0') if entry}
    def scan(data,location,depth=0):
        for name,pattern in PATTERNS.items():
            if re.search(pattern,data):report['credential_findings'].append(dict(path=location,rule=name))
        if depth<3 and data[:4]==b'PK\x03\x04':
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    for member in archive.infolist():
                        if member.is_dir():continue
                        if member.file_size>20*1024*1024:
                            report['credential_findings'].append(dict(path=location+'!'+member.filename,rule='archive_member_too_large_to_scan'))
                            continue
                        report['archive_members_scanned']+=1
                        scan(archive.read(member),location+'!'+member.filename,depth+1)
            except zipfile.BadZipFile:
                report['credential_findings'].append(dict(path=location,rule='unreadable_zip'))
    for (sha,path),commit in objects.items():
        data=git('cat-file','blob',sha)
        item=dict(path=path,bytes=len(data),blob=sha,seen_in_commit=commit)
        if path.lower().endswith('.csv') and len(data)>LIMIT:
            report['large_csv_history'].append(item)
            if path in head_paths and git('rev-parse','HEAD:'+path).decode().strip()==sha:
                report['large_csv_head'].append(item)
        if len(data)>10*1024*1024:report['large_blob_history'].append(item)
        if re.search(r'(^|/)(build|__pycache__|\.venv[^/]*|\.conda-pkgs|\.python-deps|node_modules)/',path) or data.startswith(b'\x7fELF') or path.endswith(('.pyc','.o','.a','.so','.dll','.exe')):
            report['generated_history'].append(item)
        if re.search(r'(^|/)(\.env(?:\.[^/]*)?|id_rsa|id_ed25519|credentials)(/|$)|\.(?:pem|p12|pfx)$',path):
            report['credential_findings'].append(dict(path=path,rule='credential_filename'))
        scan(data,path)
    report['head_commit']=git('rev-parse','HEAD').decode().strip()
    report['secret_scan_scope']='Reachable Git blobs and nested ZIP members; heuristic patterns and credential filenames'
    out=ROOT/'reports/GIT_PUBLISH_AUDIT.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False))
    print(json.dumps({key:len(report[key]) for key in ['large_csv_history','large_csv_head','large_blob_history','generated_history','credential_findings']}))
    print('Report:',out)
    return int(bool(report['credential_findings'] or report['generated_history'] or report['large_blob_history']))


if __name__=='__main__':raise SystemExit(main())
