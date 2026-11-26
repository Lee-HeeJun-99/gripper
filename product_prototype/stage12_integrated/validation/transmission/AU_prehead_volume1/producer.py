"""Actual STEP material-volume feasibility: access clearance cannot create missing rivet stock."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AU_prehead_volume1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'validation/transmission/AU_prehead_access1/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text());rows=[]
refs=[ref(src),d['inputs'],ref(out/'producer.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]
for r in d['rows']:
 if r['phase']!='preform_seated':continue
 final=inp['parts'][f"F{r['sector']}_IDLER_CROSSPIN"];refs.extend([r['shape'],final]);assert sha(REPO/final['path'])==final['SHA256'] and sha(REPO/r['shape']['path'])==r['shape']['SHA256']
 a=volume(read(REPO/r['shape']['path']));b=volume(read(REPO/final['path']));rows.append(dict(sector=r['sector'],preform_mm3=a,target_final_mm3=b,missing_mm3=b-a,missing_fraction=(b-a)/b,volume_feasible_without_added_stock=a>=b-1e-8))
dump(out/'inputs.json',dict(references=refs));ok=all(r['volume_feasible_without_added_stock'] for r in rows)
dump(out/'summary.json',dict(status='VOLUME_FEASIBILITY_PASS_ONLY' if ok else 'PREFORM_STOCK_DEFICIT_REJECTED',inputs=ref(out/'inputs.json'),rows=rows,scope='Necessary material volume condition for no-added-stock forming using actual reimported STEP volumes; no density or strength assumed',whole_system_release=False,next='Design sufficient protruding stock and re-evaluate actual insertion/tool/process envelope before forming qualification. Current access-clear preform cannot form AS target without added stock.'));print(json.dumps(rows));raise SystemExit(0 if ok else 2)
