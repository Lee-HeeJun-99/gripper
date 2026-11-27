"""Same77part: finite true lower-key takeup geometry and fresh frictionless cut LP.
No thread/friction/elasticcapacity certificate; host remains an explicit unknown port.
"""
import sys,json,shutil,time,os
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,bounds,overlap,common
from primary_anchor_contact38 import common_faces,surface_moment
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_keyports58/summary.json';d=json.loads(sp.read_text());assert all(d['checks'].values());cp=REPO/d['candidate']['path'];cad=json.loads(cp.read_text());refs=cad['part_references'];support=read(REPO/refs['BENCH_SUPPORT']['path']);others={n:read(REPO/r['path']) for n,r in refs.items() if n=='EXTERNAL_BENCH_PLATE' or n.startswith('BENCH_THROUGH_')};journal=[];areas=[]
for x in [0,.025,.05,.075,.1]:
 posed=translate(support,x,0,0)
 for n,s in others.items():
  assert not(ROOT/'runtime/STOP').exists();v=common(posed,s) if overlap(bounds(posed),bounds(s)) else 0.;row=dict(dx_mm=x,other=n,intersection_mm3=v);journal.append(row)
  with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
 for value in [-18.9,71.1]:areas.append(dict(dx_mm=x,wall_x_mm=value,area_mm2=sum(surface_moment(f)[0] for f in common_faces(posed,others['EXTERNAL_BENCH_PLATE'],0,value)),declared_source_gap_mm=.1-x))
L=json.loads((REPO/d['load_ledger']['path']).read_text());names=L['body_names'];external=np.array(L['external_wrench_N_Nm']).ravel();patches=json.loads((REPO/d['patches']['path']).read_text());ports=json.loads((REPO/d['connector_ports']['path']).read_text())['ports'];meta=[];columns=[]
def col(ni,nj,p,f):
 p=np.array(p)*.001;f=np.array(f);w=np.r_[f,np.cross(p,f)];a=np.zeros((5,6));a[names.index(ni)]+=w;a[names.index(nj)]-=w;return a.ravel()
for patch in patches:
 for cell in patch['cells']:columns.append(col(patch['body_i'],patch['body_j'],cell['point_mm'],patch['normal_on_i']));meta.append(dict(label=patch['label'],kind='actual_finite_normal_cell'))
for port in ports:columns.append(col(port['body_i'],port['body_j'],port['point_mm'],port['direction']));meta.append(dict(label=port['label'],kind='explicit_required_connector_port'))
A=np.array(columns).T;H=np.zeros((30,6));H[-6:]=np.eye(6);scale=np.tile([1,1,1,100,100,100],5);cases=[]
for omit in [None,'actual_key','root_connector','cap_connector','through_connector','root_wall','motor_left']:
 ix=[i for i,m in enumerate(meta) if omit is None or not m['label'].startswith(omit)];B=np.c_[A[:,ix],H];r=linprog(np.r_[np.ones(len(ix)),np.zeros(6)],A_eq=scale[:,None]*B,b_eq=-scale*external,bounds=[(0,None)]*len(ix)+[(None,None)]*6,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});row=dict(mu=0,omit=omit,feasible=bool(r.success),message=r.message)
 if r.success:
  res=(B@r.x+external).reshape(5,6);row.update(force_residual_N=float(np.linalg.norm(res[:,:3],axis=1).max()),moment_residual_Nm=float(np.linalg.norm(res[:,3:],axis=1).max()),required_unknown_host_N_Nm=r.x[-6:].tolist(),normal_and_required_port_N=[dict(meta[j],reaction_N=float(q)) for j,q in zip(ix,r.x[:-6]) if q>1e-12])
 cases.append(row)
# Relative horizontalvirtual work rejects the original untaken-up key state.
source0=ROOT/'validation/integrated/primaryP1_shoulderports58_y05';P0=json.loads((source0/'patches.json').read_text());v=np.tile([1.,0,0,0,0,0],5);v[-6:]=0;cols0=[col(p['body_i'],p['body_j'],q['point_mm'],p['normal_on_i']) for p in P0 for q in p['cells']]+[col(p['body_i'],p['body_j'],p['point_mm'],p['direction']) for p in ports];A0=np.array(cols0).T;L0=json.loads((source0/'load_ledger.json').read_text());work0=float(np.array(L0['external_wrench_N_Nm']).ravel()@v);certificate=dict(relative_support_plate_X_translation_twist=v.tolist(),nominal_contact_and_port_zero_work=float(abs(A0.T@v).max()),nominal_external_positive_work_N=work0,keyengaged_contact_work_range=(A.T@v).tolist(),meaning='Originalgap hasno frictionlessshearpath;actualfinite128mm2keywall supplies negativework at+.1mmtakeup. No fictitiousshear tie.')
checks=dict(actual77unchanged=len(refs)==77 and all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values()),all85finite_pose_pairchecks_clear=len(journal)==85 and all(abs(q['intersection_mm3'])<1e-8 for q in journal),no_keywall_contact_before_takeup=all(q['area_mm2']<1e-8 for q in areas if q['dx_mm']<.1),both64mm2keywalls_at_takeup=all(abs(q['area_mm2']-64)<1e-7 for q in areas if q['dx_mm']==.1),fresh_frictionless_required_port_equilibrium=cases[0]['feasible'],removing_keypath_rejected=not cases[1]['feasible'],removing_rootconnector_rejected=not cases[2]['feasible'],removing_capconnector_rejected=not cases[3]['feasible'],original_gap_free_mode_certificate=certificate['nominal_contact_and_port_zero_work']<1e-10 and work0>1.,key_can_oppose_slip=min(certificate['keyengaged_contact_work_range'])<-.99,all_admitted_balances=all(q['force_residual_N']<1e-8 and q['moment_residual_Nm']<1e-10 for q in cases if q['feasible']))
dump(out/'takeup_areas.json',areas);dump(out/'frictionless_cases.json',cases);dump(out/'summary.json',dict(status='ACTUAL77_FINITE_KEY_TAKEUP_FRICTIONLESS_REQUIRED_PORT_PATH_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL77_KEY_TAKEUP_PATH_REJECTED',candidate=ref(cp),source=ref(sp),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},finite_pair_queries=len(journal),journal=ref(out/'journal.jsonl'),actual_keywall_areas=ref(out/'takeup_areas.json'),fresh_frictionless_cases=ref(out/'frictionless_cases.json'),original_gap_virtualwork_certificate=certificate,physical_fixed_DOF=0,actual_cut_DOF_equilibrium_rows=30,required_unknown_host_wrench_N_Nm=cases[0].get('required_unknown_host_N_Nm'),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['85finiteposesplusactualplanar-keyareas areNOTcontinuousCCD/fullassembly/processcertificate','Requiredaxialconnectorandhostports remainUNKNOWNmechanisms; noelasticcapacity/preload/locking/source-minimum oractualwholeproductequilibrium','MovingupstreamfreshfiniteFinger/string retained;Beam/PETmesh/supportmesh1percent/time.1percent/globalenergy/3Finger/protectionremain']))
print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
