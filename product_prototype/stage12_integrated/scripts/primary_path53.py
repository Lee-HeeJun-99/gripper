"""Nine finite same-product pin/guide/payload assembly path states.
No threaded Boolean sequences and no imposed receiver fixation in statics.
"""
import json,sys,shutil,time,os
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_takeup53e import XY,C,rot
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds,overlap
from validate_nutseat46c import rotate
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
out=ROOT/'validation/integrated/primaryP1_path53';out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_takeup53e/summary.json';st=json.loads(sp.read_text());cp=REPO/st['candidate']['path'];cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/r['path']) for n,r in cad['part_references'].items()};q=np.array(st['coordinates']);rows=[];states=[];payload=[n for n in parts if not n.startswith('BENCH_') and n!='EXTERNAL_BENCH_PLATE'];static=['BENCH_SUPPORT','EXTERNAL_BENCH_PLATE']
def query(label,a,b,s,distance=False):
 assert not(ROOT/'runtime/STOP').exists();t=time.monotonic()
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(dict(state='START',fraction=s,label=label,operation='nonthread_actualassembly_intersection'+('_distance' if distance else '')))+'\n');f.flush();os.fsync(f.fileno())
 v=common(a,b);dist=None
 if distance:
  d=BRepExtrema_DistShapeShape(a,b);d.Perform();assert d.IsDone();dist=d.Value()
 r=dict(state='COMPLETE',fraction=s,label=label,intersection_mm3=v,distance_mm=dist,elapsed_s=time.monotonic()-t);rows.append(r)
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(r)+'\n');f.flush();os.fsync(f.fileno())
 return r
for fraction in np.linspace(0,1,9):
 s=float(fraction);p=q*s;t=p[2];j=p[4:].reshape(4,7);rc=(XY-C)@rot(t).T+C+p[:2];keys=XY+j[:,4:6];rail=translate(rotate(parts['BENCH_ANCHOR_RAIL'],*C,t),*p[:2],p[3]);pr=[query('receiver_support',rail,parts['BENCH_SUPPORT'],s)];pinposes=[]
 for i in range(4):
  centre=(rc[i]+keys[i])/2;a=(t+j[i,6])/2;pin=translate(rotate(parts[f'BENCH_MOUNT_SPLIT_PIN_{i}'],*XY[i],a),*(centre-XY[i]),p[3]);key=translate(rotate(parts[f'BENCH_MOUNT_SOCKET_KEY_{i}'],*XY[i],j[i,6]),*j[i,4:6],p[3]);pinposes.append(dict(index=i,centre_xy_mm=centre.tolist(),yaw_rad=float(a),z_increment_mm=float(p[3])))
  pr.append(query(f'pin{i}_key',pin,key,s,True));pr.append(query(f'pin{i}_receiver',pin,rail,s,True))
 # Carry installed upstream payload rigidly for ASSEMBLY clearance only. NOT a physical tie/FE BC.
 count=0
 for n in payload:
  shape=translate(rotate(parts[n],*C,t),*p[:2],p[3]);b=bounds(shape)
  for m in static:
   if overlap(b,bounds(parts[m])):pr.append(query('payload_'+n+'__'+m,shape,parts[m],s));count+=1
 states.append(dict(fraction=s,opening_mm=float(p[3]),receiver_yaw_rad=float(t),pinposes=pinposes,payload_static_queries=count,maximum_common_mm3=max(abs(r['intersection_mm3']) for r in pr)));print(json.dumps(states[-1]),flush=True)
checks=dict(all128CADidentity=True,nine_finite_states=len(states)==9,pins_guides_payload_nonthread_clear=all(abs(r['intersection_mm3'])<1e-8 for r in rows),pin_minimum_gap_positive=min(r['distance_mm'] for r in rows if r['distance_mm'] is not None)>1e-7)
dump(out/'summary.json',dict(status='ACTUAL_P1_NINE_FINITE_PIN_GUIDE_PAYLOAD_ASSEMBLY_STATES_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_FINITE_PIN_GUIDE_PAYLOAD_ASSEMBLY_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),pose_source=ref(sp),journal=ref(out/'journal.jsonl'),checks=checks,states=states,queries=len(rows),payload_parts=len(payload),pin_pair_queries=72,minimum_pin_gap_mm=min(r['distance_mm'] for r in rows if r['distance_mm'] is not None),maximum_intersection_mm3=max(abs(r['intersection_mm3']) for r in rows),maximum_query_seconds=max(r['elapsed_s'] for r in rows),whole_system_release=False,newly_qualified_system_gate_ids=[],accepted_physical_product_equilibria=0,limitations=['Ninefiniteposesonly,NOTcontinuous128partCCD oractualquasistatictakeup/physicalloadpath PASS','Rigidbodypayloadfollowingreceiverisassemblyplacementonly,NOT hiddenmechanicaltie orFEfixation','Actual threadedbolt/nut/seat pairs deliberatelyexcluded fromwholeBRepBooleanpath;freshtrimmedlocalboundaryqueriesrecordedseparately','Pin/forming/source minima/elasticpressures/capacity/100goperatingfield/host/mesh/time/globalenergy/all22 remainunqualified']));raise SystemExit(0 if all(checks.values()) else 2)
