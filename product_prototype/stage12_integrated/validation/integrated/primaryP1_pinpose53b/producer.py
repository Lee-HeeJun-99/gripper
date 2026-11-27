"""Actual P1 pins/keys at newly derived guide/bore finitepose;no thread Boolean."""
import json,sys,shutil,os,time
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from validate_nutseat46c import rotate
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
out=ROOT/'validation/integrated/primaryP1_pinpose53b';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_takeup53e/summary.json';state=json.loads(sp.read_text());cad=json.loads((REPO/state['candidate']['path']).read_text());parts={};rows=[]
for i in range(4):
 for n in [f'BENCH_MOUNT_SOCKET_KEY_{i}',f'BENCH_MOUNT_SPLIT_PIN_{i}','BENCH_ANCHOR_RAIL']:
  if n in parts:continue
  r=cad['part_references'][n];assert sha(REPO/r['path'])==r['SHA256'];p=state['poses'][n];parts[n]=translate(rotate(read(REPO/r['path']),*p['rotation_about_mm'][:2],p['yaw_rad']),*p['translation_after_rotation_mm'])
 for b in [f'BENCH_MOUNT_SOCKET_KEY_{i}','BENCH_ANCHOR_RAIL']:
  assert not(ROOT/'runtime/STOP').exists();a=f'BENCH_MOUNT_SPLIT_PIN_{i}';t=time.monotonic()
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',a=a,b=b))+'\n');f.flush();os.fsync(f.fileno())
  v=common(parts[a],parts[b]);d=BRepExtrema_DistShapeShape(parts[a],parts[b]);d.Perform();r=dict(state='COMPLETE',a=a,b=b,intersection_mm3=v,distance_mm=d.Value(),elapsed_s=time.monotonic()-t);rows.append(r)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
good=all(abs(r['intersection_mm3'])<1e-8 for r in rows);dump(out/'summary.json',dict(status='ACTUAL_P1_FINITE_PIN_POSE_LOCAL_CLEAR_NOT_RELEASE' if good else 'ACTUAL_P1_FINITE_PIN_POSE_INTERFERENCE_FAIL',candidate=state['candidate'],pose_source=ref(sp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),pairs=rows,whole_system_release=False,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0));print(json.dumps(rows),flush=True);raise SystemExit(0 if good else 2)
