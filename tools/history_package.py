"""Read-only diff audit; output contains paths/status, never credential values."""
import json,re,subprocess
from history_common import ROOT,write_json
def main():
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).splitlines()
    paths=set(git('diff','--name-only','5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa'))|set(git('ls-files','--others','--exclude-standard'));issues=[]
    patterns=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'AKIA[0-9A-Z]{16}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')]
    for name in sorted(paths):
        p=ROOT/name
        if name.startswith(('build/','results/','.runtime/','.python-deps/','.venv/')):issues.append(dict(path=name,reason='generated/raw/cache path'))
        if p.is_file():
            if p.stat().st_size>5*1024*1024:issues.append(dict(path=name,reason='larger than5MiB'))
            text=p.read_text(errors='ignore')
            if any(pattern.search(text) for pattern in patterns):issues.append(dict(path=name,reason='credential/private-key pattern'))
    ancestor=subprocess.run(['git','merge-base','--is-ancestor','5dd3eafbbd459abcdc1c2c3ad9654f00c01545fa','HEAD'],cwd=ROOT).returncode==0
    result=dict(status='PASS' if not issues and ancestor else 'FAIL',baseline_ancestor_preserved=ancestor,checked_paths=len(paths),issues=issues,limits='pattern scan is not proof against arbitrary secrets; no external data transfer, push or deletion performed',raw_build_ignored=True)
    write_json(ROOT/'reports/history_evidence/package_audit.json',result);print(result)
if __name__=='__main__':main()
