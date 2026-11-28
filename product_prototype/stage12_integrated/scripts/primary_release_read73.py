"""Read-only pinned official release audit. Unique output; no metadata writes."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,ref,dump
from integrated_release_gate import audit
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');b=json.loads((ROOT/'CURRENT_BASELINE.json').read_text());c=json.loads((ROOT/'models/integrated_contract.json').read_text());r=audit(b,c);r.update(producer=ref(out/'producer.py'),baseline=ref(ROOT/'CURRENT_BASELINE.json'),contract=ref(ROOT/'models/integrated_contract.json'),pinned_gate=ref(ROOT/'scripts/integrated_release_gate.py'),candidate_scope='Official unchangedgolden baselinecontract only; NOT qualification of new primaryshoulderCAD. New primaryactualphysicalchecks are separate and unqualified.');dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],errors=r['errors'])));sys.exit(0 if not r['errors'] else 2)
