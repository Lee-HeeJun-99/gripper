"""Append-only publication and byte verification; no physical PASS synthesis."""
import argparse,hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=BASE/'reports'/a.name;out.mkdir(exist_ok=False)
 legacy=json.loads((ROOT/'reports/FILM_CONTACT_EVIDENCE_20261119_thickness_v15.json').read_text());fail=[];checked=0;excluded=[]
 for name,digest in legacy['files'].items():
  # Explicitly updated narrative entry points are not immutable experiment bytes.
  if name.startswith('reports/') and name.endswith('.md'):excluded.append(name);continue
  path=Path(name) if Path(name).is_absolute() else ROOT/name
  if not path.is_file() or sha(path)!=digest:fail.append(name)
  checked+=1
 result=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='product evidence;NOT grasp/numerical/material approval',legacy=dict(checked=checked,excluded_narrative=excluded,mismatches=fail,status='PASS' if not fail else 'FAIL'),cases={},files={})
 prior=json.loads((BASE/'reports/evidence_native_v1/manifest.json').read_text());old_fail=[];old_count=0
 for name,digest in prior['files'].items():
  immutable=name.startswith('product_prototype/results/') or any(name.startswith('product_prototype/'+x) for x in ('meshes/','drawings/','cad/build_')) or name.startswith('product_prototype/sofa/scenes/')
  if not immutable:continue
  path=ROOT/name;old_count+=1
  if not path.is_file() or sha(path)!=digest:old_fail.append(name)
 result['prior_product_immutable']=dict(checked=old_count,mismatches=old_fail,status='PASS' if not old_fail else 'FAIL',scope='Raw,old assets,private binary,scenes;live source/narrative intentionally mutable')
 newer=BASE/'reports/evidence_native_coupling_v2/manifest.json';new_fail=[];new_count=0
 if newer.exists():
  for name,digest in json.loads(newer.read_text())['files'].items():
   if not(name.startswith('product_prototype/results/') or name.startswith('product_prototype/reports/evidence_native_coupling_v2/') or any(name.startswith('product_prototype/'+x) for x in ('meshes/','drawings/','cad/build_','sofa/scenes/'))):continue
   new_count+=1;path=ROOT/name
   if not path.is_file() or sha(path)!=digest:new_fail.append(name)
 result['prior_coupling_immutable']=dict(checked=new_count,mismatches=new_fail,status='PASS' if not new_fail else 'FAIL')
 skin=BASE/'reports/evidence_native_skin_v3/manifest.json';skin_fail=[];skin_count=0
 if skin.exists():
  for name,digest in json.loads(skin.read_text())['files'].items():
   if not(name.startswith('product_prototype/results/') or name.startswith('product_prototype/reports/evidence_native_skin_v3/') or any(name.startswith('product_prototype/'+x) for x in ('meshes/','drawings/','cad/build_','sofa/scenes/'))):continue
   skin_count+=1;path=ROOT/name
   if not path.is_file() or sha(path)!=digest:skin_fail.append(name)
 result['prior_skin_immutable']=dict(checked=skin_count,mismatches=skin_fail,status='PASS' if not skin_fail else 'FAIL')
 response=BASE/'reports/evidence_native_response_v4/manifest.json';response_fail=[];response_count=0
 if response.exists():
  for name,digest in json.loads(response.read_text())['files'].items():
   if not(name.startswith('product_prototype/results/') or name.startswith('product_prototype/reports/evidence_native_response_v4/') or any(name.startswith('product_prototype/'+x) for x in ('meshes/','drawings/','cad/build_','sofa/scenes/'))):continue
   response_count+=1;path=ROOT/name
   if not path.is_file() or sha(path)!=digest:response_fail.append(name)
 result['prior_response_immutable']=dict(checked=response_count,mismatches=response_fail,status='PASS' if not response_fail else 'FAIL')
 for folder in sorted((BASE/'results').iterdir()):
  if not folder.is_dir():continue
  summary=folder/'summary.json'
  if summary.exists():
   shutil.copy2(summary,out/(folder.name+'.json'));m=json.loads(summary.read_text());result['cases'][folder.name]=dict(summary_sha256=sha(summary),status=m.get('status','ANALYSIS'),source_commit=m.get('source_commit'),binary_sha256=m.get('binary_sha256'))
  scene=folder/'scene.scn'
  if scene.exists():
   tree=ET.parse(scene);control=tree.find('./Node/NativeCableSequence');root=tree.getroot();effective=dict(source_scene_sha256=sha(scene),dt_s=float(root.get('dt')),solver=[x.tag for x in root if x.get('name')=='constraints'],control=dict(control.attrib) if control is not None else None,scope='append-only metadata correction;scene/log/command authoritative;old config retained')
   (out/(folder.name+'_effective_input.json')).write_text(json.dumps(effective,indent=2))
  # Hash Raw/log/config/source snapshots. Source copies include no runtime records.
  for f in folder.rglob('*'):
   if f.is_file():result['files'][str(f.relative_to(ROOT))]=sha(f)
 for folder in (BASE/'results').iterdir():
  if folder.is_dir() and any(folder.name.endswith(x) for x in ('_144','_145','_165','_255','299','305')):
   for f in folder.glob('*.png'):shutil.copy2(f,out/(folder.name+'_'+f.name))
 for f in (BASE/'cad').glob('build_*/libReGripProductSequence.so'):result['files'][str(f.relative_to(ROOT))]=sha(f)
 for top in ('config','cad','drawings','meshes','sofa'):
  for f in (BASE/top).rglob('*'):
   if f.is_file() and not any(x.startswith('build_') or x in ('__pycache__','records') for x in f.parts):result['files'][str(f.relative_to(ROOT))]=sha(f)
 for f in out.iterdir():
  if f.is_file():result['files'][str(f.relative_to(ROOT))]=sha(f)
 (out/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(output=str(out),legacy=result['legacy'],cases=len(result['cases']),files=len(result['files']))))
 if fail or old_fail or new_fail or skin_fail or response_fail:raise SystemExit('Prior immutable evidence mismatch;inspect,do not rewrite baseline')
if __name__=='__main__':main()
