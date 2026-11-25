"""Manifest local failed/intermediate CAD without discarding large originals."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'validation/revJ_trials';out.mkdir(exist_ok=False)
 stages={'revJ_mount':'FAIL disconnected nipple cap islands','revJ_backer':'FAIL33 bulk intersections','revJ_clearance':'FAIL6 screw/plate intersections','revJ_pipe':'FAIL cap/front STL topology','revJ_precision':'FAIL precision-only did not fix real zero-wall tangencies','revJ_edgewall':'FAIL front countersink tangent to plate bottom','revJ_margin':'MESH PASS283, sampled60deg fork collision FAIL','revJ_forkclear':'See independent motion/wire evidence; release not implied'}
 for tag,status in stages.items():
  src=ROOT/'cad/exports'/tag;d=out/tag;d.mkdir()
  manifest={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(src.iterdir()) if p.is_file()}
  for name in ('producer.py','mechanisms_producer.py','summary.json','dependencies_sha256.json'):
   if (src/name).exists():shutil.copyfile(src/name,d/name)
  (d/'local_originals_manifest.json').write_text(json.dumps(dict(status=status,local_originals_preserved=True,files=manifest),indent=2))
 # Earliest failure occurred before producer freezing; do not invent its SHA.
 (out/'earliest_failure.json').write_text(json.dumps(dict(case='revJ_mechanisms',status='FAIL float passed to pitch_at: imported numeric common instead of CAD Common',source_snapshot_available=False),indent=2))
 for p in Path('/tmp').glob('regrip_stage1_*.log'):
  if p.stat().st_size<5_000_000:shutil.copyfile(p,out/p.name)
 print('Preserved actual original files in place; indexed',len(stages),'trials')
if __name__=='__main__':main()
