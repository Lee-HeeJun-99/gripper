"""Exclusive integrity index for moving-owner research, never a physics Gate."""
import argparse,hashlib,json,subprocess
from curve_common import ROOT,sha,write_json

def main():
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--verify',action='store_true');a=p.parse_args()
 if not a.version.isalnum():raise ValueError('simple version')
 index=ROOT/'reports/vector_history'/('general_manifest_'+a.version+'.json')
 if a.verify:
  d=json.loads(index.read_text());errors=[]
  for n,h in d['files'].items():
   q=ROOT/n
   if not q.is_file()or sha(q)!=h:errors.append(n)
  for n,h in d['blobs'].items():
   if hashlib.sha256(subprocess.check_output(['git','show',d['commit']+':'+n],cwd=ROOT)).hexdigest()!=h:errors.append('blob:'+n)
  print(json.dumps(dict(status='FAIL'if errors else'PASS',artifacts=len(d['files']),errors=errors,scope='integrity only')))
  if errors:raise SystemExit(1)
  return
 if index.exists():raise ValueError('refuse overwritten index')
 prefixes=('vector_history_owner_','vector_history_moving_','vector_history_compare_','vector_history_material_rule_','vector_history_rule_geometry_','vector_history_frames_','vector_history_wrench_','vector_history_prescribed_','vector_history_capacity_','vector_history_temporal_yield_','vector_history_general_suite_')
 files={}
 for folder in (ROOT/'results').iterdir():
  if folder.is_dir()and folder.name.startswith(prefixes):
   for q in folder.rglob('*'):
    if q.is_file():files[str(q.relative_to(ROOT))]=sha(q)
 for folder in (ROOT/'build').glob('vector_history_owner_*'):
  for name in ('libReGripGeneralVectorContact.so','GeneralGenerated.inc','test_general_curved','test_general_history_owner','test_general_wrench'):
   q=folder/name
   if q.is_file():files[str(q.relative_to(ROOT))]=sha(q)
 commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 names=subprocess.check_output(['git','ls-files','models/general_vector_history','tests/test_general*','tools/curve_general*'],cwd=ROOT,text=True).splitlines()
 blobs={n:hashlib.sha256(subprocess.check_output(['git','show',commit+':'+n],cwd=ROOT)).hexdigest()for n in names}
 write_json(index,dict(commit=commit,files=files,blobs=blobs,scope='immutable moving-history cohort integrity only;FAILs retained;not gripper qualification'))
 print(json.dumps(dict(index=str(index),artifacts=len(files))))
if __name__=='__main__':main()
