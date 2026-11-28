"""Actual P1 circular floor contrasts: separate algorithm, mesh, upper quadrature and path.
No pair of local references qualifies the integrated system or time convergence.
"""
import sys,json,shutil,itertools,numpy as np
from baseline_registry import ROOT,REPO,ref,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[];arrays=[]
def rms(p,t,u):
 v=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6
 return float(np.sqrt(np.sum(v[:,None]*(u[t].sum(1)**2+np.sum(u[t]**2,axis=1)))/(20*v.sum())))
for tag in sys.argv[2:]:
 sp=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(sp.read_text());a=np.load(sp.parent/'field.npz');p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];arrays.append(dict(p=p,t=t,u=u,F=a['load_N']))
 rows.append(dict(source=ref(sp),candidate=s['candidate'],h_mm=s['h_mm'],algorithm=('CIRCULAR_PROXIMAL' if s.get('exact_circular_proximal_ADMM') else 'ADAPTIVE_CIRCULAR_SUPPORT' if s.get('adaptive_circular_support_cuts') else 'INSCRIBED_POLYGON_'+str(s.get('friction_polygon_vertices',4))),upper_face_triangle_quadrature_points=s.get('upper_face_triangle_quadrature_points',3),quasistatic_load_fractions=s.get('quasistatic_load_fractions',[.1,.25,.5,1.]),full_load_local_pass=bool(all(s['checks'].values()) and s['accepted_load_fraction']==1.),accepted_fraction=s['accepted_load_fraction'],elastic_energy_Nmm=s['static_energy_Nmm'],volume_RMS_mm=rms(p,t,u),discrete_increment_friction_sum_Nmm=sum(q['step_friction_dissipation_Nmm'] for q in s['accepted_steps']),maximum_displacement_mm=s['maximum_displacement_mm'],last_law=s['last_law'],peak_RSS_KiB=s['peak_RSS_KiB']))
 accepted_geometry=[]
 for step in s['accepted_steps']:
  fp=sp.parent/f"trial_{step['fraction']:g}_{step['outer_iterations']-1:02d}.npz"
  v=np.load(fp);floor=v['floor_nodes'];du=(v['displacement_mm']-v['previous_displacement_mm'])[floor,:2];length=np.linalg.norm(du,axis=1);normal=v['reaction_N'][floor,2];T=v['reaction_N'][floor,:2];diss=-np.einsum('ij,ij->i',T,du)
  accepted_geometry.append(dict(field=ref(fp),fraction=step['fraction'],exact_circular_maximum_slip_mm=float(length.max()),compressive_contact_nodes=int((normal>1e-7).sum()),compressive_sliding_nodes=int(((normal>1e-7)&(length>1e-9)).sum()),circular_maximum_dissipation_error_Nmm=float(abs(diss-.3*np.maximum(normal,0)*length).max())))
 rows[-1]['accepted_step_circular_geometry']=accepted_geometry
 assert rows[-1]['candidate']==rows[0]['candidate']
pairs=[]
for i,j in itertools.combinations(range(len(rows)),2):
 a,b=rows[i],rows[j];vary=[k for k in ['h_mm','algorithm','upper_face_triangle_quadrature_points','quasistatic_load_fractions'] if a[k]!=b[k]]
 valid=a['full_load_local_pass'] and b['full_load_local_pass'];metrics={k:(abs(b[k]/a[k]-1) if a[k] else None) for k in ['elastic_energy_Nmm','volume_RMS_mm','discrete_increment_friction_sum_Nmm']}
 pair=dict(sources=[a['source'],b['source']],varied=vary,comparable_full_load=valid,relative_changes=metrics,one_percent_all_scalar_metrics=bool(valid and all(v is not None and v<=.01 for v in metrics.values())))
 aa,bb=arrays[i],arrays[j]
 if np.array_equal(aa['p'],bb['p']) and np.array_equal(aa['t'],bb['t']):
  dr=rms(aa['p'],aa['t'],bb['u']-aa['u']);pair.update(full_vector_difference_RMS_mm=dr,relative_full_vector_RMS=dr/a['volume_RMS_mm'],one_percent_full_vector=bool(valid and dr/a['volume_RMS_mm']<=.01),max_nodal_applied_load_difference_N=float(abs(bb['F']-aa['F']).max()))
 if vary==['h_mm']:pair['scope']='Coupled tetra AND nodal floor/upper quadrature contrast; not isolated bulk convergence'
 elif vary==['upper_face_triangle_quadrature_points']:pair['scope']='Isolated upper affine reference traction quadrature, same actual mesh/floor DOFs/wrenches; NOT actual upper constitutive contact'
 elif vary==['quasistatic_load_fractions']:pair['scope']='Quasistatic load-path subdivision; NOT dt or continuous friction-loss/global energy proof'
 else:pair['scope']='Algorithm/approximation comparison or mixed variables; NOT spatial/time convergence'
 pairs.append(pair)
dump(out/'summary.json',dict(status='ACTUAL_P1_CIRCULAR_FLOOR_ALGORITHM_QUADRATURE_MESH_PATH_CONTRASTS_NOT_RELEASE',producer=ref(out/'producer.py'),candidate=rows[0]['candidate'],rows=rows,all_pairs=pairs,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Original spatial1percent/time.1percent unchanged; all22system gates remain unqualified.','Full-vector differences include actual floor-relative rigid motion; no arbitrary alignment removes it. Across different meshes only scalar continuum norms are compared, not a matched vector field.','Affine upper wrench references and assumed material/mu remain conditional; no83body operating equilibrium, strength, preload, hardware or global energy certification.','All partial/failed fields are retained but never accepted for convergence.']))
print(json.dumps(dict(rows=len(rows),pairs=pairs)))
