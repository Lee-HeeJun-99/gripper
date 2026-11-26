"""Persist actual unittest exit status/output, no hard-coded PASS."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
command=[sys.executable,str(ROOT/'scripts/test_stage2.py'),'-v']
r=subprocess.run(command,capture_output=True,text=True,timeout=60)
(out/'test.log').write_text(r.stdout+r.stderr)
result=dict(status='PASS' if r.returncode==0 else 'FAIL',scope='SYNTHETIC SOFTWARE TESTS ONLY',exit_code=r.returncode,command=command,
 source_SHA256={str(x.relative_to(ROOT)):sha(x) for x in [Path(__file__),ROOT/'scripts/test_stage2.py',ROOT/'scripts/stage2_release_gate.py',ROOT/'scripts/hardware_records.py']},log_SHA256=sha(out/'test.log'),hardware_executed=False)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
raise SystemExit(r.returncode)
