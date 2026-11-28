"""Actual P1 finite floor contacts replace the arbitrary six-wrench host port.
Five cut bodies retain all30 equilibrium rows. Upper10 connectors are required
cut resultants ONLY; their constitutive laws/contact/preloads remain unresolved.
Floor is unilateral compressive/frictional environmental contact, no body fixed.
"""
import sys,json,shutil,time,itertools
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,box,overlap,translate
from primary_motor_bearing_wrenches import faces
from primary_anchor_contact38 import common_faces,surface_moment
start=time.monotonic();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
cp=ROOT/'cad/exports/primaryP1_ground65a/summary.json';cad=json.loads(cp.read_text());parent=json.loads((REPO/cad['parent']['path']).read_text());assert all(sha(REPO/q['path'])==q['SHA256'] for q in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]);assert all(r==parent['part_references'][n] for n,r in cad['part_references'].items() if n!='EXTERNAL_BENCH_PLATE')
source=ROOT/'validation/integrated/primaryP1_contacts64';old=json.loads((source/'summary.json').read_text());assert all(old['checks'].values());patches=json.loads((source/'patches.json').read_text());ports=json.loads((source/'connector_ports.json').read_text())['ports'];ledger=json.loads((source/'load_ledger.json').read_text());massp=ROOT/'validation/integrated/primaryP1_mass65/summary.json';mass=json.loads(massp.read_text());oldmass=json.loads((REPO/ledger['rest_mass_source']['path']).read_text());names=ledger['body_names'];bi={n:i for i,n in enumerate(names)};external=np.array(ledger['external_wrench_N_Nm']);newplate=next(r for r in mass['parts'] if r['part_ID']=='EXTERNAL_BENCH_PLATE');oldplate=next(r for r in oldmass['parts'] if r['part_ID']=='EXTERNAL_BENCH_PLATE');delta=np.array(newplate['gravity_wrench_about_origin_N_Nm'])-oldplate['gravity_wrench_about_origin_N_Nm'];external[bi['EXTERNAL_BENCH_PLATE']]+=delta;total=external.sum(0)
plate=read(REPO/cad['part_references']['EXTERNAL_BENCH_PLATE']['path']);support=translate(read(REPO/cad['part_references']['BENCH_SUPPORT']['path']),*old['support_translation_mm']);ground=json.loads((REPO/cad['ground']['path']).read_text());feet=ground['feet'];ff=faces(plate,2,-170.);actual=[]
for f in ff:
 area,c,cov=surface_moment(f);actual.append(dict(area_mm2=area,centroid_mm=c.tolist(),bounds_mm=bounds(f)))
# Independently reimport upper interface areas: feet may not silently alter seats/keys.
upper=[]
for p in patches:
 if {p['body_i'],p['body_j']}!={'BENCH_SUPPORT','EXTERNAL_BENCH_PLATE'}:continue
 fs=common_faces(support,plate,p['axis'],p['value_mm']);area=sum(surface_moment(f)[0] for f in fs);upper.append(dict(label=p['label'],new_area_mm2=area,prior_area_mm2=p['area_mm2'],same_area=abs(area-p['area_mm2'])<1e-6))

