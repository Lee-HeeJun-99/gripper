"""Independent installed-stack geometry/work and retained product-load review."""
import sys,json,math,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');src=ROOT/'validation/integrated/primaryP1_installed_stack42/summary.json';d=json.loads(src.read_text());cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';assert d['candidate']==ref(cp)
 loads=ROOT/'validation/integrated/primaryP1_anchor41_stream256/summary.json';ld=json.loads(loads.read_text());assert ld['candidate']==ref(cp);rows=[];checks=[]
 for r in d['rows']:
  # Independent analytic annular seat from actual measured area + known
  # source head diameter. Recover inner radius, don't assume full head disk.
  ro=4.25;area=r['head_base_area_mm2'];ri=math.sqrt(ro*ro-area/math.pi);reff=2/3*(ro**3-ri**3)/(ro**2-ri**2);p=.8;lead=p/(2*math.pi);L=r['nominal_overlap_length_mm'];EA=200000.*math.pi*2.5**2
  # Numerical integrate N(z)^2/EA over installed major-shank domain. This
  # independently checks the producer's closed-form uniform unloading.
  z=np.linspace(60,80,20001);lo,hi=r['nominal_engagement_interval_mm'];N=np.clip((hi-z)/L,0,1);C=float(np.trapezoid(N*N,z)/EA);formula=r['conditional_major_shank']['uniform_engagement_compliance_mm_N'];err=abs(C/formula-1)
  # Unit screw virtual work: F dz = T dtheta, dz=p*dtheta/(2pi).
  angles=np.array([-.1,-.001,.001,.1]);vw=float(abs(lead*angles-p*angles/(2*math.pi)).max());demand=[]
  for case in ld['rows']:
   F=case['bolt_tension_N'][r['station']];demand.append(dict(case=case['case'],historical_conditional_axial_N=F,frictionless_thread_torque_Nmm=F*lead,conditional_uniform_headseat_pressure_MPa=F/area,conditional_uniform_nutseat_pressure_MPa=F/r['nut_receiver_area_mm2'],conditional_uniform_engagement_extension_mm=F*C,physical_operating_load=False))
  checks.append(dict(station=r['station'],actual_head_inner_radius_matches_base_clearance=abs(ri-2.75)<1e-7,independent_axial_energy_integration=err<1e-7,independent_screw_virtual_work=vw<1e-10,absent_material_not_zero=r['minimum_material_allowable_MPa'] is None,absent_preload_not_zero=r['installed_preload_N'] is None,no_effective_engagement_claim=r['effective_engagement_length_mm'] is None,smooth_tie_rejected=not r['smooth_envelope_unit_axial_equilibrium']['feasible'],torqueless_frictionless_thread_rejected=not r['hypothetical_helical_without_reaction_torque']['feasible']))
  rows.append(dict(station=r['station'],actual_head_annulus_inner_radius_mm=ri,uniform_headseat_effective_friction_radius_mm=reff,conditional_uniform_headseat_mu_required=lead/reff,conditional_outer_radius_best_case_mu_lower_bound=lead/ro,conditional_major_radius_thread_lead_tangent=lead/2.5,uniform_major_shank_numerical_compliance_mm_N=C,independent_compliance_relative_error=err,unit_screw_virtual_work_error_Nmm=vw,historical_conditional_demands=demand))
 passed=all(all(v for k,v in c.items() if k!='station') for c in checks)
 dump(out/'summary.json',dict(status='ACTUAL_P1_INSTALLED_STACK_INDEPENDENT_BOUNDARY_REVIEW' if passed else 'ACTUAL_P1_INSTALLED_STACK_INDEPENDENT_AUDIT_FAIL',candidate=ref(cp),source=ref(src),historical_conditional_load_source=ref(loads),verifier=ref(out/'verifier.py'),rows=rows,checks=checks,local_checks_pass=passed,physical_stack_qualified=False,physical_operating_sourcefield=None,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Historical loads are frozen conditional variational sensitivities with known negative full-domain gaps;not physical operating equilibria.','Calculated friction thresholds assume uniform annular pressure and unpreloaded axial force at head. They are required conditional bounds,not supplied material/friction data or guaranteed locking.','Thread friction can react screw torque internally;frictionless helical rejection is not proof all real threaded joints fail.','Uniform major-shank axial energy is independent boundary sensitivity only;not nut/core/flank/head finite-body deformation or global coupled energy.','No new numerical pressure,mesh,material,strength,operating or hardware gate qualified.']))
 print(json.dumps(dict(local_checks_pass=passed,checks=checks,rows=rows)));assert passed
if __name__=='__main__':main()
