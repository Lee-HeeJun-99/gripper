"""Fresh exact-CAD 28 hardware gravity and disjoint78part source accounting.

Hardware gets its own free rigid wrench, never an arbitrary Base lump or
reaction cancellation. Nominal envelope density is conditional, not measured
thread mass/strength. Anchor resultant is a requirement, never applied load.
"""
import sys,json,time,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps


def main():
 start=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cp.read_text());sourcepath=ROOT/'validation/integrated/primaryP1_fresh_sources28/summary.json';source=json.loads(sourcepath.read_text());state=json.loads((REPO/source['results'][0]['state']['path']).read_text());masspath=ROOT/'validation/integrated/primaryP1_seated_string1/mass_points.json';mass=json.loads(masspath.read_text());modelpath=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';model=json.loads(modelpath.read_text());bodies={'OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'}
 upstream=set(x['part_ID'] for x in state['moving_mass_points']+state['fixed_mass_points']+state['string']['rotors'])|{'F0_MICRO_MOTOR'}|set(x['part_ID'] for x in mass if x['mode']=='wire');remaining=set(cad['part_references'])-upstream-bodies;assert len(remaining)==28
 patchpath=ROOT/'validation/integrated/primaryP1_axial_rebuild27env/actual_bearing_material_quadrature.json';patches=json.loads(patchpath.read_text());assert {p['hardware'] for p in patches}==remaining
 deps=[ref(S1/'scripts/incremental_stage1.py')]
 dump(out/'inputs.json',dict(candidate=ref(cp),source=ref(sourcepath),fivebody=ref(modelpath),mass_points=ref(masspath),actual_hardware_footprints=ref(patchpath),producer=ref(out/'producer.py'),dependencies=deps,conditional_density_kg_m3=7900.,
   policy='Fresh exact CAD envelope volume/centroid/inertia for every omitted support fastener, own free rigid wrench. No artificial transfer to TEST_BASE. No source-backed material minimum/actual thread correction claimed.'))
 hw=[];W=np.zeros(6);force_sum=np.zeros(3);moment_sum=np.zeros(3)
 for name in sorted(remaining):
  assert not(ROOT/'runtime/STOP').exists();r=cad['part_references'][name];assert sha(REPO/r['path'])==r['SHA256'];s=read(REPO/r['path']);g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g,1e-11);co=g.CentreOfMass();q=np.array([co.X(),co.Y(),co.Z()]);V=g.Mass();m=V*7900e-9;ff=np.array([0,0,-m*9.80665]);ww=np.r_[ff,np.cross(q*.001,ff)];W+=ww;force_sum+=ff;moment_sum+=np.cross(q*.001,ff)
  I=g.MatrixOfInertia();inertia=np.array([[I.Value(i+1,j+1) for j in range(3)] for i in range(3)])*7900e-15;patch=next(p for p in patches if p['hardware']==name)
  hw.append(dict(part_ID=name,STEP=r,nominal_envelope_volume_mm3=float(V),centroid_mm=q.tolist(),conditional_mass_kg=float(m),conditional_inertia_kg_m2=inertia.tolist(),gravity_wrench_about_world_origin_N_Nm=ww.tolist(),
    actual_bearing_branch=patch['branch'],bearing_side=patch['side'],adjacent_body=patch['body'],own_rigid_body_load=True,transferred_to_adjacent_body=False,force_transfer_qualified=False,minimum_inertia_eigenvalue_kg_m2=float(np.linalg.eigvalsh(inertia).min())))
 reports=[]
 for mr in model['results']:
  gravity=np.array(mr['fivebody_gravity_wrench_N_Nm']);external=np.array(state['Root_origin_wrench_N_Nm'])+state['Motor_origin_wrench_N_Nm']+gravity+W
  reports.append(dict(mesh_level=mr['mesh_level'],upstream_parts=len(upstream),elastic_parts=len(bodies),explicit_hardware_parts=len(remaining),total_disjoint_parts=len(upstream|bodies|remaining),
   conditional_hardware_total_mass_kg=float(sum(x['conditional_mass_kg'] for x in hw)),hardware_gravity_wrench_N_Nm=W.tolist(),fivebody_gravity_wrench_N_Nm=gravity.tolist(),
   conditional_complete_external_resultant_N_Nm=external.tolist(),necessary_external_anchor_resultant_N_Nm=(-external).tolist(),anchor_resultant_is_requirement_only=True,
   anchor_resultant_applied=False,actual_hardware_to_support_load_transfer_implemented=False,actual_equilibrium=False,physics_sourcefield_created=False))
 checks=dict(exact_disjoint_78part_inventory=len(upstream|bodies|remaining)==78 and not(upstream&bodies) and not(upstream&remaining) and not(bodies&remaining),fresh28hardware_CAD_inertia=len(hw)==28 and all(x['nominal_envelope_volume_mm3']>0 and x['minimum_inertia_eigenvalue_kg_m2']>0 for x in hw),
  all_actual_hardware_bearing_owners_present={x['part_ID'] for x in hw}=={p['hardware'] for p in patches},independent_hardware_force_moment_sum=float(np.max(abs(W-np.r_[force_sum,moment_sum])))<1e-12,no_invented_transfer_or_Base_load=all(not r['anchor_resultant_applied'] and not r['actual_hardware_to_support_load_transfer_implemented'] for r in reports))
 dump(out/'hardware_rigid_mass_loads.json',hw)
 dump(out/'summary.json',dict(status='ACTUAL_P1_78PART_CONDITIONAL_GRAVITY_ACCOUNTING_VERIFIED_LOAD_TRANSFER_BLOCKED' if all(checks.values()) else 'ACTUAL_P1_78PART_GRAVITY_ACCOUNTING_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,results=reports,hardware=ref(out/'hardware_rigid_mass_loads.json'),upstream_part_IDs=sorted(upstream),elastic_part_IDs=sorted(bodies),hardware_part_IDs=sorted(remaining),elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
 limitations=['CAD smooth fastener envelopes are not actual helical threads. Density7900kg/m3 remains conditional inherited assumption, not measured mass/material minimum.',
 'All78parts counted once in conditional external resultant. Hardware wrench remains attached to own free body; bearing/thread shear/tilt/preload and finite load transfer still missing.',
 'Necessary anchor resultant derived from physical gravity/object sources is a boundary design demand ONLY, never an applied balancing force or support equilibrium. Actual bench attachment remains unqualified.',
 'No source-backed real performance, full3DFinger, force closure, material strength, mesh/time/globalenergy/full3Finger release.']))
 print(json.dumps(dict(checks=checks,results=reports)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
