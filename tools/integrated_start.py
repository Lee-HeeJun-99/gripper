import json
import socket
import subprocess
import sys
from integrated_common import OUT,ROOT,sha,write_json,provenance

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'reports/NEXT_EVIDENCE_MANIFEST.json').read_text());errors=[]
    for key in ('source_sha256','binary_sha256','evidence_sha256','report_sha256','figure_sha256'):
        errors.extend(p for p,h in manifest[key].items() if sha(ROOT/p)!=h)
    dns={}
    for host in ('pypi.org','repo.anaconda.com'):
        try:dns[host]=socket.gethostbyname(host)
        except OSError as e:dns[host]=str(e)
    cmd=[sys.executable,'-m','pip','install','--isolated','--retries','0','--timeout','8','--target',str(ROOT/'.python-deps'),'optuna>=3.6,<5']
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=45);(OUT/'pip.log').write_text(p.stdout+p.stderr)
    write_json(OUT/'start.json',dict(provenance=provenance(),previous_evidence_errors=errors,dns=dns,pip_command=cmd,pip_exit=p.returncode))
    if errors:raise RuntimeError('previous evidence mismatch '+str(errors))
    print('Previous evidence verified; DNS:',dns)

if __name__=='__main__':main()
