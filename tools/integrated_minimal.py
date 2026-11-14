"""Minimal engine repro without any ReGrip ForceField or observer."""
import os
from integrated_common import ROOT,SOFA,OUT,BUILD,write_json,sha
from run_trial import execute_process

root=OUT/'minimal_engine';root.mkdir(parents=True,exist_ok=False)
os.environ['REGRIP_GRAPH_PROBE']='1'
cmd=[str(BUILD/'diagnostics/integrated_driver'),str(SOFA),str(ROOT/'scenes/integrated/minimal_mapping_graph.scn'),'60000','1']
r=execute_process(cmd,root,120);write_json(root/'result.json',dict(command=cmd,source_sha256=sha(ROOT/'scenes/integrated/minimal_mapping_graph.scn'),**r));print(r)
