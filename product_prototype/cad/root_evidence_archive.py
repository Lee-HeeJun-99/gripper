"""Append-only root/compact CAD evidence chain;not physics qualification."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from manufacturing_assembly import BASE,sha
sys.path.insert(0,str(BASE/'sofa'))
from product_candidate_evidence import immutable

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--prior',required=True);p.add_argument('--cases',nargs='+',required=True);p.add_argument('--cad',nargs='+',required=True);a=p.parse_args();prior=BASE/'reports'/a.prior/'manifest.json';old=json.loads(prior.read_text());root=BASE.parent;files={name:digest for name,digest in old['files'].items() if immutable(name)};bad=[name for name,digest in files.items() if not(root/name).is_file() or sha(root/name)!=digest]
 if bad:raise ValueError('prior immutable hashes changed:'+repr(bad))
 out=BASE/'reports'/a.name;out.mkdir(exist_ok=False);cases={}
 for case in a.cases:
  if Path(case).name!=case:raise ValueError('local case name required')
  folder=BASE/'results'/case;summary=folder/'summary.json';detail=json.loads(summary.read_text());shutil.copy2(summary,out/(case+'.json'));record=dict(summary_sha256=sha(summary),status=detail['status'],annotations={})
  for f in folder.rglob('*'):
   if f.is_file():
    files[str(f.relative_to(root))]=sha(f)
    if f.name.endswith('CORRECTION.json') or f.name.endswith('REJECTION.json'):record['annotations'][f.name]=json.loads(f.read_text())
  cases[case]=record
 for name in a.cad:
  if Path(name).name!=name:raise ValueError('local CAD name required')
  folder=BASE/'meshes'/name
  if not folder.is_dir():raise ValueError('missing actual CAD folder')
  for f in folder.rglob('*'):
   if f.is_file():files[str(f.relative_to(root))]=sha(f)
  draw=BASE/'drawings'/name
  if draw.is_dir():
   for f in draw.rglob('*'):
    if f.is_file():files[str(f.relative_to(root))]=sha(f)
 for f in (BASE/'cad').glob('*.py'):shutil.copy2(f,out/('cad_'+f.name))
 for f in out.iterdir():
  if f.is_file():files[str(f.relative_to(root))]=sha(f)
 d=dict(scope='Append-onlyCAD/reference evidence including partialfailures/corrections;NOT product/physics/STEP qualification. NewCAD directories hashed as produced,including failedpartialSTLs;directory presence isNOT completion.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),prior_manifest_sha256=sha(prior),prior_immutable_audit=dict(checked=len([k for k in old['files'] if immutable(k)]),mismatches=bad),cases=cases,files=files)
 (out/'manifest.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(files=len(files),cases=len(cases),prior_checked=d['prior_immutable_audit']['checked'],mismatches=bad)))
if __name__=='__main__':main()
