"""Installed dedup/source order and independent linear impulse at one actual step."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def frame(path,key,target):
 with path.open() as f:
  for r in csv.DictReader(f):
   t=float(r[key])
   if abs(t-target)<1e-12:yield r
   elif t>target+1e-12:break
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--time',type=float,required=True);p.add_argument('--vertex',type=int,default=360);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;surface=list(frame(src/'surface.csv','time_s',a.time-.0001));assert len(surface)==1;previous=np.fromstring(surface[0]['q'],sep=' ').reshape(-1,3)[a.vertex];groups={};responses={}
 for r in frame(src/'detector.csv','accepted_time_s',a.time):groups.setdefault((r['model0'],r['model1']),[]).append(r)
 for r in frame(src/'response_rows.csv','time_s',a.time):responses.setdefault((r['model0'],r['model1']),[]).append(r)
 records=[];witness=[];error=0.;counts_match=True;unmeasured=0;sumactual=np.zeros(6);summap=np.zeros(6)
 for pair,raw in groups.items():
  raw.sort(key=lambda r:int(r['pair_index']));kept=[];discard={}
  for r in raw:
   q=np.array([np.fromstring(r[f'detected_point{i}'],sep=' ') for i in (0,1)]);i=next((i for i,x in enumerate(kept) if float(np.sum((x[1]-q)**2))<float(np.float32(1e-8))),None)
   if i is None:kept.append((r,q))
   else:discard[int(r['pair_index'])]=int(kept[i][0]['pair_index'])
  owned=sorted(responses.get(pair,[]),key=lambda r:int(r['row_id']));equal=len(owned)==len(kept);counts_match &=equal;records.append(dict(models=pair,detector_count=len(raw),predicted_retained=len(kept),actual_rows=len(owned)))
  for r in raw:
   for side in (0,1):
    if pair[side]=='/wire/wireSurface/PointCollisionModel1' and np.linalg.norm(np.fromstring(r[f'detected_point{side}'],sep=' ')-previous)<=1e-12:
     pid=int(r['pair_index']);witness.append(dict(models=pair,pair_index=pid,detected_points=[r['detected_point0'],r['detected_point1']],retained=pid not in discard,discarded_for=discard.get(pid)))
  if not equal:continue
  for (_,q),r in zip(kept,owned):
   actual=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');summap+=actual;lam=float(r['lambda_Ns']);delta=q[1]-q[0];norm=np.linalg.norm(delta)
   if norm<=1e-15:
    unmeasured+=int(lam!=0);continue
   sign=-1 if pair[0].startswith('/wire/') else 1;expected=sign*delta/norm*lam;error=max(error,float(abs(expected-actual[:3]).max()));sumactual[:3]+=expected
 state=list(frame(src/'states.csv','time_s',a.time));assert len(state)==1;aggregate=np.fromstring(state[0]['object_impulse_Ns_Nms'],sep=' ');partition=float(abs(aggregate-summap).max());d=dict(status='PASS_SOURCE_ORDER_AND_LINEAR_IMPULSE_ONLY' if counts_match and unmeasured==0 and error<=1e-12 and partition<=1e-12 else 'FAIL_SOURCE_ORDER_OR_LINEAR_IMPULSE_REFERENCE',case=a.case,target_time_s=a.time,wire_vertex=a.vertex,pair_inventory=records,actual_previous_vertex_detector_witness=witness,all_pair_retained_row_counts_match=bool(counts_match),maximum_per_row_linear_impulse_error_Ns=error,actual_row_vs_aggregate_impulse_error_Ns_Nms=partition,unmeasured_nonzero_degenerate_normals=unmeasured,scope='Replay installed combinedpoint100umdedup perACTUALmodelpair/order. Independent normalizeddetectorseparation timeslambda vsNativewire Jtranspose translation. Not angularimpulse/energy/CCD/physicalcontact/graspPASS. Zero-friction1row/contact only. Alloriginalphysicalgeometry/features retained inpartition case.',source_sha256=sha(Path(__file__)),input_sha256={f:sha(src/f) for f in ('surface.csv','states.csv','detector.csv','response_rows.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='pair_inventory'},indent=2))
if __name__=='__main__':main()
