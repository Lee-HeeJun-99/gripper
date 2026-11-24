"""New append-only integrity index for explicit COMPLETED experiment directories."""
import argparse,hashlib,json,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();assert Path(a.tag).name==a.tag;out=BASE/'results'/a.tag;assert not out.exists();records=[]
 for name in a.cases:
  assert Path(name).name==name;folder=BASE/'results'/name;assert (folder/'summary.json').is_file(),'Only completed cases;never hash changing NativeRaw'
  for f in sorted(folder.rglob('*')):
   assert not f.is_symlink()
   if f.is_file():records.append(dict(path=str(f.relative_to(BASE.parent)),bytes=f.stat().st_size,sha256=digest(f),git_excluded_raw=f.name in ('detector.csv','layer_pairs.csv') or f.stat().st_size>=100_000_000))
 sdk=Path('/home/ubuntu/SOFA/v26.06.00');references=[sdk/'lib/libSofa.Component.Collision.Response.Contact.so',sdk/'plugins/BeamAdapter/lib/libBeamAdapter.so.1.0',sdk/'include/Sofa.Component.Collision.Response.Contact/sofa/component/collision/response/contact/BaseUnilateralContactResponse.inl',sdk/'plugins/BeamAdapter/include/BeamAdapter/component/mapping/AdaptiveBeamMapping.inl',BASE/'cad/build_contact_gap1211/libReGripContactGapProbe.so'];d=dict(status='PASS_COMPLETED_ARTIFACT_HASH_INDEX_ONLY',source_commit_before_manifest_save=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),cases=a.cases,files=len(records),git_excluded_raw_files=sum(r['git_excluded_raw'] for r in records),records=records,installed_reference_sha256={str(f):digest(f) for f in references},source_sha256=digest(Path(__file__)),scope='Newintegrityindexonly;alloriginalRaw/SDK/previousmanifest unchanged. ExcludedRawstaysatlocaloriginalpath;thisindex isNOT anexternal backup or physicalPASS. NoNative/verificationresult regeneration. Completedfilesread-only.');out.mkdir();(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('records','installed_reference_sha256','cases')},indent=2))
if __name__=='__main__':main()
