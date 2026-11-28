"""Independent actual P1 floor field30resultant and direct-component cone audit.
No product strength/material/friction certification, source assumptions retained.
"""
import sys,json,shutil,itertools
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_floor65c';s=json.loads((src/'summary.json').read_text());assert all(s['checks'].values());cp=REPO/s['candidate']['path'];assert sha(cp)==s['candidate']['SHA256'];cad=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);d=json.loads((src/'contact_fields.json').read_text());ld=json.loads((src/'load_ledger.json').read_text());patches=json.loads((REPO/ld['source_upper_patches']['path']).read_text());ports=json.loads((REPO/ld['source_ports']['path']).read_text())['ports'];names=json.loads((REPO/ld['source_load_ledger']['path']).read_text())['body_names'];bi={n:i for i,n in enumerate(names)};feet=json.loads((REPO/cad['ground']['path']).read_text())['feet'];E=np.array(ld['external_wrench_N_Nm']);rows=[]
def w(p,f):return np.r_[f,np.cross(np.array(p)/1000,f)]
for group in ['rows','spatial_contrasts','negative_controls','six_wrench_perturbations','one_foot_absent']:
 for q in d[group]:
  if not q['feasible']:continue
  mu=q['ground_mu_ASSUMED'];cols=[]
  for p in patches:
   tang=[a for a in range(3) if a!=p['axis']]
   for c in p['cells']:
    for a,sign in [(tang[0],1),(tang[0],-1),(tang[1],1),(tang[1],-1)]:
     f=np.array(p['normal_on_i'],float);f[a]+=.3*sign;col=np.zeros((5,6));col[bi[p['body_i']]]+=w(c['point_mm'],f);col[bi[p['body_j']]]-=w(c['point_mm'],f);cols.append(col.ravel())
  for p in ports:
   col=np.zeros((5,6));col[bi[p['body_i']]]+=w(p['point_mm'],p['direction']);col[bi[p['body_j']]]-=w(p['point_mm'],p['direction']);cols.append(col.ravel())
  first=len(cols);n=int(round(q['cells_per_foot']**.5))
  for i,ft in enumerate(feet):
   if i in q['removed_feet']:continue
   a=ft['contact_bounds_mm']
   for ix,iy in itertools.product(range(n),repeat=2):
    p=[a[0]+(ix+.5)*(a[3]-a[0])/n,a[1]+(iy+.5)*(a[4]-a[1])/n,-170.]
    for ax,sign in [(0,-1),(0,1),(1,-1),(1,1)]:
     f=np.array([0.,0,1]);f[ax]=sign*mu;col=np.zeros((5,6));col[bi['EXTERNAL_BENCH_PLATE']]=w(p,f);cols.append(col.ravel())
  A=np.array(cols).T;coeff=np.array(q['full_ray_coefficients']);external=np.array(q['external_wrench_N_Nm']);bal=(A@coeff).reshape(5,6)+external;err=float(abs(bal).max());cells=q['floor_cells'];floorw=sum((w(c['point_mm'],c['force_N']) for c in cells),np.zeros(6));target=-external.sum(0);grounderr=float(abs(floorw-target).max());slack=min(mu*c['normal_N']-abs(c['force_N'][0])-abs(c['force_N'][1]) for c in cells);pressuremax=max(c['pressure_MPa'] for c in cells)
  # Wrong environmental contact height must alter horizontal-force moment arm.
  wrongw=sum((w([*c['point_mm'][:2],0],c['force_N']) for c in cells),np.zeros(6));wrongerr=float(abs(wrongw-target).max());seed=np.arange(30).reshape(5,6)/23.;work=float(np.sum((A@coeff).reshape(5,6)*seed)+np.sum(external*seed));rows.append(dict(group=group,label=q['label'],n=n,full30row_error=err,ground6row_error=grounderr,physical_virtualwork_error=work,nonnegative_ray_min=float(coeff.min()),minimum_friction_diamond_slack_N=slack,peak_pressure_error_MPa=abs(pressuremax-q['minimum_peak_uniform_cell_pressure_MPa']),wrong_floor_height_rejected=wrongerr>1e-4,wrong_floor_height_residual=wrongerr))
# INDEPENDENTforce-component formulation: no friction rays,6eqs,4inequalities/cell.
points=[];areas=[]
for ft in feet:
 a=ft['contact_bounds_mm']
 for i,j in itertools.product(range(2),repeat=2):points.append([a[0]+(i+.5)*10,a[1]+(j+.5)*10,-170.]);areas.append(100.)
B=np.column_stack([w(p,e) for p in points for e in np.eye(3)]);target=-E.sum(0)
def direct(mu):
 G=[]
 for i in range(len(points)):
  for sx,sy in itertools.product([-1,1],repeat=2):
   c=np.zeros(3*len(points));c[3*i:3*i+3]=[sx,sy,-mu];G.append(c)
 scale=np.array([1,1,1,100,100,100]);res=linprog(np.zeros(B.shape[1]),A_ub=np.array(G),b_ub=np.zeros(len(G)),A_eq=scale[:,None]*B,b_eq=scale*target,bounds=[b for _ in points for b in [(None,None),(None,None),(0,None)]],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});return res
lo=0.;hi=.1
for _ in range(30):
 m=(lo+hi)/2
 if direct(m).success:hi=m
 else:lo=m
r=direct(.3);directerr=float(abs(B@r.x-target).max()) if r.success else None
threshold=s['conditional_ground_mu_min_bracket'];checks=dict(actual83hashes=True,all_saved_30rows_reconstructed=all(r['full30row_error']<1e-8 for r in rows),all_ground6rows_reconstructed=all(r['ground6row_error']<1e-8 for r in rows),all_physical_work=all(abs(r['physical_virtualwork_error'])<1e-8 for r in rows),nonnegative_and_actual_floor_friction=all(r['nonnegative_ray_min']>-1e-9 and r['minimum_friction_diamond_slack_N']>-1e-8 for r in rows),peak_pressure=all(r['peak_pressure_error_MPa']<1e-8 for r in rows),wrong_floor_height_controls=all(r['wrong_floor_height_rejected'] for r in rows),independent_components_feasible=bool(r.success),independent_component_balance=directerr is not None and directerr<1e-8,independent_threshold_matches=abs((lo+hi)/2-sum(threshold)/2)<1e-7,failed_controls_retain_infeasibility=all(not q['feasible'] for q in d['negative_controls']))
dump(out/'summary.json',dict(status='INDEPENDENT_ACTUAL_FLOOR30ROW_COMPONENT_CONE_VERIFIED_NOT_RELEASE' if all(checks.values()) else 'INDEPENDENT_ACTUAL_FLOOR_VERIFICATION_FAIL',candidate=ref(cp),source=ref(src/'summary.json'),producer=ref(out/'producer.py'),checks=checks,verified_successful_fields=len(rows),rows=rows,independent_direct_components_ground_mu_bracket=[lo,hi],independent6row_balance_error_N_Nm=directerr,ground_force_moment_N_Nm=target.tolist(),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['IndependentdifferentLPvariableparameterization verifies sameconditionalrigidfinite-floorcone,notmaterial/frictiontruth.','Unknownupper10connectorconstitutivelaws/installedpreload remain. No elasticmesh/time/globalenergy or83bodyequilibrium certificate.']))
print(json.dumps(dict(checks=checks,threshold=[lo,hi],verified_fields=len(rows))));raise SystemExit(0 if all(checks.values()) else 2)
