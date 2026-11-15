"""Same-parent process monitor; never trusts a PID from another invocation."""
import json,os,time,threading
from pathlib import Path
from verification_common import write_json
class Monitor:
    def __init__(self,out):self.out=out;self.stop=threading.Event();self.samples=[];self.error=None;self.start=time.monotonic();self.thread=threading.Thread(target=self.poll,daemon=True)
    def poll(self):
        while not self.stop.wait(2):
            try:
                metadata=self.out/'process.json'
                if not metadata.exists():continue
                pid=json.loads(metadata.read_text())['pid'];proc=Path('/proc')/str(pid);status={r.split(':')[0]:r.split(':',1)[1].strip() for r in (proc/'status').read_text().splitlines() if ':'in r}
                if int(status['PPid'])!=os.getpid():raise ValueError('PID is not this runner child')
                sample=dict(wall_s=time.monotonic()-self.start,pid=pid,rss_kib=int(status['VmRSS'].split()[0]),fd=len(list((proc/'fd').iterdir())))
                rollup={r.split(':')[0]:r.split(':',1)[1].strip() for r in (proc/'smaps_rollup').read_text().splitlines() if ':'in r}
                sample.update(pss_kib=int(rollup['Pss'].split()[0]),private_dirty_kib=int(rollup['Private_Dirty'].split()[0]));self.samples.append(sample)
            except (FileNotFoundError,ProcessLookupError):pass
            except (ValueError,OSError,KeyError)as e:self.error=str(e)
    def finish(self):
        self.stop.set();self.thread.join(timeout=3);write_json(self.out/'resource_samples.json',dict(samples=self.samples,monitor_error=self.error,parent_pid=os.getpid(),scope='actual same-parent/proc sampling,2second cadence; not allocation traceback or hours-soak proof'))
