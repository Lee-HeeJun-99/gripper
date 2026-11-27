import json,sys,shutil
from pathlib import Path
b=Path('product_prototype/stage12_integrated').resolve();sys.path.insert(0,str(b/'scripts'))
from baseline_registry import ref,dump
import integrated_release_gate as gate
out=b/'validation/integrated/primaryP1_release6';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
r=gate.audit(json.loads((b/'CURRENT_BASELINE.json').read_text()),json.loads((b/'models/integrated_contract.json').read_text()));r.update(producer=ref(out/'producer.py'),actual_gate_source=ref(b/'scripts/integrated_release_gate.py'),scope_note='Read-only unchanged actual integrated audit. No registry/criteria/control source modified. New actual P1 keyed Ground/Base fixture work does not satisfy full system gates.');dump(out/'summary.json',r);print(json.dumps(r));raise SystemExit(0 if not r['errors'] else 2)