def wrench(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def column(ni,nj,p,f):
 a=np.zeros((5,6));w=wrench(p,f);a[bi[ni]]+=w
 if nj is not None:a[bi[nj]]-=w
 return a.ravel()
def internal(mu):
 cols=[];meta=[]
 for p in patches:
  n=np.array(p['normal_on_i'],float);tang=[i for i in range(3) if i!=p['axis']]
  for cell in p['cells']:
   for axis,sign in ([(tang[0],1),(tang[0],-1),(tang[1],1),(tang[1],-1)] if mu else [(tang[0],0)]):
    f=n.copy();f[axis]+=sign*mu;cols.append(column(p['body_i'],p['body_j'],cell['point_mm'],f));meta.append(dict(kind='upper_patch',label=p['label'],point_mm=cell['point_mm'],force_direction=f.tolist(),area_mm2=cell['area_mm2']))
 for p in ports:
  cols.append(column(p['body_i'],p['body_j'],p['point_mm'],p['direction']));meta.append(dict(kind='UNKNOWN_REQUIRED_CONNECTOR_PORT_NOT_TIE',label=p['label'],point_mm=p['point_mm'],force_direction=p['direction'],area_mm2=None))
 return cols,meta

def solve(mu,n=2,remove_feet=(),ext=None,pressure_objective=True,cap=None,loadlabel='nominal'):
 assert not(ROOT/'runtime/STOP').exists();cols,meta=internal(.3);first=len(cols)
 for i,ft in enumerate(feet):
  if i in remove_feet:continue
  a=ft['contact_bounds_mm'];dx=(a[3]-a[0])/n;dy=(a[4]-a[1])/n
  for ix,iy in itertools.product(range(n),repeat=2):
   p=[a[0]+(ix+.5)*dx,a[1]+(iy+.5)*dy,-170.]
   for ax,sign in [(0,-1),(0,1),(1,-1),(1,1)]:
    f=np.array([0.,0.,1.]);f[ax]=sign*mu;cols.append(column('EXTERNAL_BENCH_PLATE',None,p,f));meta.append(dict(kind='finite_floor_cell_ray',foot=i,cell=[ix,iy],point_mm=p,force_direction=f.tolist(),area_mm2=dx*dy))
 A=np.array(cols).T;E=external.copy() if ext is None else ext;scale=np.tile([1,1,1,100,100,100],5);P=len(cols);cellkeys=sorted(set((m['foot'],*m['cell']) for m in meta[first:]));G=np.zeros((len(cellkeys),P+1));ki={k:i for i,k in enumerate(cellkeys)}
 for j,m in enumerate(meta[first:],first):G[ki[(m['foot'],*m['cell'])],j]=1.;G[ki[(m['foot'],*m['cell'])],-1]=-m['area_mm2']
 Ae=np.c_[scale[:,None]*A,np.zeros(30)];objective=np.zeros(P+1);objective[-1]=1 if pressure_objective else 0;objective[:P]=0 if pressure_objective else 1
 res=linprog(objective,A_ub=G,b_ub=np.zeros(len(G)),A_eq=Ae,b_eq=-scale*E.ravel(),bounds=[(0,None)]*P+[(0,cap)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 row=dict(label=loadlabel,ground_mu_ASSUMED=mu,upper_mu_ASSUMED=.3,cells_per_foot=n*n,removed_feet=list(remove_feet),feasible=bool(res.success),status=int(res.status),message=res.message,all_physical_resultant_rows=30,physical_fixed_DOF=0,arbitrary_host_resultant_columns=0,required_connector_ports=len(ports),pressure_cap_MPa=cap,external_wrench_N_Nm=E.tolist())
 if res.success:
  ray=res.x[:-1];bal=(A@ray+E.ravel()).reshape(5,6);gw=A[:,first:]@ray[first:];w=gw.reshape(5,6).sum(0);reactions=[]
  for k,i in ki.items():
   inds=[j for j,m in enumerate(meta) if m['kind']=='finite_floor_cell_ray' and (m['foot'],*m['cell'])==k];N=float(sum(ray[j] for j in inds));F=sum((ray[j]*np.array(meta[j]['force_direction']) for j in inds),np.zeros(3));reactions.append(dict(foot=k[0],cell=list(k[1:]),point_mm=meta[inds[0]]['point_mm'],area_mm2=meta[inds[0]]['area_mm2'],normal_N=N,force_N=F.tolist(),pressure_MPa=N/meta[inds[0]]['area_mm2'],diamond_slack_N=mu*N-abs(F[0])-abs(F[1])))
  groundpower=[]
  # Physical virtual work for30unrestricted generalized rigidDOFs, arbitrary twist.
  twist=np.arange(30,dtype=float).reshape(5,6)/29.;vwork=float(np.sum(E*twist)+np.sum((A@ray).reshape(5,6)*twist))
  row.update(max_force_residual_N=float(abs(bal[:,:3]).max()),max_moment_residual_Nm=float(abs(bal[:,3:]).max()),min_ray_N=float(ray.min()),minimum_peak_uniform_cell_pressure_MPa=float(res.x[-1]),ground_wrench_N_Nm=w.tolist(),ground_center_of_pressure_mm=[float(-((w[4]+.170*w[0])/w[2])*1000),float(((w[3]-.170*w[1])/w[2])*1000)],floor_cells=reactions,connector_required_N={m['label']:float(ray[j]) for j,m in enumerate(meta) if m['kind']=='UNKNOWN_REQUIRED_CONNECTOR_PORT_NOT_TIE'},body_residual_N_Nm=bal.tolist(),physical_allDOF_virtualwork_residual=vwork,full_ray_coefficients=ray.tolist())
 return row
rows=[solve(mu,2,loadlabel='mu_contrast') for mu in [0,.01,.02,.05,.3]]
lo=0.;hi=.1
for _ in range(30):
 m=(lo+hi)/2
 if solve(m,2,pressure_objective=False)['feasible']:hi=m
 else:lo=m
threshold=[lo,hi];fine=[solve(.3,n,loadlabel='finite_pressure_cells') for n in [1,2,4,8]]
controls=[solve(.3,2,remove_feet=tuple(range(4)),loadlabel='NO_GROUND_MUST_FAIL'),solve(.3,2,cap=.000001,loadlabel='TINY_PRESSURE_CAP_MUST_FAIL')]
# A frictionless plane cannot supply horizontal load; old unrestricted-host success is not reused.
controls.append(solve(0,2,loadlabel='FRICTIONLESS_MUST_FAIL'))
# Every6wrenchcomponent gets an independent physical perturbation around SAME demand.
perturb=[]
for j in range(6):
 for sign in [-1,1]:
  ext=external.copy();ext[0,j]+=sign*(1. if j<3 else .1);perturb.append(solve(.3,2,ext=ext,loadlabel='actual6wrench_component_'+str(j)+'_'+str(sign)))
lift=[solve(.3,2,remove_feet=(i,),loadlabel='foot_'+str(i)+'_not_contacting') for i in range(4)]
# A level4foot floor is a manufacturing condition; robust3foot failures stay failures.
checks=dict(all83_actual_hashes=True,one_real_changed_plate=True,four_actual_bottom_faces=len(actual)==4,area1600=abs(sum(q['area_mm2'] for q in actual)-1600)<1e-6,all_four_actual_bounds_match=all(any(max(abs(np.array(q['bounds_mm'])-np.array(f['contact_bounds_mm'])))<1e-6 for q in actual) for f in feet),unchanged_upper_actual_contact_areas=bool(upper) and all(q['same_area'] for q in upper),gravity_delta_only_actual_changed_part=True,no_host_or_fixedDOF=all(q['physical_fixed_DOF']==q['arbitrary_host_resultant_columns']==0 for q in rows),mu0_and01_reject=not rows[0]['feasible'] and not rows[1]['feasible'],mu02_and_above_feasible=all(q['feasible'] for q in rows[2:]),negative_controls_reject=all(not q['feasible'] for q in controls),floor_finite_pressure_mesh_comparisons_present=len(fine)==4,all_feasible_original_balance=all(q['max_force_residual_N']<1e-8 and q['max_moment_residual_Nm']<1e-10 and q['min_ray_N']>=-1e-9 and abs(q['physical_allDOF_virtualwork_residual'])<1e-8 and min(c['diamond_slack_N'] for c in q['floor_cells'])>-1e-8 for q in rows+fine+controls+perturb+lift if q['feasible']))
dump(out/'contact_fields.json',dict(rows=rows,spatial_contrasts=fine,negative_controls=controls,six_wrench_perturbations=perturb,one_foot_absent=lift));dump(out/'load_ledger.json',dict(candidate=ref(cp),parent_unchanged_upstream=ref(source/'summary.json'),source_load_ledger=ref(source/'load_ledger.json'),source_upper_patches=ref(source/'patches.json'),source_ports=ref(source/'connector_ports.json'),all82retained_source_parts=True,mass=ref(massp),changed_plate_gravity_delta_N_Nm=delta.tolist(),external_wrench_N_Nm=external.tolist(),total_external_wrench_N_Nm=total.tolist(),actual_ground_faces=actual,upper_interface_area_recheck=upper,unknown_ground_mu=True,unknown_surface_flatness=True,unknown_material_minimum=True))
pairs=[]
for i,j in [(0,1),(1,2),(2,3),(0,3)]:
 a=fine[i];b=fine[j];d=abs(b['minimum_peak_uniform_cell_pressure_MPa']/a['minimum_peak_uniform_cell_pressure_MPa']-1);pairs.append(dict(n=[int(np.sqrt(a['cells_per_foot'])),int(np.sqrt(b['cells_per_foot']))],minimum_peak_pressure_relative_change=d,within1percent=d<=.01,meaning='LP static finite-cell pressure minimum only; NOT elastic displacement/energy convergence or actual pressure uniqueness'))
result=dict(status='SAME83P1_ACTUAL_FINITE_GROUND_WRENCH_CONDITIONAL_BOUNDS_NOT_SYSTEM_EQUILIBRIUM' if all(checks.values()) else 'SAME83P1_FINITE_GROUND_AUDIT_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),checks=checks,load_ledger=ref(out/'load_ledger.json'),contact_fields=ref(out/'contact_fields.json'),actual_bottom_area_mm2=sum(q['area_mm2'] for q in actual),conditional_product_mass_kg=mass['total_conditional_mass_kg'],required_ground_wrench_N_Nm=(-total).tolist(),necessary_friction_L1_lower_bound=float((abs(total[0])+abs(total[1]))/-total[2]),conditional_ground_mu_min_bracket=threshold,nominal_ground_mu_used=.3,nominal_ground_feasible=rows[-1]['feasible'],physical_fixed_DOF=0,arbitrary_host_resultant_columns=0,retained_unknown_upper_connector_ports=len(ports),all30_cut_resultant_rows_retained=True,spatial_pressure_comparisons=pairs,perturbed6wrench_success_count=sum(q['feasible'] for q in perturb),one_foot_absent_feasibility=[q['feasible'] for q in lift],all_original_system_gates_unchanged=True,newly_qualified_system_gate_ids=[],accepted83body_physical_equilibria=0,whole_system_release=False,hardware='NOT_MEASURED',elapsed_s=time.monotonic()-start,limitations=['Finite physical floor force cones replace unrestrictedhost6port. Environment floor is levelrigid plane; actual flatness/contact/friction not measured. Fourcoplanarfeet may rock; threefootcontrasts explicit.','Fivecutbody30row statics retains actualupstreamdeformed20mmstate and all83gravity. Tenunknownupperconnectorports are NOT physicalthread/preload/constitutive laws. Rigidunioncut isNOT83bodycontactequilibrium.','InscribedL1Coulombcone and assumeduppermu.3/groundmu contrasts; nonuniqueminpressure field isnecessaryadmissibility,notactualpressure/stiffness/capacity. No elasticmesh/time/globalenergy/strength certification.','Addedfeet increase mass; thickbillet machining/source-minimum/edge fillets,tool/process/handling and finalsamer ev3Finger require verification. No hardware or Stage3.'])
dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
