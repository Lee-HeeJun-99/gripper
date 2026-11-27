"""Independent saved collision witnesses: reverse boolean and volume subtraction."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,cut,volume
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/stage1/batch6_idler_after_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 source=ROOT/'validation/stage1/batch6_idler_after1/summary.json';d=json.loads(source.read_text());ip=REPO/d['inputs']['path'];assert sha(ip)==d['inputs']['SHA256'];inp=json.loads(ip.read_text())
 for r in [inp['candidate'],inp['producer'],*inp['parts'].values(),*inp['dependencies']]:assert sha(REPO/r['path'])==r['SHA256']
 dump(out/'inputs.json',dict(source=ref(source),source_inputs=ref(ip),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],volume_relative_limit=1e-6,volume_absolute_limit_mm3=1e-8))
 cache={};witnesses=[]
 def part(n):
  if n not in cache:cache[n]=read(REPO/inp['parts'][n]['path'])
  return cache[n]
 # One largest witness per sector and entry height; every rejected row needs a physical witness.
 for row in d['rows']:
  if not row['hits']:continue
  h=max(row['hits'],key=lambda h:h['common_mm3']);a=translate(part(h['moving']),0,0,row['dz_mm']);b=part(h['fixed'])
  assert not (ROOT/'runtime/STOP').exists()
  v=common(b,a);loss=volume(a)-volume(cut(a,b));tol=max(1e-8,1e-6*h['common_mm3'])
  ok=BRepCheck_Analyzer(a).IsValid() and BRepCheck_Analyzer(b).IsValid() and v>1e-8 and abs(v-h['common_mm3'])<tol and abs(loss-v)<tol
  witnesses.append(dict(sector=row['sector'],dz_mm=row['dz_mm'],moving=h['moving'],fixed=h['fixed'],reported_mm3=h['common_mm3'],reversed_common_mm3=v,subtracted_volume_mm3=loss,passed=ok))
 counts=[len(g) for g in inp['groups'].values()];partition=[n for g in inp['groups'].values() for n in g]+inp['deferred']+inp['initial_fixed']
 checks=dict(input_hashes=True,partition_exact=len(partition)==len(set(partition))==254 and set(partition)==set(inp['parts']),six_groups_partition=len(counts)==6 and len(set(counts[:3]))==1 and len(set(counts[3:]))==1,all_rejected_rows_witnessed=len(witnesses)==d['collision_rows'],nonempty_actual_collision=bool(witnesses),independent_booleans=all(w['passed'] for w in witnesses),unchanged_final_nominal=bool(d['nominal_samples_clear']))
 dump(out/'summary.json',dict(status='REJECTION_WITNESSES_VERIFIED' if all(checks.values()) else 'VERIFICATION_FAIL',source=ref(source),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),checks=checks,witnesses=witnesses,whole_system_release=False,scope='Every rejected row independently reimported with reversed boolean common and volume subtraction; not independent exhaustive collision-free proof or continuous path certification.'))
 print(json.dumps(dict(checks=checks,witnesses=len(witnesses))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
