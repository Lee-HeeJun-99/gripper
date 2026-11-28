"""Same actual P1 plate: distinguish mesh from friction-direction convergence.
Only full-load physically admissible local fields enter qualified contrasts.
"""
import sys,json,shutil,itertools,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
for tag in sys.argv[2:]:
 sp=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(sp.read_text());a=np.load(sp.parent/'field.npz');p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];F=a['load_N'];r=a['reaction_N'];floor=a['floor_nodes'];v=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6;normal=r[floor,2];T=r[floor,:2];nd=s.get('friction_polygon_vertices',4)
 rms=float(np.sqrt(np.sum(v[:,None]*(np.sum(u[t],axis=1)**2+np.sum(u[t]**2,axis=1)))/(20*v.sum())))
 # Full displacement map, not last-increment displacement, for endpoint work.
 endpoint_circle=float(np.sum(.3*np.maximum(normal,0)*np.linalg.norm(u[floor,:2],axis=1)));actual_endpoint=float(-np.sum(T*u[floor,:2]))
 row=dict(source=ref(sp),h_mm=s['h_mm'],friction_directions=nd,full_load_local_physical_pass=all(s['checks'].values()) and s['accepted_load_fraction']==1.,accepted_fraction=s['accepted_load_fraction'],attempt_fraction=s['current_attempt_fraction'],nodes=s['nodes'],tetra=s['tetra'],elastic_energy_Nmm=s['static_energy_Nmm'],exact_continuum_volume_RMS_mm=rms,endpoint_increment_loss_sum_Nmm=sum(q['step_friction_dissipation_Nmm'] for q in s['accepted_steps']),final_reaction_displacement_work_Nmm=actual_endpoint,circular_support_endpoint_Nmm=endpoint_circle,circular_support_shortfall_Nmm=endpoint_circle-actual_endpoint,minimum_circular_cone_slack_N=float((.3*np.maximum(normal,0)-np.linalg.norm(T,axis=1)).min()),compressive_floor_nodes=int(np.sum(normal>1e-7)),raw_floor_tangent_moving_nodes=s['accepted_steps'][-1]['sliding_nodes'] if s['accepted_steps'] else None,maximum_displacement_mm=s['maximum_displacement_mm'],minimum_normal_N=float(normal.min()),peak_RSS_KiB=s['peak_RSS_KiB'])
 rows.append(row)
pairs=[]
for a,b in itertools.combinations(rows,2):
 if a['h_mm']==b['h_mm'] and a['friction_directions']!=b['friction_directions']:kind='FRICTION_ANGULAR';same=True
 elif a['h_mm']!=b['h_mm'] and a['friction_directions']==b['friction_directions']:kind='SPATIAL_MESH';same=True
 else:kind='MIXED_OR_SAME';same=False
 valid=same and a['full_load_local_physical_pass'] and b['full_load_local_physical_pass'];metrics={k:abs(b[k]/a[k]-1) if a[k] else None for k in ['elastic_energy_Nmm','exact_continuum_volume_RMS_mm','endpoint_increment_loss_sum_Nmm']}
 pairs.append(dict(kind=kind,sources=[a['source'],b['source']],h_mm=[a['h_mm'],b['h_mm']],friction_directions=[a['friction_directions'],b['friction_directions']],comparable_accepted_full_load=valid,relative_changes=metrics,threshold_fraction=.01,all_reported_metrics_within1percent=bool(valid and all(z is not None and z<=.01 for z in metrics.values()))))
# Exact same-mesh comparisons retain full vector differences (including rigid motion).
vector_pairs=[]
for a,b in itertools.combinations(rows,2):
 if a['h_mm']!=b['h_mm'] or not(a['full_load_local_physical_pass'] and b['full_load_local_physical_pass']):continue
 aa=np.load((REPO/a['source']['path']).parent/'field.npz');bb=np.load((REPO/b['source']['path']).parent/'field.npz');assert np.array_equal(aa['points_mm'],bb['points_mm']) and np.array_equal(aa['tetra'],bb['tetra']);p=aa['points_mm'];t=aa['tetra'];v=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6;du=bb['displacement_mm']-aa['displacement_mm'];drms=float(np.sqrt(np.sum(v[:,None]*(du[t].sum(1)**2+np.sum(du[t]**2,axis=1)))/(20*v.sum())));vector_pairs.append(dict(friction_directions=[a['friction_directions'],b['friction_directions']],exact_continuum_vector_difference_RMS_mm=drms,relative_to_first_RMS=drms/a['exact_continuum_volume_RMS_mm'],within1percent=drms/a['exact_continuum_volume_RMS_mm']<=.01))
dump(out/'summary.json',dict(status='ACTUAL_P1_FULL_PLATE_SPATIAL_ANGULAR_CONTRASTS_NOT_SYSTEM_CERTIFICATE',producer=ref(out/'producer.py'),candidate=s['candidate'],rows=rows,all_pairs=pairs,all_same_mesh_vector_pairs=vector_pairs,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['IdenticalactualproductSTEPandexplicitupperNeumannwrenchreference;not83bodyconstitutivecontactequilibrium.','Frictionangularandspatialmeshareseparatevariables;failedpartialloadsneverenterqualifiedconvergence.','Endpointincrementslossisadiscreteconditionalpathquantity;NOtime,continuousfrictionorglobalenergycertificate.','Rawsliding_nodesincludesopenfloornodes;tangentmotiondoesnotproveactivecontactsliding.','Alloriginal22criteriaretained,assumedmu/materialandunmeasuredfloor/uppersettingremain.']))
print(json.dumps(dict(rows=len(rows),pairs=pairs,vector_pairs=vector_pairs)))
