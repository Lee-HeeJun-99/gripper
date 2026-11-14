"""Compare bounded native-engine vs BatchGUI memory and native physical regression."""
import json
import threading
import time
from next_stability import snapshot
from native_scene import generate
from run_trial import execute_process
from trial_validation import analyze
from verification_common import ROOT,SOFA,BUILD,write_json,sha,provenance,assert_build_current

def measured(out,cmd):
    out.mkdir(parents=True,exist_ok=False);samples=[];stop=threading.Event();started=time.monotonic()
    def monitor():
        while not stop.wait(.1):
            try:pid=json.loads((out/'process.json').read_text())['pid']
            except (OSError,ValueError,KeyError):continue
            row=snapshot(pid)
            if row:row['time']-=started;samples.append(row)
    thread=threading.Thread(target=monitor);thread.start()
    try:result=execute_process(cmd,out,120)
    finally:stop.set();thread.join()
    write_json(out/'command.json',cmd)
    return dict(process=result,samples=samples,growth_kib=samples[-1]['rss_kib']-samples[0]['rss_kib'] if samples else None)

def main():
    assert_build_current();root=ROOT/'results/next_phase/headless';root.mkdir(parents=True,exist_ok=False)
    binary=ROOT/'build/next_headless/regrip_headless';scene=ROOT/'results/next_phase/memory_controls/engine_free/scene.scn'
    cases={}
    for clear in (0,1000):
        out=root/f'clear_{clear}';r=measured(out,[str(binary),str(SOFA),str(scene),'60000',str(clear)])
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        r['completed']=r['process']['exit_code']==0 and '[ERROR]' not in log and '60000 iterations done' in log
        cases[str(clear)]=r;print('headless',clear,r['growth_kib'],flush=True)
    out=root/'native_regression';out.mkdir();generate(out/'scene.scn',k=100)
    cmd=[str(binary),str(SOFA),str(out/'scene.scn'),'6000','0',str(BUILD/'diagnostics/libReGripDiagnostics.so'),str(BUILD/'plugin/bin/libSofaTangentialV110.so')]
    result=execute_process(cmd,out,90);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
    physical=analyze(out,dict(n=11,dt=.0005,load=1e-4,k=100,duration=3,connectors=None),result['exit_code'],log)
    ref=json.loads((ROOT/'reports/revalidation_evidence/metrics/k100.json').read_text())
    difference=abs(physical['tip_deflection_mm']-ref['tip_deflection_mm'])
    write_json(root/'summary.json',dict(provenance=provenance(),cases=cases,native_physics=physical,
        reference_tip_difference_mm=difference,reference_passed=difference<1e-10 and physical['status']=='complete',
        binary_sha256=sha(binary),source_sha256={str(p.relative_to(ROOT)):sha(p) for p in (ROOT/'diagnostics/headless').iterdir() if p.is_file()},
        scope='Diagnostic alternate driver only; does not replace certified batch path or extend physics certificate'))

if __name__=='__main__':main()
