"""Actual keeper preload-setting contrast under fresh product necessary port loads.
Conditional rod calculations expose unresolved installed state, NOT a capacity law.
"""
import sys,json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_keeper60c/summary.json';cad=json.loads(cp.read_text());auditp=ROOT/'validation/integrated/primaryP1_keeperaudit60d/summary.json';au=json.loads(auditp.read_text());src=ROOT/'validation/integrated/primaryP1_contacts60c';cut=json.loads((src/'summary.json').read_text());rows=json.loads((src/'rows.json').read_text());ports=json.loads((src/'connector_ports.json').read_text())['ports'];cases=[];a=.5/(2*math.pi);E=200000.;dc=3-1.226869*.5;Ac=math.pi*dc**2/4
for case in rows:
 if not(case['feasible'] and case['explicit_unknown_host_resultant_port']):continue
 local=[]
 for port in ports:
  if port['label'].startswith('through'):continue
  bolt,nut=port['part_IDs'];bb=bounds(read(REPO/cad['part_references'][bolt]['path']));nb=bounds(read(REPO/cad['part_references'][nut]['path']));hs=-3 if bolt.startswith('F0_RF') else 29;eng=min(hs,nb[5])-max(bb[2],nb[2]);free=hs-nb[5];C=(free+eng/3)/(E*Ac);F=sum(r['coefficient_N'] for r in case['reactions'] if r['label']==port['label']);q=next(r for r in au['screw_results'] if r['bolt']==bolt);takeup=q['screw_lead_bracket_mm'][1];fullbackoff=.5/6+takeup+.5*2.650623321533203/360
  # Local screw free mode delta=a*theta: no axial energy while head may rotate.
  # Keeper has clearance: its tangent is ZERO inside gap; do not add a fixed DOF.
  b=np.array([1.,-a]);K=np.outer(b,b)/C;v=np.array([a,1.]);zero=float(np.linalg.norm(K@v));Fshear=a*F/(2.4/(2*math.sqrt(3))) # geometric maximum normal moment arm: half side length of AF2.4 regular hex; actual pressures unknown
  # Source-size SOLID cylinder overestimates split-pin cross-section. Stress is
  # a geometric scale only, never an allowable; two separate pin-guide planes.
  pin_solid_upperarea=math.pi*.9**2/4
  local.append(dict(bolt=bolt,required_axial_cut_N=F,thread_friction_ASSUMED=0,required_head_torque_Nmm=a*F,absolute_minimum_total_socket_normal_N=Fshear,actual_nut_engagement_mm=eng,basic_core_d_mm=dc,conditional_rod_compliance_mm_N=C,conditional_rod_extension_under_required_cut_N_mm=C*F,keeper_clearance_lead_mm=takeup,backoff_index_plus_keeper_and_nut_clearance_mm=fullbackoff,rod_only_preload_to_span_fullbackoff_N=fullbackoff/C,rod_only_stress_to_span_fullbackoff_MPa=fullbackoff/C/Ac,interpretation='Rodonlystiffnesscontrast; realhost/head/nut/flanks/cagecompliance lowers totalstiffness. This is NOT necessary installedpreload, strengthlimit or available capacity. Unknownpreload means retain NOTQUALIFIED.',free_screw_mode_inside_keeper_clearance_residual_N=zero,scalar_axial_tie_would_add_false_energy_Nmm=.5*a*a/C,source_splitpin_actual_area_mm2=None,solid_shaft_envelope_area_upper_mm2=pin_solid_upperarea,actual_physical_compliant_equilibrium=False))
 cases.append(dict(mu_ASSUMED=case['mu_ASSUMED'],ports=local,actual_host=cut['required_total_host_wrench_N_Nm']))
checks=dict(actual_candidate_hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in [*cad['part_references'].values(),cad['assembly'],cad['BOM']]),finite_nonnegative_cut_demands=all(q['required_axial_cut_N']>=0 and math.isfinite(q['required_head_torque_Nmm']) for c in cases for q in c['ports']),six_actual_screw_geometries_each=len(cases)>0 and all(len(c['ports'])==6 and all(q['actual_nut_engagement_mm']>0 for q in c['ports']) for c in cases),free_screw_mode_retained_inside_actual_clearance=all(q['free_screw_mode_inside_keeper_clearance_residual_N']<1e-8 for c in cases for q in c['ports']),no_physical_capacity_or_preload_claim=True)
dump(out/'summary.json',dict(status='ACTUAL83_INDEXED_KEEPER_SETTING_AND_LOAD_DEMAND_CONTRAST_NOT_INSTALLED_RETENTION',candidate=ref(cp),source=ref(src/'summary.json'),geometry_audit=ref(auditp),producer=ref(out/'producer.py'),thread_source=ref(ROOT/'models/standard_drive/primary_captive_sources59/thread_reviewed.json'),checks=checks,cases=cases,preload_known=False,keeper_finite_elasticity_solved=False,pin_eye_and_bent_legs_implemented=False,whole_system_release=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],next_mechanism='Keep the same actual P1 keeper/boss path. Resolve initial screw/hexnut/keeper index and set length with finite head/nut/flank/cage/guide compliance and actual split-pin axial retention. A nominal aligned zero-clearance clamp or rod-only spring is not a substitute. If an indexed keeper cannot preserve setting, change to an arbitrary-angle positive head lock with explicit grounded anchor; do not relax criteria.'))
print(json.dumps(dict(checks=checks,cases=len(cases),max_rod_only_preload_contrast_N=max(q['rod_only_preload_to_span_fullbackoff_N'] for c in cases for q in c['ports']))));raise SystemExit(0 if all(checks.values()) else 2)
