"""Independent closed-form actual spool integral and saved jam state checks."""
import json,math,shutil
from baseline_registry import ROOT,REPO,ref,dump,sha
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/overload/batch6_drive_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
p=ROOT/'validation/overload/batch6_drive_inertia3/summary.json';d=json.loads(p.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text())
assert all(sha(REPO/r['path'])==r['SHA256'] for r in inp['dependencies'])
expected=math.pi/2*(11**4*2+(12**4-11**4)-1.6**4*2)-4*(math.pi/2*1.65**4*2+math.pi*1.65**2*2*6.35**2)
spool=next(x for x in d['parts'] if x['part_ID']=='F0_SPOOL');error=abs(spool['axis_geometric_inertia_mm5']/expected-1)
assert error<1e-8
J=sum(x['scenario_axis_inertia_kg_m2'] for x in d['parts']);errors=[]
for c in d['cases']:
 k=c['stiffness_N_m'];F=c['constant_force_scenario_N'];T=c['initial_tension_N'];w=c['initial_speed_rpm']*math.pi/30
 # independently reconstruct energy at analytic turning tension, subtract drive work
 peak=c['exact_peak_N'];res=(peak**2-T**2)/(2*k)-F*(peak-T)/k-J*w*w/2
 errors.append(abs(res));assert abs(res)<1e-12
 assert all(abs(n['peak_N']/peak-1)<.001 and abs(n['energy_residual_J'])<1e-8 for n in c['numerical'])
assert abs((spool['axis_geometric_inertia_mm5']*1.01)/expected-1)>1e-8
r=dict(status='ANALYTIC_SPOOL_AND_SCENARIO_ENERGY_PASS_MESH_FAIL_RETAINED',source=ref(p),producer=ref(out/'producer.py'),spool_closed_form_mm5=expected,spool_relative_error=error,energy_residuals_J=errors,input_hashes_match=True,perturbed_inertia_rejected=True,mesh_status=d['mesh_inertia_verification'],mesh_failures=d['mesh_inertia_errors'],source_status_correction='Source top-level VERIFIED label is overbroad: its explicit mesh_inertia_verification is FAIL; no overall inertia certification',actual_capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',r);print(json.dumps(r))
