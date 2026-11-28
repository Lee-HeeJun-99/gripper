"""Actual five cut-body finite-face necessary statics with EXPLICIT connector ports.
This uses the existing finite patch LP. Ports are required loads, not bolt laws.
No body is fixed and a free host must fail. No elastic uniqueness is asserted.
"""
import sys,json,shutil,time
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,box,bounds
from primary_anchor_contact38 import common_faces,surface_moment
from primary_motor_bearing_wrenches import faces
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
start=time.monotonic();src=ROOT/'validation/integrated'/sys.argv[1];out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sd=json.loads((src/'summary.json').read_text());assert all(sd['checks'].values());r=json.loads((src/'state.json').read_text());cp=REPO/sd['candidate']['path'];cad=json.loads(cp.read_text());refs=cad['part_references'];assert sha(cp)==sd['candidate']['SHA256'];assert all(sha(REPO/q['path'])==q['SHA256'] for q in [*refs.values(),cad['assembly'],cad['BOM']]);dy=sd['root_translation_mm'][1];my=sd.get('motor_translation_mm',[0,0,0])[1];dx=sd.get('support_translation_mm',[0,0,0])[0]
names=['F0_ROOT_BACK','F0_MICRO_MOTOR','MOTOR_CAP','BENCH_SUPPORT','EXTERNAL_BENCH_PLATE'];parts={n:read(REPO/refs[n]['path']) for n in names};parts={n:translate(s,dx if n!='EXTERNAL_BENCH_PLATE' else 0,dy if n=='F0_ROOT_BACK' else my if n=='F0_MICRO_MOTOR' else 0,0) for n,s in parts.items()};patches=[]
def patch(ni,nj,axis,value,direction,label):
 for face in common_faces(parts[ni],parts[nj],axis,value):
  area,center,cov=surface_moment(face);bb=np.array(bounds(face));other=[j for j in range(3) if j!=axis];grid=[np.linspace(bb[j],bb[j+3],5) for j in other];cells=[]
  for a,b in zip(grid[0][:-1],grid[0][1:]):
   for c,d in zip(grid[1][:-1],grid[1][1:]):
    assert not(ROOT/'runtime/STOP').exists();lo=bb[:3].copy();size=bb[3:]-lo;lo[axis]-=.01;size[axis]=.02;lo[other]=[a,c];size[other]=[b-a,d-c];cell=BRepAlgoAPI_Common(face,box(*map(float,lo),*map(float,size))).Shape();ar,q,cv=surface_moment(cell)
    if ar>1e-8:cells.append(dict(point_mm=q.tolist(),area_mm2=ar))
  patches.append(dict(label=label,body_i=ni,body_j=nj,axis=axis,value_mm=value,normal_on_i=direction,area_mm2=area,centroid_mm=center.tolist(),cells=cells,area_sum_error_mm2=sum(c['area_mm2'] for c in cells)-area))
patch(names[0],names[3],2,-7,[0,0,1],'root_seat');patch(names[0],names[3],0,68+dx,[-1,0,0],'root_wall')
patch(names[1],names[3],1,-9.5,[0,-1,0],'motor_axial_shoulder');patch(names[1],names[3],2,14,[0,0,1],'motor_bottom');patch(names[1],names[3],0,-5+dx,[1,0,0],'motor_left');patch(names[1],names[3],0,5+dx,[-1,0,0],'motor_right');patch(names[1],names[2],2,26,[0,0,-1],'motor_top');patch(names[3],names[4],2,-130,[0,0,1],'support_plate')
for value in [-18.9,71.1]:patch(names[3],names[4],0,value,[-1,0,0],'actual_key_xwall_'+str(value))
# Required axial resultants at ACTUAL bolt head/nut seat centers. Their detailed
# thread, bending, preload and motions remain unresolved, never tied by this LP.
ports=[]
for i,y in enumerate([-16,16]):ports.append(dict(label='root_connector_'+str(i),body_i=names[0],body_j=names[3],point_mm=[64+dx,y,-3],direction=[0,0,-1],part_IDs=[f'F0_RF{i}_BOLT',f'F0_RF{i}_NUT']))
for x in [-7,7]:
 for y in [-29.5,-13.5]:ports.append(dict(label=f'cap_connector_{x}_{y}',body_i=names[2],body_j=names[3],point_mm=[x+dx,y,29],direction=[0,0,-1],part_IDs=[f'MOTOR_CAP_BOLT_{x}_{y}',f'MOTOR_CAP_NUT_{x}_{y}']))
