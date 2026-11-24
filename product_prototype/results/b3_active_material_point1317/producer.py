"""Exact recorded-clock join:Native detector -> child row -> impulse -> Skin node."""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(f):return list(csv.DictReader(f.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_existing_provenance1315';join=BASE/'results/b3_provenance_join1316/summary.json';joined=json.loads(join.read_text());assert joined['all_unique'];obj=read(src/'object.csv');times=[float(r['time_s']) for r in obj];index={t:i for i,t in enumerate(times)};response={}
 for r in read(src/'response_rows.csv'):
  key=(float(r['time_s']),int(r['row_id']));assert key not in response;response[key]=r
 tree=ET.parse(src/'scene.scn');root=tree.getroot();local=np.array(json.loads((BASE/'results/b3_railback_grasp1001298/mesh.json').read_text())['local_positions_mm']);films=[read(src/f'finger{i}.csv') for i in range(3)];records=[];unmapped_active=[]
 for j in joined['records']:
  prev=j['previous_time_s'];k=index[prev];assert k+1<len(times);accepted=times[k+1];r=response[(accepted,j['row'])];f=j['detector'];assert {r['model0'],r['model1']}=={f['model0'],f['model1']};lam=float(r['lambda_Ns'])
  if lam<=0 or 'skinCollision'not in f['model0']+f['model1']:continue
  object_side=0 if '/object/'in f['model0'] else 1;direction=np.fromstring(f['normal'],sep=' ')*(1 if object_side==1 else -1);I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');impulse_error=float(abs(I[:3]-lam*direction).max());assert impulse_error<=1e-12;side=1-object_side;model=f[f'model{side}'];m=re.fullmatch(r'/finger(\d+)/skinCollision/PointCollisionModel\d*',model)
  if not m:unmapped_active.append(dict(previous_time_s=prev,accepted_time_s=accepted,row=j['row'],model=model,normal_N=lam/.0025));continue
  finger=int(m.group(1));indices=np.fromstring(root.find(f"./Node[@name='finger{finger}']/Node[@name='skinCollision']/SubsetMapping").get('indices'),sep=' ',dtype=int);element=int(f[f'element{side}']);parent=int(indices[element]);point=np.fromstring(f[f'point{side}'],sep=' ');before=np.fromstring(films[finger][k]['q_m'],sep=' ').reshape(-1,3)[parent];after=np.fromstring(films[finger][k+1]['q_m'],sep=' ').reshape(-1,3)[parent];rec=dict(previous_time_s=prev,accepted_time_s=accepted,row=j['row'],finger=finger,detector_point_index=element,parent_FEM_node=parent,material_reference_mm=local[parent].tolist(),actual_detector_point_m=point.tolist(),normal_on_object=direction.tolist(),normal_force_N=lam/.0025,object_normal_impulse_error_Ns=impulse_error,detector_vs_previous_accepted_parent_error_m=float(abs(point-before).max()),detector_vs_next_accepted_parent_error_m=float(abs(point-after).max()));records.append(rec)
 clean=bool(records) and all(r['detector_vs_previous_accepted_parent_error_m']<=1e-12 for r in records)
 d=dict(status='PASS_ACTIVE_POINT_ROW_MATERIAL_PROVENANCE_ONLY' if clean else 'FAIL_POINT_PARENT_PHASE_ALIGNMENT',records=records,unmapped_active_nonpoint_skin_rows=unmapped_active,physical_validation='NOT QUALIFIED',scope='Unique actual detector/childnormal/response row/PointCollisionModel SubsetMapping link and explicit previous→next accepted clock. Nonpoint material interpolation not inferred. No contactarea,pressure,Wrapping,capacity or causal claim.',input_hashes={str(join.relative_to(BASE)):sha(join),**{str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','object.csv','response_rows.csv','finger0.csv','finger1.csv','finger2.csv')}});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
