"""Read-only review of the Git index, without displaying secret contents."""
import json
from pathlib import Path
import re
import subprocess
from audit_publish import PATTERNS
from verification_common import ROOT


def main():
    def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
    problems=[];count=0;total=0
    for entry in git('ls-files','-s','-z').split(b'\0'):
        if not entry:continue
        metadata,path=entry.split(b'\t',1);mode,sha,stage=metadata.decode().split();name=path.decode()
        if stage!='0':problems.append(dict(path=name,rule='unresolved_merge'));continue
        data=git('cat-file','blob',sha);count+=1;total+=len(data)
        if len(data)>1024**2:problems.append(dict(path=name,rule='file_over_1MiB'))
        if data.startswith(b'\x7fELF') or re.search(r'(^|/)(build|__pycache__|\.python-deps|\.conda-pkgs|\.conda-envs|\.venv[^/]*)/',name):
            problems.append(dict(path=name,rule='generated_artifact'))
        if re.search(r'(^|/)(\.env|credentials|id_rsa|id_ed25519)$|\.(pem|p12|pfx)$',name):
            problems.append(dict(path=name,rule='credential_filename'))
        for rule,pattern in PATTERNS.items():
            if re.search(pattern,data):problems.append(dict(path=name,rule=rule))
    print(json.dumps(dict(files=count,total_bytes=total,problems=problems),ensure_ascii=False))
    return int(bool(problems))


if __name__=='__main__':raise SystemExit(main())
