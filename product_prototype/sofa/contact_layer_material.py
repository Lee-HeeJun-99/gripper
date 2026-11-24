"""Actual detector->row->composite material coordinate,with explicit ambiguity.

Point index is Native vertex index. Lines match a UNIQUE geometric boundary
edge at strict1e-12;auto-generated Native edge ordering is NOT guessed.
"""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/contact_layer_provenance1353';baseline=BASE/'results/b3_contact_layer_union_entry1351';join=BASE/'results/contact_layer_provenance_join1354/summary.json';joined=json.loads(join.read_text());assert joined['all_unique'];assert all(joined['input_hashes'][str((src/f).relative_to(BASE))]==sha(src/f) for f in ('provenance.features.csv','provenance.children.csv'));assert json.loads((src/'preflight.json').read_text())['source_scene_sha256']==sha(baseline/'scene.scn');u=json.loads((baseline/'union_surface.json').read_text());g=json.loads((baseline/'pad_mesh.json').read_text());mesh=json.loads((baseline/'mesh.json').read_text());count=u['original_node_count'];used=np.array(u['used']);local=np.vstack([np.array(mesh['local_positions_mm']),np.array(g['local_positions_mm'])[1::2]])[used];tri=np.array(u['triangles']);edges=np.array(sorted({tuple(sorted((int(a),int(b)))) for f in tri for a,b in zip(f,np.roll(f,-1))}));incident={i:set() for i in range(len(used))}
 for f,material in zip(tri,u['face_material']):
  label='layer' if material=='layer' else 'rail' if np.min(local[f,2])<0 else 'Skin'
  for i in f:incident[int(i)].add(label)
 obj=read(src/'object.csv');times=[float(r['time_s']) for r in obj];index={t:k for k,t in enumerate(times)};response={(float(r['time_s']),int(r['row_id'])):r for r in read(src/'response_rows.csv')};film=[read(src/f'finger{i}.csv') for i in range(3)];pad=[read(src/f'contact_layer{i}.csv') for i in range(3)];records=[];unmapped=[]
 for record in joined['records']:
  prev=record['previous_time_s'];k=index[prev];assert k+1<len(times);accepted=times[k+1];row=record['row'];r=response[(accepted,row)];lam=float(r['lambda_Ns']);f=record['detector']
  if lam<=0:continue
  object_side=0 if '/object/'in f['model0'] else 1;side=1-object_side;model=f[f'model{side}'];m=re.fullmatch(r'/contactLayer(\d+)/exterior/(Point|Line)CollisionModel\d*',model)
  if not m:unmapped.append(dict(row=row,reason='UNSUPPORTED_MODEL',model=model));continue
  finger=int(m[1]);point=np.fromstring(f[f'point{side}'],sep=' ');assert {r['model0'],r['model1']}=={f['model0'],f['model1']}
  def positions(step):
   assert float(film[finger][step]['time_s'])==float(pad[finger][step]['time_s'])==times[step]
   q=np.fromstring(film[finger][step]['q_m'],sep=' ').reshape(-1,3);p=np.fromstring(pad[finger][step]['q'],sep=' ').reshape(-1,3);return np.vstack([q,p[1::2]])[used]
  before=positions(k);after=positions(k+1)
  if m[2]=='Point':parents=[int(f[f'element{side}'])];weights=np.array([1.]);matching='Native Point vertex index'
  else:
   A=before[edges[:,0]];B=before[edges[:,1]];D=B-A;s=np.einsum('ij,ij->i',point-A,D)/np.einsum('ij,ij->i',D,D);err=np.max(abs(A+s[:,None]*D-point),axis=1);found=np.flatnonzero((s>=0)&(s<=1)&(err<=1e-12))
   if len(found)!=1:unmapped.append(dict(row=row,reason='NONUNIQUE_GEOMETRIC_EDGE',matches=len(found),element_index=f[f'element{side}']));continue
   n=int(found[0]);parents=edges[n].tolist();weights=np.array([1-s[n],s[n]]);matching='UNIQUE actual previous-coordinate edge;Native edge ordering NOT inferred'
  error=float(abs(weights@before[parents]-point).max());assert error<=1e-12;normal=np.fromstring(f['normal'],sep=' ')*(1 if object_side==1 else -1);I=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ');ie=float(abs(I[:3]-normal*lam).max());assert ie<=1e-12;materials=set.intersection(*(incident[p] for p in parents));label=next(iter(materials)) if len(materials)==1 else 'AMBIGUOUS_INTERFACE';records.append(dict(previous_time_s=prev,accepted_time_s=accepted,row=row,finger=finger,feature_type=m[2],native_element_index=int(f[f'element{side}']),matching=matching,composite_vertex_indices=parents,weights=weights.tolist(),material_reference_mm=(weights@local[parents]).tolist(),incident_materials=sorted(materials),material_label=label,normal_on_object=normal.tolist(),normal_force_N=lam/.0025,object_normal_impulse_error_Ns=ie,detector_previous_parent_error_m=error,detector_next_parent_difference_m=float(abs(weights@after[parents]-point).max())))
 span=[r['material_reference_mm'][0] for r in records];d=dict(status='PASS_COMPOSITE_MATERIAL_PROVENANCE_ONLY' if records and not unmapped else 'PARTIAL_MATERIAL_PROVENANCE',records=records,unmapped_active_rows=unmapped,mapped_material_station_span_mm=[min(span),max(span)] if span else None,scope='Actual uniquely joined active normal rows in two sampled windows only. Explicit interface ambiguity;no contact area,pressure,global wrapping,Holding or force-capacity claim.',physical_validation='NOT QUALIFIED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (join,baseline/'union_surface.json',baseline/'pad_mesh.json',src/'scene.scn',src/'object.csv',src/'response_rows.csv')});(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(status=d['status'],records=len(records),unmapped=len(unmapped),span=d['mapped_material_station_span_mm'],labels=sorted({r['material_label'] for r in records}))))
if __name__=='__main__':main()