for i,(x,y) in enumerate([(-65,-35),(107,-35),(-65,15),(107,15)]):ports.append(dict(label='through_connector_'+str(i),body_i=names[3],body_j=names[4],point_mm=[x,y,-124],direction=[0,0,-1],part_IDs=[f'BENCH_THROUGH_BOLT_{i}',f'BENCH_THROUGH_NUT_{i}']))
# Prove each port axis passes its real head and nut seat (area, not envelope).
port_seats=[]
for port in ports:
 label=port['label'];a,b=port['part_IDs'];ni,nj=port['body_i'],port['body_j'];za,zb=(-3,-12) if label.startswith('root') else (29,11) if label.startswith('cap') else (-124,-138)
 for part,body,z in [(a,ni,za),(b,nj,zb)]:
  ff=common_faces(translate(read(REPO/refs[part]['path']),0 if part.startswith('BENCH_THROUGH_') else dx,0,0),parts[body],2,z);area=sum(surface_moment(f)[0] for f in ff);port_seats.append(dict(port=label,part_ID=part,cut_body=body,z_mm=z,area_mm2=area))
# Use the exact freshly solved deformed upstream gravity/wrenches, then account
# for EVERY remaining77part mass once; hardware gravity is a cut load,not a tie.
mp=ROOT/'validation/integrated/primaryP1_mass59c/summary.json';mass=json.loads(mp.read_text());bi={n:i for i,n in enumerate(names)};external=np.zeros((5,6));external[0]=r['Root_origin_wrench_N_Nm'];external[1]=r['Motor_origin_wrench_N_Nm'];accounted={q['part_ID'] for q in r['moving_mass_points']+r['fixed_mass_points']}|{q['part_ID'] for q in r['string']['rotors']}|{'F0_MICRO_MOTOR','F0_TENDON_WIRE'};extra=[]
def wrench(p,f):return np.r_[f,np.cross(np.asarray(p)*.001,f)]
for q in mass['parts']:
 n=q['part_ID']
 if n in accounted:continue
 i=bi.get(n,3);w=np.array(q['gravity_wrench_about_origin_N_Nm']);shift=np.array([0 if n.startswith('BENCH_THROUGH_') or n=='EXTERNAL_BENCH_PLATE' else dx,dy if n=='F0_ROOT_BACK' else 0,0])*.001;w[3:]+=np.cross(shift,w[:3]);external[i]+=w;extra.append(dict(part_ID=n,assigned_cut_body=names[i],gravity_wrench_N_Nm=w.tolist(),conditional_mass_kg=q['conditional_mass_kg'],posed_centroid_m=(np.array(q['CAD_centroid_mm'])*.001+shift).tolist()))
assert accounted|{q['part_ID'] for q in extra}==set(refs)
def column(ni,nj,p,f):
 a=np.zeros((5,6));w=wrench(p,f);a[bi[ni]]+=w;a[bi[nj]]-=w;return a.ravel()
def assemble(mu):
 cols=[];meta=[]
 for j,patch in enumerate(patches):
  n=np.array(patch['normal_on_i'],float);ax=patch['axis'];tang=[k for k in range(3) if k!=ax]
  for k,cell in enumerate(patch['cells']):
   for axis,sign in [(tang[0],1),(tang[0],-1),(tang[1],1),(tang[1],-1)] if mu else [(tang[0],0)]:
    f=n.copy();f[axis]+=sign*mu;cols.append(column(patch['body_i'],patch['body_j'],cell['point_mm'],f));meta.append(dict(kind='finite_patch_inscribed_Coulomb_ray',label=patch['label'],patch=j,cell=k,body_i=patch['body_i'],body_j=patch['body_j'],point_mm=cell['point_mm'],direction=f.tolist(),area_mm2=cell['area_mm2']))
 for port in ports:cols.append(column(port['body_i'],port['body_j'],port['point_mm'],port['direction']));meta.append(dict(port,kind='EXPLICIT_REQUIRED_AXIAL_CONNECTOR_PORT_NOT_BOLT_LAW',area_mm2=None))
 return np.array(cols).T,meta
