"""Actual full128part finite offaxis endpoint assembly;exclude threaded BRep pairs.
Same rigid payload placement for assembly ONLY,not mechanical ties or FE BCs.
"""
import json,sys,shutil,os,time,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,overlap,common
from validate_nutseat46c import rotate
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
out=ROOT/'validation/integrated/primaryP1_assembly54';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_independent54d/summary.json';st=json.loads(sp.read_text());assert all(st['checks'].values());cp=REPO/st['candidate']['path'];assert sha(cp)==st['candidate']['SHA256'];cad=json.loads(cp.read_text());parts={};bb={};groups={};rows=[];excluded=[]
for n,r in cad['part_references'].items():
 assert sha(REPO/r['path'])==r['SHA256'];s=read(REPO/r['path'])
 if n in st['poses']:pose=st['poses'][n]
 elif n=='EXTERNAL_BENCH_PLATE':pose=st['poses']['BENCH_SUPPORT']
 else:pose=st['poses']['BENCH_ANCHOR_RAIL']
 s=translate(rotate(s,*pose['rotation_about_mm'][:2],pose['yaw_rad']),*pose['translation_after_rotation_mm']);parts[n]=s;bb[n]=bounds(s);groups[n]=json.dumps(pose,sort_keys=True)
for a,b in itertools.combinations(parts,2):
 if groups[a]==groups[b] or not overlap(bb[a],bb[b]):continue
 if any({a,b}=={f'BENCH_MOUNT_BOLT_{i}',f'BENCH_MOUNT_NUT_{i}'} for i in range(4)):
  excluded.append([a,b]);continue
 assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',pair=[a,b],operation='actual_finite_nonthread_BRep_intersection'))+'\n');f.flush();os.fsync(f.fileno())
 volume=common(parts[a],parts[b]);gap=None
 if ('SPLIT_PIN' in a or 'SPLIT_PIN' in b):
  d=BRepExtrema_DistShapeShape(parts[a],parts[b]);d.Perform();assert d.IsDone();gap=d.Value()
 row=dict(state='COMPLETE',pair=[a,b],intersection_mm3=volume,distance_mm=gap,elapsed_s=time.monotonic()-t);rows.append(row)
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
hits=[r for r in rows if abs(r['intersection_mm3'])>1e-8];checks=dict(all128partidentity=len(parts)==128,finite_nonthread_endpoint_clear=not hits)
dump(out/'summary.json',dict(status='ACTUAL_P1_OFFAXIS_128PART_FINITE_ASSEMBLY_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_OFFAXIS_128PART_FINITE_ASSEMBLY_FAIL',candidate=ref(cp),pose_source=ref(sp),producer=ref(out/'producer.py'),journal=ref(out/'journal.jsonl'),checks=checks,actual_parts=len(parts),queries=len(rows),excluded_thread_pairs=excluded,rows=rows,interferences=hits,maximum_intersection_mm3=max(abs(r['intersection_mm3']) for r in rows),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Onefiniteendpoint,not continuousinsertion/toolpath orcontact dynamics','Samepayload groupinternalsunchanged;groupmotion isassemblyplacement only,NOT a mechanicaltie/FEBC','Threadedpairs excludedfromglobalBoolean;partialflank/crestlocalbindings recordedseparately;remainingthreadfeaturesnotfullycertified','All22gatesremainunqualified;nooperating/strength/energy/host/hardwarePASS']))
print(json.dumps(dict(checks=checks,queries=len(rows),hits=hits)));raise SystemExit(0 if all(checks.values()) else 2)
