"""One-time truthful incomplete registry. Never replace existing evidence."""
import json
from stage2_release_gate import ROOT,REQUIRED,expected_baseline
p=ROOT/'models/analytical/release_registry.json'
if p.exists():raise SystemExit('Refusing to overwrite registry')
doc=dict(baseline=expected_baseline(),collision_models_removed=False,qv_forced=False,
    hardware_executed=False,records={k:dict(status='NOT QUALIFIED',domain=d,evidence={},metrics=[],
    scope='UNFINISHED SYSTEM QUALIFICATION') for k,d in REQUIRED.items()})
p.write_text(json.dumps(doc,indent=2)+'\n')
print(p)