def run(mu,host=False,omit=None):
 A,meta=assemble(mu);ix=[j for j,m in enumerate(meta) if omit is None or not m['label'].startswith(omit)];A=A[:,ix];meta=[meta[j] for j in ix];nr=A.shape[1];bounds0=[(0,None)]*nr;c=np.array([1 if m['kind'].startswith('EXPLICIT') else 1e-5 for m in meta]);hostcols=np.zeros((30,6));hostcols[-6:]=np.eye(6)
 if host:A=np.c_[A,hostcols];bounds0 += [(None,None)]*6;c=np.r_[c,np.zeros(6)]
 scale=np.tile([1,1,1,100,100,100],5);res=linprog(c,A_eq=scale[:,None]*A,b_eq=-scale*external.ravel(),bounds=bounds0,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 row=dict(mu_ASSUMED=mu,explicit_unknown_host_resultant_port=host,omitted=omit,feasible=bool(res.success),solver_status=int(res.status),message=res.message,all_cut_DOF_equilibrium_rows=30,physical_fixed_DOF=0,connector_law_solved=False)
 if res.success:
  bal=(A@res.x+external.ravel()).reshape(5,6);ray=res.x[:nr];row.update(required_host_wrench_N_Nm=res.x[nr:].tolist() if host else None,max_force_residual_N=float(np.linalg.norm(bal[:,:3],axis=1).max()),max_moment_residual_Nm=float(np.linalg.norm(bal[:,3:],axis=1).max()),minimum_ray_N=float(ray.min()),reactions=[dict(m,coefficient_N=float(x),uniform_normal_pressure_MPa=None if m['area_mm2'] is None else float(x/m['area_mm2'])) for m,x in zip(meta,ray) if x>1e-12],body_internal_wrench_N_Nm=(A[:,:nr]@ray).reshape(5,6).tolist(),balance_N_Nm=bal.tolist(),objective=float(res.fun))
 return row
rows=[run(mu,host) for mu in [0,.1,.3,.8] for host in [False,True]];controls=[run(.3,True,p) for p in ['root_connector','cap_connector','through_connector','motor_left','root_wall']]
total=external.sum(0);twist=np.tile([0,0,-1,0,0,0],5);A,_=assemble(.3);certificate=dict(all5body_translation_twist=twist.tolist(),maximum_internal_virtualwork=float(abs(A.T@twist).max()),external_downward_translation_work_N=float(external.ravel()@twist),meaning='All internal contacts and connector ports dozero work under commontranslation; positivegravity work proves floating77partassembly cannot staticallyequilibrate. No hiddenhostfixation.')
checks=dict(candidate77_hashes=True,fresh_upstream_admitted=all(sd['checks'].values()),all_actual_patch_areas_positive=all(p['area_mm2']>0 for p in patches),all20actual_port_seats_nonzero=len(port_seats)==20 and all(p['area_mm2']>0 for p in port_seats),exact_cell_area_sums=all(abs(p['area_sum_error_mm2'])<1e-6 for p in patches),all77_gravity_once=True,free_host_all_reject=all(not q['feasible'] for q in rows if not q['explicit_unknown_host_resultant_port']),free_host_work_certificate=certificate['maximum_internal_virtualwork']<1e-12 and certificate['external_downward_translation_work_N']>0,feasible_rows_original_balance=all(q['max_force_residual_N']<1e-8 and q['max_moment_residual_Nm']<1e-10 and q['minimum_ray_N']>=-1e-10 for q in rows+controls if q['feasible']))
dump(out/'patches.json',patches);dump(out/'connector_ports.json',dict(ports=ports,actual_seats=port_seats,scope='RequiredaxialcutportsONLY;notphysicalthread/preload/stiffness/bending/contactsolution'));dump(out/'load_ledger.json',dict(body_names=names,external_wrench_N_Nm=external.tolist(),total_external_wrench_N_Nm=total.tolist(),upstream=ref(src/'state.json'),rest_mass_source=ref(mp),upstream_accounted_part_IDs=sorted(accounted),remaining_gravity=extra,full77part_count=len(refs),conditional_source_mass=True));dump(out/'rows.json',rows);dump(out/'controls.json',controls)
dump(out/'summary.json',dict(status='ACTUAL77_FRESH_CUT_FINITE_CONTACT_AND_REQUIRED_CONNECTOR_HOST_PORT_BOUNDS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL77_FRESH_CUT_CONTACT_PORT_AUDIT_FAIL',candidate=ref(cp),source=ref(src/'summary.json'),producer=ref(out/'producer.py'),patches=ref(out/'patches.json'),connector_ports=ref(out/'connector_ports.json'),load_ledger=ref(out/'load_ledger.json'),rows=ref(out/'rows.json'),negative_controls=ref(out/'controls.json'),checks={k:bool(v) for k,v in checks.items()},patch_count=len(patches),actual_finite_contact_cells=sum(len(p['cells']) for p in patches),root_translation_mm=[dx,dy,0],motor_translation_mm=[dx,my,0],support_translation_mm=[dx,0,0],free_host_certificate=certificate,free_host_solved_equilibria=0,conditional_host_port_feasible_mu=[q['mu_ASSUMED'] for q in rows if q['explicit_unknown_host_resultant_port'] and q['feasible']],required_total_host_wrench_N_Nm=(-total).tolist(),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start,limitations=['Fivecutbody equilibrium retains30resultants,not full77independentrigidbody or elasticcontact solve. Connectorports are explicitUNKNOWN constitutivelaws,not ties/capacity/preload.','Conditional mu usesinscribeddiamond,notmeasuredfriction. Nonuniquepatchreactions areadmissiblenecessarybounds,not actualpressuredistribution.','Unknown ultimatehost6resultantport doesnotinstantiate hostgeometry/contact/fixation. All freehostcasesmustreject.','Sourceconditionalmass/density and oldmesh/time/globalenergyFAILs,3Finger/protection/materialminima/process/all22remain.']));print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
