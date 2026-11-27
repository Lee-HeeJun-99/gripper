"""Fresh actual P1 conditional Finger/string source evaluations with explicit gamma.

No archived support pose/solution/load field transfer, no prescribed Base force.
No support equilibrium claim: evaluate reference Root/Motor and source gamma
probes, return gamma generalized force without silently eliminating it.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
from primary_prescribed_string28 import PrescribedYString
from primary_prescribed_finger28 import solve
from primary_finite_port import ObjectiveRootPort,motor_pullback


def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());oldpath=ROOT/'cad/exports/primaryP1_seated22/summary.json';old=json.loads(oldpath.read_text());changed=[n for n,r in cad['part_references'].items() if old['part_references'].get(n)!=r];assert set(changed)=={'OPEN_FRAME','F0_ROOT_BACK'}
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
 mass=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';points=json.loads(mass.read_text());seedpath=ROOT/'validation/finger/primaryP1_gravity_cat_demand32_2/cases.json';seed=json.loads(seedpath.read_text())[0]
 # Changed support body masses are excluded by source solver, not inherited.
 modelpath=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelpath.read_text())
 deps=['primary_prescribed_string28','primary_prescribed_finger28','primary_seated_string','primary_spatial_string','primary_support_feedback','primary_terminal_corner_v2','primary_finger_tangent_v5','primary_gravity_pullback','primary_gravity_swivel','primary_finite_port']
 dump(out/'inputs.json',dict(candidate=ref(cp),unchanged_upstream_geometry_reference=ref(oldpath),changed_support_only=changed,mass=ref(mass),seed=ref(seedpath),fivebody=ref(modelpath),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/f'scripts/{n}.py') for n in deps],
   parent_poses='Identity reference Root and Motor; no historical displacement/pressure/port load fields',conditional_boundary='Reference Root pose and Motor pose are evaluation coordinates, not enforced physical fixations. External gamma is sampled, not constrained or solved to zero.',physical_base_anchor='ABSENT; never cancel partial external wrench'))
 results=[];pullbacks={};curves={}
 for case,gamma,order in [('reference',0.,16),('plus',.00001,16),('minus',-.00001,16),('order32',0.,32)]:
  assert not(ROOT/'runtime/STOP').exists();E=np.array([seed['cable_end_m'][0],0,seed['cable_end_m'][1]]);c=PrescribedYString(points,np.eye(3),np.array([0,0,.020]),E,.01125,gamma,order);initial=c.solve(seed)
  parent=dict(root_R=np.eye(3).tolist(),root_translation_m=[0,0,0],motor_R=np.eye(3).tolist(),motor_C_m=[0,0,.020],actual_wire_center_radius_m=.01125,actual=initial)
  r=solve(parent,seed,points,gamma,order);curves[case]={k:r['string'].pop(k) for k in ('curve_m','wrap_curve_m','lead_curve_m','free_curve_m')};dump(out/f'{case}_source_state.json',r)
  RW=np.array(r['Root_origin_wrench_N_Nm']);MW=np.array(r['Motor_origin_wrench_N_Nm']);Q=r['upstream_gamma_generalized_force_N'];dy=np.array([0,gamma*.001,0]);W=RW.copy();W[3:]-=np.cross(dy,W[:3]);maps=[]
  for mr in model['results']:
   h=mr['mesh_level'];a=np.load(REPO/mr['reference_model']['path']);p=a['F0_ROOT_BACK_points_mm'];w=a['Root_port_weights_mm2'];ids=np.flatnonzero(w);port=ObjectiveRootPort(p[ids],w[ids]);ff=port.pullback(np.zeros((len(ids),3)),W);mapped=np.r_[ff.sum(0),np.cross(p[ids]*.001,ff).sum(0)];f=np.zeros(len(a['reference_coordinates_mm']));off=int(a['F0_ROOT_BACK_offset']);f[off+3*ids[:,None]+np.arange(3)]=ff;mo=int(a['motor_offset']);f[mo:mo+6]=motor_pullback(np.zeros(6),MW);f[int(a['upstream_freeY_offset'])]=Q
   pullbacks[f'{case}_h{h}_source_generalized_N']=f
   maps.append(dict(mesh_level=h,root_port_nodes=len(ids),root_force_error_N=float(np.linalg.norm(mapped[:3]-W[:3])),root_moment_error_Nm=float(np.linalg.norm(mapped[3:]-W[3:])),upstream_gamma_force_stored_N=float(f[int(a['upstream_freeY_offset'])]),no_Base_counterload=True))
  results.append(dict(case=case,upstream_gamma_mm=gamma,quadrature_order=order,status=r['status'],checks=r['checks'],normal_N=r['normal_N'],T_N=r['T_N'],force_equivalent_N=r['force_equivalent_N'],Root_wrench_N_Nm=RW.tolist(),Motor_wrench_N_Nm=MW.tolist(),
   gamma_generalized_force_N=Q,source_pair_wrench_error_N_Nm=r['pair_wrench_error'],gamma_is_not_eliminated=True,full_system_equilibrium=False,maps=maps,state=ref(out/f'{case}_source_state.json')))
 np.savez_compressed(out/'fresh_source_pullbacks.npz',**pullbacks);dump(out/'curves.json',curves)
 derivative=(results[1]['gamma_generalized_force_N']-results[2]['gamma_generalized_force_N'])/.00002
 # Oddness is an independent symmetry control for identical zero-Y reference geometry.
 odderr=abs(results[1]['gamma_generalized_force_N']+results[2]['gamma_generalized_force_N']);qerr=abs(results[0]['normal_N']-results[3]['normal_N'])
 checks=dict(all_conditional_source_stationarity=all(all(r['checks'].values()) for r in results),all_fresh_port_resultants=all(m['root_force_error_N']<1e-8 and m['root_moment_error_Nm']<1e-10 for r in results for m in r['maps']),
  gamma_not_eliminated=abs(results[1]['gamma_generalized_force_N'])>1e-12 and abs(results[2]['gamma_generalized_force_N'])>1e-12,source_symmetry=odderr<1e-8,quadrature_force=qerr<1e-8,no_Base_counterload=all(m['no_Base_counterload'] for r in results for m in r['maps']))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FRESH_CONDITIONAL_COUPLED_SOURCE_BLOCK_VERIFIED_NOT_SUPPORT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_FRESH_CONDITIONAL_COUPLED_SOURCE_BLOCK_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,results=results,source_pullbacks=ref(out/'fresh_source_pullbacks.npz'),gamma_force_derivative_N_per_mm=derivative,odd_symmetry_error_N=odderr,order16_32_normal_force_difference_N=qerr,elapsed_s=time.monotonic()-start,
  newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,limitations=['Source solver remains conditional planar rail/PET and rigid ideal cuts/world-X stop; full3DFinger/finitewire/protector/materialminimum/mesh1%/time.1% not certified.',
  'Explicit upstream gamma retained and conjugate force returned; physical compatibility of this coordinate with deforming Root port remains to be reviewed before coupled support solve. No artificial gamma spring or fixation.',
  'Fresh states at reference support coordinates, not full same-revision load equilibrium. Remaining hardware gravity and physical Base anchor still required; no inherited old sourcefield, pressure or Base cancellation.',
  'Conditional historical upstream mass distribution reused only after exact CAD identity of all upstream parts; changed Root and Frame excluded from upstream masses and represented by new fivebody block.']))
 print(json.dumps(dict(checks=checks,gamma_force_derivative_N_per_mm=derivative,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
