"""Actual material-feature identity and same-state multiplier observations.
No row-angle/contact-count to area/holding conversion;no force correction.
"""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();sources={};groups={};records=[];normError=moment=angular=0.;minimumForce=float('inf');topology=None
 for name in a.cases:
  src=ROOT/'results'/('autonomous_film_'+name);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS' or m['process']['exit_code'] or m['sofa_errors']:raise ValueError('completed qualified actual case required')
  for f,d in m['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('actual evidence changed')
  triangles=np.fromstring(ET.parse(src/'scene.scn').find('.//TriangleSetTopologyContainer').get('triangles'),sep=' ',dtype=int).reshape(-1,3)
  if topology is None:topology=triangles
  elif not np.array_equal(topology,triangles):raise ValueError('material mesh changed')
  sources[name]=dict(summary_sha256=sha(src/'summary.json'),binary_sha256=m['binary_sha256'])
  for row in csv.DictReader((src/'three.rows.csv').open()):
   f=int(row['owner_finger']);feature=int(row['feature']);triangle=int(row['triangle']);ids=triangles[triangle];support=sorted(int(ids[i]) for i in ({0:(0,),1:(1,),2:(2,),3:(0,1),4:(0,2),5:(1,2),6:(0,1,2)}[feature]));kind='face' if feature==6 else 'edge' if feature>=3 else 'vertex';key=(row['time'],f);groups.setdefault(key,[]).append(row)
   q=np.fromstring(row['stage_q'],sep=' ');normal=np.array([float(row['n'+d]) for d in 'xyz']);point=np.array([float(row['p'+d]) for d in 'xyz']);J=np.fromstring(row['jacobian'],sep=' ');force=float(row['force']);minimumForce=min(minimumForce,force);normError=max(normError,abs(np.linalg.norm(normal)-1));moment=max(moment,float(np.linalg.norm(np.cross(point-q[-6:-3],normal))));angular=max(angular,float(np.max(abs(J[-3:]))));records.append(dict(case=name,time_s=float(row['time']),finger=f,triangle=triangle,feature=feature,material_kind=kind,material_nodes=' '.join(map(str,support)),normal_force_N=force,gap_mm=float(row['gap'])))
 duplicates=[]
 for (time,f),rows in groups.items():
  if len(rows)<2:continue
  exact=all(np.array_equal(np.fromstring(x['stage_'+k],sep=' '),np.fromstring(rows[0]['stage_'+k],sep=' ')) for x in rows[1:] for k in ('q','v'))
  if not exact:raise ValueError('different physical states share a recorded epoch;cannot merge')
  forces=[float(x['force']) for x in rows];spread=max(forces)-min(forces);scale=max(map(abs,forces));duplicates.append(dict(time_s=float(time),finger=f,samples=len(rows),force_spread_N=spread,relative_spread_percent=100*spread/scale if scale else None))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 for name,rows in (('material_rows.csv',records),('same_state_force.csv',duplicates)):
  with (out/name).open('w') as stream:
   if rows:w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 transitions=[]
 for f in range(3):
  rr=sorted((x for x in records if x['finger']==f),key=lambda x:x['time_s']);previous=None
  for row in rr:
   identity=(row['material_kind'],row['material_nodes'])
   if previous and identity!=(previous['material_kind'],previous['material_nodes']):transitions.append(dict(finger=f,last_old_sample_s=previous['time_s'],first_new_sample_s=row['time_s'],old_kind=previous['material_kind'],old_nodes=previous['material_nodes'],new_kind=row['material_kind'],new_nodes=row['material_nodes'],continuous_event_time=None))
   previous=row
 result=dict(status='EXPERIMENTAL',scope='actual material-row lifetime and same-q/v/time multiplier inventory;NOT continuous event root/time convergence/contact area/grasp',sources=sources,normal_unit_error=normError,radial_unit_force_moment_arm_mm=moment,rigid_angular_J_max_abs=angular,minimum_recorded_normal_force_N=minimumForce,material_transitions=transitions,same_state_groups=len(duplicates),max_same_state_force_spread_N=max((x['force_spread_N'] for x in duplicates),default=None),max_same_state_relative_spread_percent=max((x['relative_spread_percent'] for x in duplicates if x['relative_spread_percent'] is not None),default=None),force_values='recorded endpoint and next initial multipliers retained separately;NOT averaged/corrected',contact_area=None,pressure=None,holding_load=None,raw_hashes={name:sha(out/name) for name in ('material_rows.csv','same_state_force.csv')});write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
