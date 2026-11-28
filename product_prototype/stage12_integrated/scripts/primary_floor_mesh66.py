"""Actual full-plate mesh contrasts; ALL adjacent and coarse/finest pairs.
Exact P1 continuum volume RMS includes physical floor-referenced rigid motion.
No correspondence of nodal maxima is claimed. No system/time/strength PASS.
"""
import sys,json,shutil,itertools,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
for tag in sys.argv[2:]:
 p=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(p.read_text());a=np.load(p.parent/'field.npz');x=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];v=abs(np.linalg.det(x[t[:,1:]]-x[t[:,0,None]]))/6
 rms=float(np.sqrt(np.sum(v[:,None]*(np.sum(u[t],axis=1)**2+np.sum(u[t]**2,axis=1)))/(20*v.sum())))
 floor=a['floor_nodes'];r=a['reaction_N'];normal=r[floor,2];valid_contact=normal>1e-7
 rows.append(dict(source=ref(p),h_mm=s['h_mm'],full_load_and_law=all(s['checks'].values()) and s['accepted_load_fraction']==1.,nodes=s['nodes'],tetra=s['tetra'],energy_Nmm=s['static_energy_Nmm'],continuum_RMS_mm=rms,peak_displacement_mm=s['maximum_displacement_mm'],endpoint_step_friction_sum_Nmm=sum(q['step_friction_dissipation_Nmm'] for q in s['accepted_steps']),compressive_contact_nodes=int(valid_contact.sum()),open_or_negligible_normal_floor_nodes=int((~valid_contact).sum()),total_normal_N=float(normal.sum()),total_floor_tangent_N=r[floor,:2].sum(0).tolist(),peak_RSS_KiB=s['peak_RSS_KiB']))
 assert s['candidate']==json.loads((REPO/rows[0]['source']['path']).read_text())['candidate']
pairs=[]
for a,b in itertools.combinations(rows,2):
 d={k:abs(b[k]/a[k]-1) for k in ['energy_Nmm','continuum_RMS_mm','endpoint_step_friction_sum_Nmm']};pairs.append(dict(h_mm=[a['h_mm'],b['h_mm']],relative_changes=d,threshold_fraction=.01,local_mesh_1percent=all(z<=.01 for z in d.values()) and a['full_load_and_law'] and b['full_load_and_law']))
dump(out/'summary.json',dict(status='ACTUAL_FULL_P1_FLOOR_MESH_CONTRASTS_NOT_SYSTEM_CERTIFICATION',producer=ref(out/'producer.py'),candidate=s['candidate'],rows=rows,all_pairs=pairs,all_pairs_local_mesh_1percent=bool(pairs) and all(q['local_mesh_1percent'] for q in pairs),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['IdenticalactualCAD,upperreferencewrenches,materialandfloorassumptions;not actualuppercontactlaws.','ExactcontinuousvolumeRMSandenergycompared;peaknodaldisplacementsnotmatchedmesherrornorm.','Endpointincrementfrictionsumsnotcontinuousloss,timeor globalenergy.','Noindependenttimecriterion,source-minimumstrengthor83bodyequilibrium;all22UNQUALIFIED.']))
print(json.dumps(pairs))
