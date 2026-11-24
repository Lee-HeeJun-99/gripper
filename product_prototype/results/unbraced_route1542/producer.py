"""Minimal sector clearance from ACTUAL saved guide poses,not new dynamics.
Find ONE geometry root for1mm saved guide gap;not random offset/grasp tuning.
"""
import argparse,copy,csv,json,itertools,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from mechanism_candidates import world,width,guide_outboard,guide_normal
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/paired_mesh_hold1001534';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());obj=read(src/'object.csv');times=[float(r['time_s']) for r in obj];centre=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in obj]);R=float(root.find("Node[@name='object']/Node/SphereCollisionModel").get('radius'));groups=[]
 for i,angle in enumerate((0,120,240)):
  film=read(src/f'finger{i}.csv');frames=read(src/f'guide_frames{i}.csv');assert [float(r['time_s']) for r in film]==times==[float(r['time_s']) for r in frames];rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);initial=np.fromstring(root.find(f"Node[@name='guides{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  for j,side in enumerate((-1,1)):
   node=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owners=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);q=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in film]);assert len(owners)==len(c['tendon']['guide_stations']);groups.append(dict(finger=i,cable=j,side=side,angle=angle,rest=rest,owners=owners,initial=initial,rigid=rigid,q=q,radius=float(node.find('SphereCollisionModel').get('radius'))))
 def evaluate(margin,check_wire=False):
  cfg=copy.deepcopy(c);cfg['tendon']['sector_margin_mm']=margin;points=[];wire=1e9;objectgap=1e9
  for g in groups:
   path=np.array([world(cfg,[x,g['side']*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)],g['angle']) for x in [0]+cfg['tendon']['guide_stations']])*.001;path[:,2]+=cfg['research_root_translation_z_mm']*.001;actual=g['q'].copy()
   for k,owner in enumerate(g['owners']):
    delta=Rotation.from_quat(g['initial'][owner,3:]).inv().apply(path[k+1]-g['rest'][k]);actual[:,k]+=Rotation.from_quat(g['rigid'][:,owner,3:]).apply(np.repeat(delta[None],len(times),axis=0))
   points.append(actual);objectgap=min(objectgap,float((np.linalg.norm(actual-centre[:,None],axis=2)-R-g['radius']).min()))
   if check_wire:
    full=np.concatenate([np.repeat(path[:1][None],len(times),axis=0),actual],axis=1);edge=np.diff(full,axis=1);a=full[:,:-1];u=np.clip(np.sum((centre[:,None]-a)*edge,axis=2)/np.sum(edge*edge,axis=2),0,1);wire=min(wire,float((np.linalg.norm(a+u[:,:,None]*edge-centre[:,None],axis=2)-R-.00025).min()))
  gap=1e9
  for i,j in itertools.combinations(range(6),2):
   if groups[i]['finger']==groups[j]['finger']:continue
   gap=min(gap,float((np.linalg.norm(points[i][:,:,None]-points[j][:,None,:],axis=3)-groups[i]['radius']-groups[j]['radius']).min()))
  return dict(minimum_replayed_interfinger_guide_gap_mm=gap*1000,minimum_replayed_guide_object_gap_mm=objectgap*1000,minimum_replayed_finite_wire_object_gap_mm=wire*1000 if check_wire else None)
 initial=float(c['tendon']['sector_margin_mm']);old=evaluate(initial,True);lo=initial;hi=initial+1.;assert evaluate(hi)['minimum_replayed_interfinger_guide_gap_mm']>=1.,'No safe geometric root in declaredbracket'
 for _ in range(40):
  mid=(lo+hi)/2
  if evaluate(mid)['minimum_replayed_interfinger_guide_gap_mm']>=1.:hi=mid
  else:lo=mid
 new=evaluate(hi,True);c['tendon']['sector_margin_mm']=hi;ok=new['minimum_replayed_interfinger_guide_gap_mm']>=1 and new['minimum_replayed_guide_object_gap_mm']>=.2 and new['minimum_replayed_finite_wire_object_gap_mm']>=.25;d=dict(status='READY_STATIC_ROUTE_INTERVENTION_ONLY' if ok else 'REJECT_REPLAY_ROUTE',source_case=src.name,old_sector_margin_mm=initial,candidate_sector_margin_mm=hi,target_saved_guide_gap_mm=1.,declared_bracket_mm=[initial,initial+1],bisection_iterations=40,old_replay=old,candidate_replay=new,scope='Actual savedRigidposes with only newchildGuideoffsets;NOT newNativeequilibrium/holding or sweptCCD. NoGuidecollision/radiusdisabled. ONEgeometricroot restoresoriginal1mmdesignclearance throughsavedmotion,not force/dt/randomrouteperformance scan. RealhardwareCOM/inertia/supportshape unqualified. FreshNative trial must showzerohardwarebracing andoriginal100ggoal.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','config.json','object.csv','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv')});(out/'config.json').write_text(json.dumps(c,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
