"""Bounded live-SOFA soak with procfs observations, no whole-engine leak claim."""
import json
import os
from pathlib import Path
import signal
import threading
import time
from run_trial import run_trial
from trial_validation import verify_artifacts,TrialError
from verification_common import ROOT,write_json,provenance
from next_common import NEXT

OUT=NEXT/'stability'

def snapshot(pid):
    try:
        lines=Path(f'/proc/{pid}/status').read_text().splitlines()
        values={line.split(':')[0]:line.split(':')[1].strip() for line in lines if ':' in line}
        return dict(time=time.monotonic(),rss_kib=int(values.get('VmRSS','0 kB').split()[0]),
            fds=len(list(Path(f'/proc/{pid}/fd').iterdir())),threads=int(values['Threads']))
    except (FileNotFoundError,ProcessLookupError,PermissionError):return None

def main():
    OUT.mkdir(parents=True,exist_ok=False);start=time.monotonic();before=len(list(Path('/proc/self/fd').iterdir()));records=[];samples=[];stopped=[]
    target=OUT/'long_simulation';done=threading.Event()
    def observe():
        while not done.wait(.2):
            try:pid=json.loads((target/'process.json').read_text())['pid']
            except (OSError,ValueError,KeyError):continue
            row=snapshot(pid)
            if row:
                row['time']-=start;samples.append(row)
                disk=sum(p.stat().st_size for p in target.iterdir() if p.is_file())
                if row['rss_kib']>512*1024 or row['fds']>256 or disk>512*1024**2:
                    stopped.append(dict(row=row,disk_bytes=disk));os.killpg(pid,signal.SIGKILL);return
    watcher=threading.Thread(target=observe);watcher.start()
    try:long=run_trial(target,k=100,duration=30,timeout=120)
    finally:done.set();watcher.join()
    for i in range(12):
        if time.monotonic()-start>240:break
        r=run_trial(OUT/f'repeat_{i:02d}',k=1,duration=.05,timeout=15)
        verify_artifacts(OUT/f'repeat_{i:02d}')
        try:os.kill(r['pid'],0);reaped=False
        except ProcessLookupError:reaped=True
        records.append(dict(status=r['status'],execution_completed=r['execution_completed'],pid=r['pid'],reaped=reaped))
    errors={}
    # Copies of deliberately broken metadata; original valid trial never modified.
    bad=OUT/'invalid_json';bad.mkdir();(bad/'metrics.json').write_text('{"status":')
    try:verify_artifacts(bad);errors['invalid_json']=False
    except (json.JSONDecodeError,TrialError):errors['invalid_json']=True
    bad=OUT/'changed_hash';bad.mkdir();(bad/'sample.csv').write_text('corrupt\n')
    write_json(bad/'metrics.json',dict(artifact_sha256={'sample.csv':'0'*64}))
    try:verify_artifacts(bad);errors['changed_hash']=False
    except TrialError:errors['changed_hash']=True
    after=len(list(Path('/proc/self/fd').iterdir()))
    plateau=samples[len(samples)//2:]
    checks=dict(long_simulation_equilibrium=long['status']=='complete',no_resource_limit_kill=not stopped,
        repetitions=len(records)==12 and all(r['execution_completed'] and r['reaped'] for r in records),
        parent_fd_balance=before==after,**errors)
    write_json(OUT/'summary.json',dict(provenance=provenance(),checks=checks,passed=all(checks.values()),
        scope='bounded 30-second simulation plus 12 short native-SOFA processes; NOT hours-long soak or full-engine ASan/LSan',
        wall_seconds=time.monotonic()-start,before_fds=before,after_fds=after,samples=samples,repeats=records,limit_stops=stopped,
        peak_child_rss_kib=max((r['rss_kib'] for r in samples),default=None),
        late_rss_range_kib=max((r['rss_kib'] for r in plateau),default=0)-min((r['rss_kib'] for r in plateau),default=0),
        peak_child_fds=max((r['fds'] for r in samples),default=None),long_metrics=str(target/'metrics.json')))
    print(checks,flush=True)

if __name__=='__main__':main()
