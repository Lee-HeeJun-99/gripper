"""Reuse immutable B3 Detector/Response journals;no new grasp or contact area."""
import argparse,csv,json,collections
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def kind(a,b):
 for p in (a,b):
  if 'skinCollision' in p:return p.rsplit('/',1)[-1]
 return None
def assess(case,lo=1.6,hi=2.):
 src=BASE/'results'/case;dt=.0025;frames={}
 with (src/'object.csv').open() as f:
  for r in csv.DictReader(f):
   t=float(r['time_s'])
   if lo<=t<=hi:frames[t]={}
 detect=collections.Counter();response=collections.Counter();forces={};normals={};claimed=set();duplicate=0
 with (src/'detection_pairs.csv').open() as f:
  for r in csv.DictReader(f):
   t=float(r['accepted_time_s'])
   if t>hi:break
   k=kind(r['model0'],r['model1'])
   if t in frames and k and '/object/' in r['model0']+r['model1']:detect[k]+=1
 with (src/'response_rows.csv').open() as f:
  for r in csv.DictReader(f):
   t=float(r['time_s'])
   if t>hi:break
   k=kind(r['model0'],r['model1'])
   if t not in frames or not k or '/object/' not in r['model0']+r['model1']:continue
   key=(t,int(r['row_id']));duplicate+=key in claimed;claimed.add(key);response[k]+=1;I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');forces.setdefault(k,np.zeros(3));forces[k]+=I[:3]/dt
   if (int(r['row_id'])-int(r['first_row']))%3==0:normals.setdefault(k,np.zeros(3));normals[k]+=I[:3]/dt
 n=len(frames);return dict(case=case,accepted_window_s=[lo,hi],window_membership='strict recorded accumulated time,no rounding/interpolation',accepted_frames=n,detector_feature_outputs=dict(detect),response_rows=dict(response),mean_skin_force_by_feature_N={k:(v/n).tolist() for k,v in forces.items()},mean_skin_normal_force_by_feature_N={k:(v/n).tolist() for k,v in normals.items()},duplicate_skin_response_row_ids=duplicate,contact_area=None,detector_normals=None,new_holding_verdict=None,scope='Historical actual model-pair/response-force partition ONLY. Original response observer metadata side effects and time/mesh failures unchanged. Detector counts are NOT area,distinct material points or one-to-one response coverage.',input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','object.csv','detection_pairs.csv','response_rows.csv','summary.json')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--early-phases',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);windows=[(1.,1.2),(1.2,1.5),(1.6,2.)] if a.early_phases else [(1.6,2.)];d=dict(status='HISTORICAL_B3_FEATURE_FORCE_PARTITION_ONLY',records=[assess(c,*window) for c in ('b3_alarm_window485','b3_mass100_explore1059') for window in windows],physical_validation='NOT QUALIFIED',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))
if __name__=='__main__':main()
