"""Exercise unchanged Stage2 authority on actual AY identities; no adoption."""
import json,importlib.util,shutil
from pathlib import Path
from baseline_registry import ROOT,REPO,S2,sha,ref,dump
from integrated_release_gate import FROZEN_CRITERIA
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/integrated/AY_plate_readiness1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAY_plate_root1/summary.json';d=json.loads(src.read_text());bom=REPO/d['BOM']['path'];b=json.loads(bom.read_text());criteria=S2/'models/analytical/criteria.json';registry=S2/'models/analytical/release_registry.json';gate=S2/'scripts/stage2_release_gate.py'
assert sha(criteria)==FROZEN_CRITERIA
assert sha(bom)==d['BOM']['SHA256'] and sha(REPO/d['assembly']['path'])==d['assembly']['SHA256']
assert {r['part_ID']:r['STEP'] for r in b['parts']}==d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
spec=importlib.util.spec_from_file_location('existing_stage2',gate);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
verdict=mod.validate(json.loads(registry.read_text()),S2,dict(case=d['revision'],assembly_SHA256=d['assembly']['SHA256'],BOM_SHA256=sha(bom),criteria_SHA256=sha(criteria)))
errors=['No complete same-revision Stage1 release for AY','No AY SYSTEM_LOAD_TRANSFER evidence']+['stage2: '+e for e in verdict['errors']]
r=dict(status='INTEGRATED_NOT_QUALIFIED',revision=d['revision'],candidate=ref(src),BOM=ref(bom),existing_stage2_gate=ref(gate),criteria=ref(criteria),registry=ref(registry),producer=ref(out/'producer.py'),stage2=verdict,errors=errors,required_gate_ids=sorted(mod.REQUIRED),whole_system_release=False,adopted=False,hardware_status='HARDWARE_NOT_MEASURED',scope='Actual AY geometry/BOM identity exercised against unchanged existing release registry; bounded geometry is not same-revision system evidence')
assert verdict['status']!='STAGE2_LOAD_TRANSFER_DIGITAL_RELEASE_PASS' and verdict['errors']
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],revision=d['revision'],unqualified_stage2=len(verdict['errors']))));raise SystemExit(2)
