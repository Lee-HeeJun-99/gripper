"""Isolate observed per-step RSS growth using actual engine control scenes."""
import json
import os
import signal
import threading
import time
from pathlib import Path
import xml.etree.ElementTree as ET
from next_stability import snapshot
from native_scene import generate
from run_trial import execute_process
from verification_common import ROOT,SOFA,BUILD,write_json,provenance,sha,assert_build_current

def main():
    assert_build_current();root=ROOT/'results/next_phase/memory_controls';root.mkdir(parents=True,exist_ok=False);records=[]
    for name,writer,residual,k in [('engine_free',False,False,None),('engine_coupled',False,False,1),
        ('writer_no_residual',True,False,1),('writer_residual',True,True,1)]:
        out=root/name;out.mkdir();generate(out/'scene.scn',k=k)
        tree=ET.parse(out/'scene.scn');scene=tree.getroot()
        for parent in scene.iter('Node'):
            for node in list(parent):
                if node.tag=='PrecisionStateWriter':
                    if not writer:parent.remove(node)
                    else:node.set('writeResidual','true' if residual else 'false')
        tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
        cmd=[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','60000','--hideProgressBar']
        if writer:cmd+=['-l',str(BUILD/'diagnostics/libReGripDiagnostics.so')]
        if k is not None:cmd+=['-l',str(BUILD/'plugin/bin/libSofaTangentialV110.so')]
        cmd += [str(out/'scene.scn')];write_json(out/'command.json',cmd)
        samples=[];stop=threading.Event();started=time.monotonic()
        def monitor():
            while not stop.wait(.1):
                try:pid=json.loads((out/'process.json').read_text())['pid']
                except (OSError,ValueError,KeyError):continue
                row=snapshot(pid)
                if row:
                    row['time']-=started;samples.append(row)
                    if row['rss_kib']>512*1024:os.killpg(pid,signal.SIGKILL);return
        thread=threading.Thread(target=monitor);thread.start()
        try:result=execute_process(cmd,out,120)
        finally:stop.set();thread.join()
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        row=dict(case=name,process=result,samples=samples,completion='60000 iterations done' in log and '[ERROR]' not in log,
            initial_rss_kib=samples[0]['rss_kib'] if samples else None,final_rss_kib=samples[-1]['rss_kib'] if samples else None,
            growth_kib=samples[-1]['rss_kib']-samples[0]['rss_kib'] if samples else None)
        records.append(row);write_json(root/'summary.json',dict(provenance=provenance(),cases=records))
        print(name,row['completion'],row['growth_kib'],flush=True)

if __name__=='__main__':main()
