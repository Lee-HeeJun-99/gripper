"""Independent bounded-evidence availability/hash audit; NOT product release."""
import argparse,csv,hashlib,json,re,subprocess,shutil
from stage2_release_gate import validate,expected_baseline
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S1=ROOT.parent/'stage1_manufacturing'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
SELECTED=['models/geometry/revAA_extract2','validation/integrated/envelope1','validation/finger/endpoint1',
 'validation/finger/elastica1','validation/shaft/sections1','validation/convergence/torsion1',
 'validation/integrated/stroke1','validation/worst_case/dimension_corners1',
 'validation/integrated/torsion_dynamic1','validation/tendon/seated1',
 'hardware_test/inspection/fixture_geometry1','validation/coupling/alignment2',
 'validation/finger/clamp_load1','validation/finger/sliding_pet_correlated1',
 'validation/integrated/software_controls4','validation/finger/sliding_contact4',
 'validation/finger/contact_independent1']
def digests(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            if 'sha256' in k.lower() or k=='hashes':yield from hashes(v)
    # recurse only into explicitly named hash blocks, not numeric data
def hashes(obj):
    if isinstance(obj,str) and re.fullmatch('[0-9a-f]{64}',obj):yield obj
    elif isinstance(obj,dict):
        for v in obj.values():yield from hashes(v)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    files=[p for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    bom=S1/'bom/revAA_mbd1/STAGE1_BOM.csv';parts=list(csv.DictReader(bom.open()))
    files += [bom,S1/'cad/assembly/revAA_mbd1/ASSEMBLY.step',S1/'cad/exports/revAA_heel_relief2/summary.json']
    part_errors=[]
    for row in parts:
        path=S1/row['STEP'];files.append(path)
        if sha(path)!=row['STEP_SHA256']:part_errors.append(row['part_ID'])
    files.append(Path('/tmp/regrip_stage2_fem/libgmsh.so.4.15'))
    files.extend(Path('/tmp/regrip_stage2_fem/osqp').glob('ext_builtin*.so'))
    available={sha(p):str(p) for p in files if p.is_file()};checks=[]
    for rel in SELECTED:
        path=ROOT/rel/'summary.json';doc=json.loads(path.read_text())
        missing=sorted(set(digests(doc))-available.keys())
        checks.append(dict(evidence=rel,status=doc.get('status'),summary_SHA256=sha(path),missing_hashes=missing))
    gitdiff=subprocess.check_output(['git','diff','c0e5dfdc6fe3812b8bbd09ed3392e239a30aca2a','--name-only','--',str(S1)],text=True).strip()
    gate=json.loads((ROOT/'validation/integrated/release_audit2/summary.json').read_text())
    physical_counts={}
    for name,fields in [('TENSION_RECORDS.csv',['force_N','extension_m']),('ALIGNMENT_RECORDS.csv',['r0_m','r90_m','r180_m','r270_m'])]:
        rr=list(csv.DictReader((ROOT/'hardware_test/inspection'/name).open()))
        physical_counts[name]=sum(any(r.get(k) not in (None,'') for k in fields) for r in rr)
    physical_counts['Stage1_INSPECTION_RECORDS.csv']=sum(r['measured_mm']!='' for r in csv.DictReader((S1/'validation/revAA_first_article_template2/INSPECTION_RECORDS.csv').open()))
    historical_diff=subprocess.check_output(['git','diff','c0e5dfdc6fe3812b8bbd09ed3392e239a30aca2a','--name-only','--','product_prototype/results','product_prototype/sofa','product_prototype/cad','product_prototype/stage1_manufacturing'],text=True).strip()
    fresh=validate(json.loads((ROOT/'models/analytical/release_registry.json').read_text()),ROOT,expected_baseline())
    gate_matches=all(gate[k]==fresh[k] for k in ('status','analytical_pass','numerical_pass','errors'))
    result=dict(status='PASS' if not part_errors and len(parts)==304 and not gitdiff and not historical_diff and all(c['status']=='PASS' and not c['missing_hashes'] for c in checks) and gate_matches else 'FAIL',
        scope='SELECTED BOUNDED EVIDENCE INTEGRITY ONLY; NOT STAGE2 QUALIFICATION',checks=checks,
        Stage1_tracked_changes=gitdiff,part_hash_errors=part_errors,Stage1_part_count=len(parts),
        fail_closed_release_status=gate['status'],source_SHA256=sha(Path(__file__)),
        fresh_release_verdict_matches=gate_matches,
        historical_protected_paths_changed=historical_diff,
        physical_measurement_row_counts=physical_counts,all_physical_records_empty=all(v==0 for v in physical_counts.values()),
        command='python scripts/artifact_audit.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
