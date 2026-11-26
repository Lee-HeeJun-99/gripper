"""Read-only re-evaluation of actual saved states and release audit."""
import json,hashlib,sys
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,dump,ref
import flexible_rail_distributed as model
from integrated_release_gate import audit
out=ROOT/'validation/finger'/sys.argv[1]
s=json.loads((out/'summary.json').read_text());inputs=json.loads((out/'inputs.json').read_text())
for item in inputs['inputs']:
    assert hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()==item['SHA256']
assert len(s['rows'])==9
certificates=[]
for r in s['rows']:
    u=np.r_[r['rail_q'],r['PET_q']]
    gaps={kind:model.contact.exact_min(r['n'],u,kind)[0] for kind in ('interface','front','back')}
    assert min(gaps.values())>=s['criteria']['gap_m_min']
    assert r['KKT_force_equivalent_N']<s['criteria']['force_N_max']
    assert r['root_force_balance_N']<s['criteria']['force_N_max']
    assert r['root_moment_balance_Nm']<s['criteria']['moment_Nm_max']
    assert r['complementarity_relative']<s['criteria']['complementarity_relative_max']
    assert r['static_energy_relative_error']<s['criteria']['energy_relative_max']
    certificates.append(dict(n=r['n'],force_N=r['force_N'],continuous_gaps_m=gaps,status=r['status']))
assert sum(r['status']=='FAIL' for r in s['rows'])==2
assert s['status']=='FAIL' and all(s['controls'].values())
a=audit(json.loads((ROOT/'CURRENT_BASELINE.json').read_text()),json.loads((ROOT/'models/integrated_contract.json').read_text()))
assert a['status']=='INTEGRATED_NOT_QUALIFIED'
dump(out/'verification.json',dict(status='PASS',scope='Independent reread of actual saved states, not reversal of research FAIL',summary=ref(out/'summary.json'),producer=ref(Path(__file__)),certificates=certificates,analysis_execution=dict(actually_executed=True,exit_code=2,timeout_s=420,memory_limit_KiB=4194304,command="PYTHONPATH=/tmp/regrip_stage2_fem OPENBLAS_NUM_THREADS=1 timeout 420s bash -c 'ulimit -v 4194304; exec python product_prototype/stage12_integrated/scripts/flexible_rail_distributed.py flexible_distributed2'",log=ref(out/'execution.log')),release_audit=a,known_analysis_children_running=0))
print(json.dumps(dict(verification='PASS',research=s['status'],failed_rows=2,release=a['status'])))
