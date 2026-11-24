"""Bounded immutable-evidence and SDK audit;not physics certification."""
import argparse,json,subprocess,sys,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(BASE/'sofa'))
from native_bending_coupon import guarded
ROOT=BASE.parent
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
 prior=BASE/'reports/evidence_product_layer_bending_v78/manifest.json';m=json.loads(prior.read_text());roots=('product_prototype/results/','product_prototype/reports/evidence_','product_prototype/meshes/','product_prototype/drawings/');checked=0;bad=[]
 for rel,expected in m['files'].items():
  if not rel.startswith(roots):continue
  checked+=1;f=ROOT/rel
  if not f.is_file() or digest(f)!=expected:bad.append(rel)
 sdk_before=json.loads((BASE/'results/modal_layer_validation1284/summary.json').read_text())['SDK_identity'];sdk_now={f:digest(Path(f)) for f in sdk_before};sdk_same=sdk_now==sdk_before;raw=BASE/'results/layer_mesh_native1260/layer_pairs.csv';raw_ok=digest(raw)=='ad90ceea5e3856329c6efbbb8ebe6baa3c02155cc73af99d74034ca168782539';d=dict(status='PASS_SCOPED_IMMUTABLE_AND_SDK_AUDIT' if checked and not bad and sdk_same and raw_ok else 'FAIL_PRESERVATION',prior_manifest_sha256=digest(prior),immutable_files_checked=checked,mismatches=bad,SDK_hashes_unchanged=sdk_same,SDK_files=len(sdk_now),original_untracked_oversized_Raw_preserved=raw_ok,scope='Only original manifest Raw/evidence/mesh/drawing roots audited. Mutable active source/config/reports intentionally excluded,not claimed immutable. No newphysical qualification. No deletion/rewrite/push.',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
