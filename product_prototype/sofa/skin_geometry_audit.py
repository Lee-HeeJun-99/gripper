"""Independent accepted-state Skin geometry check against actual row impulses."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('completed trial required')
 tree=ET.parse(src/'scene.scn');c=json.loads((src/'config.json').read_text());objectrows=read(src/'object.csv');objects=np.array([np.fromstring(r['rigid_q'],sep=' ')[:3] for r in objectrows]);time=np.array([float(r['time_s']) for r in objectrows]);index={t:k for k,t in enumerate(time)};active=np.zeros((len(time),meta['fingers']),dtype=bool)
 provenance='direct Contact response rows' if (src/'response_rows.csv').exists() else 'legacy child-J INFLUENCE ONLY,not direct-contact provenance'
 for row in read(src/'response_rows.csv' if (src/'response_rows.csv').exists() else src/'skin_rows.csv'):
  for f in range(meta['fingers']):
   direct=(any('/object/' in row[k] for k in ('model0','model1')) and any(f'/finger{f}/skinCollision/' in row[k] for k in ('model0','model1'))) if (src/'response_rows.csv').exists() else bool(int(row['film_mask'])&(1<<f))
   if direct and abs(float(row['lambda_Ns']))>0:active[index[float(row['time_s'])],f]=True
 records=[];mapping_errors=[]
 for f in range(meta['fingers']):
  node=tree.find(f"./Node[@name='finger{f}']/Node[@name='skinCollision']");ids=np.fromstring(node.find('SubsetMapping').get('indices'),sep=' ',dtype=int);tri=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);body=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3)[ids] for r in read(src/f'finger{f}.csv')]);file=src/f'skin_points{f}.csv'
  points=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in read(file)]) if file.exists() else body
  if file.exists():mapping_errors.append(float(np.max(abs(body-points))))
  for k,q in enumerate(points):
   closest=trimesh.triangles.closest_point(q[tri],np.repeat(objects[k,None,:],len(tri),axis=0));gap=float(np.linalg.norm(closest-objects[k],axis=1).min()-c['simulation']['sphere_radius_mm']*.001);records.append(dict(time_s=time[k],finger=f,minimum_skin_gap_mm=gap*1000,active_skin_impulse=bool(active[k,f])))
 selected=[r for r in records if r['active_skin_impulse']];contact=c['simulation']['contact_distance_mm'];worst=max(selected,key=lambda r:r['minimum_skin_gap_mm']) if selected else None
 result=dict(status='FAIL' if worst and worst['minimum_skin_gap_mm']>contact else 'DIAGNOSTIC_ONLY',scope='accepted-state global Skin nearest gap vs active row;not per-row complementarity or swept clearance certification',case=a.case,mapping_query_max_error_m=max(mapping_errors) if mapping_errors else None,contact_distance_mm=contact,worst_active_gap=worst,minimum_gap_mm=min(r['minimum_skin_gap_mm'] for r in records),source_sha256=sha(Path(__file__)),input_hashes={x.name:sha(x) for x in src.glob('*.csv')},note='positive gap with impulse requires collision/proximity/linearization diagnosis;do not certify Skin holding from row force alone')
 result['contact_provenance']=provenance
 with (out/'geometry.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
