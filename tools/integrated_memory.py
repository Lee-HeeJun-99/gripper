"""Allocator and live C++ allocation attribution; RSS alone is not a leak verdict."""
import json
import os
import threading
import time
from pathlib import Path
from run_trial import execute_process
from integrated_common import OUT,BUILD,SOFA,write_json,provenance

def main():
    root=OUT/'memory';root.mkdir(parents=True,exist_ok=False);results={}
    scene=Path(__file__).resolve().parents[1]/'results/next_phase/memory_controls/engine_free/scene.scn'
    for name,steps,trim,profile in [('allocator_default',60000,0,False),('allocator_trim',60000,1,False),('allocation_stacks',10000,0,True)]:
        out=root/name;out.mkdir();done=threading.Event();samples=[]
        def monitor():
            while not done.wait(.2):
                try:
                    pid=json.loads((out/'process.json').read_text())['pid'];p=Path(f'/proc/{pid}')
                    fields={k:int(v.split()[0]) for line in (p/'smaps_rollup').read_text().splitlines() if ':' in line for k,v in [line.split(':',1)]}
                    samples.append(dict(time=time.monotonic(),rss_kib=fields['Rss'],pss_kib=fields['Pss'],private_dirty_kib=fields['Private_Dirty'],fds=len(list((p/'fd').iterdir()))))
                except (OSError,ValueError,KeyError):continue
        thread=threading.Thread(target=monitor);thread.start()
        old=os.environ.get('LD_PRELOAD')
        if profile:os.environ['LD_PRELOAD']=str(BUILD/'diagnostics/libAllocationProbe.so')
        try:
            cmd=[str(BUILD/'diagnostics/integrated_driver'),str(SOFA),str(scene),str(steps),str(trim)]
            result=execute_process(cmd,out,150)
        finally:
            if old is None:os.environ.pop('LD_PRELOAD',None)
            else:os.environ['LD_PRELOAD']=old
            done.set();thread.join()
        log=(out/'stdout.log').read_text();rows=[json.loads(line[4:]) for line in log.splitlines() if line.startswith('MEM ')]
        results[name]=dict(process=result,command=cmd,mallinfo=rows,proc_samples=samples,completed=f'{steps} iterations done' in log and result['exit_code']==0)
        write_json(root/'summary.json',dict(provenance=provenance(),cases=results));print(name,result['exit_code'],rows[-3:] if rows else [],flush=True)

if __name__=='__main__':main()
