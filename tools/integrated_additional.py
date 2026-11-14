from dataclasses import replace
import json
from integrated_trial import Config,run
from integrated_common import OUT,write_json

root=OUT/'additional_convergence';root.mkdir(parents=True,exist_ok=False);d=Config(k=100);records={}
for name,c in [('L2_mesh',replace(d,nodes=21,connectors=tuple(range(2,21,2)))),('L2_halfdt',replace(d,dt=.00025)),('L2_repeat',d),('L2_extended',replace(d,duration=18))]:
    records[name]=run(root/name,c)
    write_json(root/'summary.json',records)
