"""Exact recorded-clock join:Native detector -> child row -> impulse -> Skin node."""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(f):return list(csv.DictReader(f.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',default='b3_existing_provenance1315');p.add_argument('--join',default='b3_provenance_join1316');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.source;join=BASE/'results'/a.join/'summary.json';joined=json.loads(join.read_text());assert joined['all_unique'];assert all(joined['input_hashes'][str((src/f).relative_to(BASE))]==sha(src/f) for f in ('provenance.features.csv','provenance.children.csv'));obj=read(src/'object.csv');times=[float(r['time_s']) for r in obj];index={t:i for i,t in enumerate(times)};response={}
 for r in read(src/'response_rows.csv'):
  key=(float(r['time_s']),int(r['row_id']));assert key not in response;response[key]=r
 tree=ET.parse(src/'scene.scn');root=tree.getroot();local=np.array(json.loads((BASE/'results/b3_railback_grasp1001298/mesh.json').read_text())['local_positions_mm']);films=[read(src/f'finger{i}.csv') for i in range(3)];records=[];unmapped_active=[]
 for j in joined['records']:
  prev=j['previous_time_s'];k=index[prev];assert k+1<len(times);accepted=times[k+1];r=response[(accepted,j['row'])];f=j['detector'];assert {r['model0'],r['model1']}=={f['model0'],f['model1']};lam=float(r['lambda_Ns'])
  if lam<=0 or 'skinCollision'not in f['model0']+f['model1']:continue
  object_side=0 if '/object/'in f['model0'] else 1;direction=np.fromstring(f['normal'],sep=' ')*(1 if object_side==1 else -1);I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');impulse_error=float(abs(I[:3]-lam*direction).max());assert impulse_error<=1e-12;side=1-object_side;model=f[f'model{side}'];m=re.fullmatch(r'/finger(\d+)/skinCollision/(Point|Line)CollisionModel\d*',model)
  if not m:unmapped_active.append(dict(previous_time_s=prev,accepted_time_s=accepted,row=j['row'],model=model,normal_N=lam/.0025));continue
  finger=int(m.group(1));skin=root.find(f"./Node[@name='finger{finger}']/Node[@name='skinCollision']");indices=np.fromstring(skin.find('SubsetMapping').get('indices'),sep=' ',dtype=int);element=int(f[f'element{side}']);point=np.fromstring(f[f'point{side}'],sep=' ');qb=np.fromstring(films[finger][k]['q_m'],sep=' ').reshape(-1,3);qa=np.fromstring(films[finger][k+1]['q_m'],sep=' ').reshape(-1,3)
  if m.group(2)=='Point':parents=[int(indices[element])];weights=np.array([1.])
  else:
   edges=np.fromstring(skin.find('MeshTopology').get('edges'),sep=' ',dtype=int).reshape(-1,2);parents=indices[edges[element]].tolist();A,B=qb[parents];s=float(np.dot(point-A,B-A)/np.dot(B-A,B-A));assert 0<=s<=1,'line point outside declared segment';weights=np.array([1-s,s])
  before=weights@qb[parents];after=weights@qa[parents];rec=dict(previous_time_s=prev,accepted_time_s=accepted,row=j['row'],finger=finger,feature_type=m.group(2),detector_element_index=element,parent_FEM_nodes=parents,interpolation_weights=weights.tolist(),material_reference_mm=(weights@local[parents]).tolist(),actual_detector_point_m=point.tolist(),normal_on_object=direction.tolist(),normal_force_N=lam/.0025,object_normal_impulse_error_Ns=impulse_error,detector_vs_previous_accepted_parent_error_m=float(abs(point-before).max()),detector_vs_next_accepted_parent_error_m=float(abs(point-after).max()));records.append(rec)
 clean=bool(records) and all(r['detector_vs_previous_accepted_parent_error_m']<=1e-12 for r in records)
 d=dict(status='PASS_ACTIVE_POINT_ROW_MATERIAL_PROVENANCE_ONLY' if clean else 'FAIL_POINT_PARENT_PHASE_ALIGNMENT',records=records,unmapped_active_skin_rows=unmapped_active,physical_validation='NOT QUALIFIED',scope='Actual unique detector/childnormal/response row with Point SubsetMapping or explicitly declared Line edge interpolation,verified at previousaccepted coordinates. Explicit clockindex join,not dt multiplication. Triangle interpolation not inferred. No area,pressure,Wrapping,capacity or causal claim.',input_hashes={str(join.relative_to(BASE)):sha(join),**{str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv','finger0.csv','finger1.csv','finger2.csv')}});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
