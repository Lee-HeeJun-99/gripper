"""Independent actual-part connector identity audit; no solver imports."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');reports=[]
 for tag in sys.argv[2:]:
  src=ROOT/'validation/integrated'/tag;d=json.loads((src/'summary.json').read_text());g=json.loads((REPO/d['geometry']['path']).read_text());o=np.load(REPO/d['operators']['path']);labels=[p['label'] for p in g['patches']];bolts=[labels.index('bolt'+str(j)) for j in range(3)];spr=o['spring_mm_N'];actual=np.flatnonzero(spr).tolist();expected=14/(200000*np.pi*2.5**2)
  checks=dict(exactly3actual_bolt_labels=len(set(bolts))==3,connector_stiffness_attached_only_actual_bolts=set(actual)==set(bolts),actual_bolt_nominal_law=all(abs(spr[j]-expected)<1e-18 for j in bolts),canonical_bolts_last=bolts==list(range(len(labels)-3,len(labels))),reported_bolt_forces=all(np.max(abs(np.array(r['contact_forces_N'])[bolts]-r['bolt_tension_N']))<1e-12 for r in d['rows'] if 'contact_forces_N' in r))
  reports.append(dict(source=ref(src/'summary.json'),checks=checks,actual_bolt_variable_indices=bolts,spring_variable_indices=actual,variable_labels=labels))
 checks=dict(all_physical_connector_bindings=all(all(r['checks'].values()) for r in reports));dump(out/'summary.json',dict(status='ACTUAL_P1_PART_ID_CONNECTOR_BINDING_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_PART_ID_CONNECTOR_BINDING_FAIL',candidate=d['candidate'],verifier=ref(out/'verifier.py'),checks=checks,reports=reports,whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Checks exactpartID correspondence of conditional nominalshank law;does NOT qualify real core/flank/head/nut/preload/material or external fixture.','Force/work equilibrium audits alone cannot detect a physically misbound spring law.']))
 print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
