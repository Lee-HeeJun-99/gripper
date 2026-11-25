"""Final bounded-session evidence, tool binary identity, logs and size guard."""
import datetime,hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 out=ROOT/'validation/session_final';out.mkdir(exist_ok=False)
 logs=out/'logs';logs.mkdir()
 for name in ['revB','revC','revD','revE','revF','revG','revH']:
  p=Path('/tmp')/f'regrip_stage1_{name}.log'
  if p.is_file():shutil.copyfile(p,logs/p.name)
 p=Path('/tmp/regrip_stage1_capture.log')
 if p.is_file():shutil.copyfile(p,logs/p.name)
 binary=Path('/tmp/regrip_stage1_ocp/OCP/OCP.cpython-310-x86_64-linux-gnu.so')
 result=dict(source_head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),toolchain=dict(OCP='cadquery-ocp7.9.3.1.1',VTK='9.6.2',binary_path=str(binary),binary_sha256=sha(binary),installation_scope='/tmp only; no system/robot_ws/SOFA SDK modification'),release='STAGE1_DESIGN_RELEASE_FAIL',Native_executed=False,hardware_measured=False,background_continuation=False,per_job_runtime='not recorded; do not infer from STEP timestamps',old_research_queue_modified=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2))
 files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in str(p)]
 assert not [str(p) for p in files if p.stat().st_size>=50_000_000]
 (out/'manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)},indent=2))
 print(json.dumps(dict(files=len(files),largest_bytes=max(p.stat().st_size for p in files),release=result['release'])))
if __name__=='__main__':main()
