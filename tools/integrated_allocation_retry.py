"""Shorter bounded attribution after 10k-step profiler timeout; original failure retained."""
import os
from run_trial import execute_process
from integrated_common import OUT,ROOT,BUILD,SOFA,write_json

out=OUT/'allocation_short';out.mkdir(parents=True,exist_ok=False)
os.environ['LD_PRELOAD']=str(BUILD/'diagnostics/libAllocationProbe.so')
cmd=[str(BUILD/'diagnostics/integrated_driver'),str(SOFA),str(ROOT/'results/next_phase/memory_controls/engine_free/scene.scn'),'1500','0']
r=execute_process(cmd,out,90);write_json(out/'result.json',dict(command=cmd,**r));print(r)
