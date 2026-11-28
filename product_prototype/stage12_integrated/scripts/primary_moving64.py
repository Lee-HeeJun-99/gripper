"""Fresh finite Root translation and actual carried-object upstream solves.
No pose is a solved support equilibrium; all six cut resultants remain explicit.
"""
import sys,json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from primary_detached_finger56 import solve
from primary_local_gamma29 import LocalGammaString
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common,bounds,overlap
start=time.monotonic();tag=sys.argv[1];dy=float(sys.argv[2]);my=float(sys.argv[3]);dx=float(sys.argv[4]);out=ROOT/'validation/integrated'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
cp=ROOT/'cad/exports/primaryP1_round64c/summary.json';cad=json.loads(cp.read_text());assert len(cad['part_references'])==83 and all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']])
base=json.loads((ROOT/'validation/integrated/primaryP1_operating56/inputs.json').read_text());points=json.loads((REPO/base['mass_points']['path']).read_text());seed=json.loads((REPO/base['seed']['path']).read_text())[0];oldp=ROOT/'validation/integrated/primaryP1_detached56/state.json';last=json.loads(oldp.read_text());seed=dict(seed,state=last['state'],swivel_beta_rad=last['swivel_beta_rad'],interface_tip_force_N=last['interface_tip_force_N'],normal_N=last['normal_N'],corner_contact_force_local_N=last['corner_force_N'],corner_material_station_m=last['corner_material_station_m'],T_N=last['T_N'],cable_end_m=[last['string']['E_m'][0],last['string']['E_m'][2]])
tr=np.array([dx*.001,dy*.001,0]);E=np.array(last['string']['E_m'])+tr
initial=LocalGammaString(points,np.eye(3),np.array([dx*.001,my*.001,.020]),E,.01125,0.,16,axis=np.array([0,1,0])).solve(seed)
parent=dict(root_R=np.eye(3).tolist(),root_translation_m=tr.tolist(),motor_R=np.eye(3).tolist(),motor_C_m=[dx*.001,my*.001,.020],actual_wire_center_radius_m=.01125,actual=initial)
dump(out/'inputs.json',dict(candidate=ref(cp),accepted_conditional_seed=ref(oldp),upstream_admission=ref(ROOT/'validation/integrated/primaryP1_detached_audit56/summary.json'),mass_points=base['mass_points'],parent_pose=parent,root_translation_mm=[dx,dy,0],motor_translation_mm=[dx,my,0],normal_N=.980665/(3*.3),object_down_N=.980665/3,mu_ASSUMED=.3,producer=ref(out/'producer.py'),pose_scope='Finite evaluation cut,not imposed support/fixed DOF or equilibrium. Downstream all6DOF reaction compatibility mandatory.',criteria=dict(force_N=1e-8,gap_m=1e-9,moment_Nm=1e-10,mesh_fraction=.01,time_fraction=.001)))
r=solve(parent,seed,points,0.,16,target_normal=.980665/(3*.3),object_down_N=.980665/3,lower_station_m=last['lower_corner_material_station_m']);curves={k:r['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')};dump(out/'curves.json',curves);dump(out/'state.json',r)
# The exact moved cartridge/frame solid common is checked, not an assumed clearance.
support=translate(read(REPO/cad['part_references']['BENCH_SUPPORT']['path']),dx,0,0);pairs=[]
for n in ['F0_ROOT_BACK','F0_ROOT_FRONT','F0_MICRO_MOTOR','MOTOR_CAP']:
 s=read(REPO/cad['part_references'][n]['path']);shift=[dx,dy,0] if n.startswith('F0_ROOT_') else [dx,my,0] if n=='F0_MICRO_MOTOR' else [dx,0,0];s=translate(s,*shift);v=common(s,support) if overlap(bounds(s),bounds(support)) else 0.;pairs.append(dict(part_ID=n,translation_mm=shift,intersection_mm3=v))
plate=read(REPO/cad['part_references']['EXTERNAL_BENCH_PLATE']['path']);pairs.append(dict(part_ID='BENCH_SUPPORT_vs_PLATE',translation_mm=[dx,0,0],intersection_mm3=common(support,plate)))
for n,q in cad['part_references'].items():
 if n.startswith('BENCH_THROUGH_'):
  shape=read(REPO/q['path']);pairs.append(dict(part_ID='BENCH_SUPPORT_vs_'+n,translation_mm=[dx,0,0],intersection_mm3=common(support,shape) if overlap(bounds(support),bounds(shape)) else 0.))
checks=dict(upstream_original_checks=all(r['checks'].values()),actual_moved_cut_solids_clear=all(abs(p['intersection_mm3'])<1e-8 for p in pairs),paired_wrench=r['pair_wrench_error']<1e-12)
dump(out/'summary.json',dict(status='ACTUAL83_FRESH_MOVING_CUT_CONDITIONAL_UPSTREAM_ADMITTED_NOT_SUPPORT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL83_FRESH_MOVING_CUT_REJECTED',candidate=ref(cp),inputs=ref(out/'inputs.json'),state=ref(out/'state.json'),producer=ref(out/'producer.py'),root_translation_mm=[dx,dy,0],motor_translation_mm=[dx,my,0],support_translation_mm=[dx,0,0],checks=checks,upstream_checks=r['checks'],moved_CAD_pairs=pairs,T_N=r['T_N'],Root_origin_wrench_N_Nm=r['Root_origin_wrench_N_Nm'],Motor_origin_wrench_N_Nm=r['Motor_origin_wrench_N_Nm'],force_equivalent_N=r['force_equivalent_N'],minimum_dense_gap_m=r['minimum_dense_gap_m'],support_equilibrium_solved=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-start));print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
