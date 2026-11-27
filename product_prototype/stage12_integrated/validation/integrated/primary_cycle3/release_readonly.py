import sys,json,shutil
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'product_prototype/stage12_integrated/scripts'))
from baseline_registry import ROOT,ref,dump
import integrated_release_gate as gate
out=ROOT/'validation/integrated/primaryP1_release3';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
r=gate.audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()));r.update(producer=ref(out/'producer.py'),unchanged_gate=ref(Path(gate.__file__)),scope='Read-only unchanged baseline integrated release audit; no current P1 gate promotion')
dump(out/'summary.json',r);print(json.dumps({'status':r['status'],'errors':len(r['errors'])}));raise SystemExit(2 if r['errors'] else 0)
