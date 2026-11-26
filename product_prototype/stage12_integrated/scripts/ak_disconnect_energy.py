"""Finite-delay torque disconnect on actual AK drum geometry; conditional only.
No rated disconnect, allowable, complete inertia or installed mechanism claimed.
"""
import sys,json,math,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S2,ref,sha,dump
sys.path.insert(0,str(S2/'scripts'))
from extract_geometry import load,properties

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/overload/AK_disconnect2';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAK_integral2/summary.json';doc=json.loads(source.read_text())
    parts={n:r for n,r in doc['part_references'].items() if n.startswith('F0_DRUM')};assert len(parts)==6
    refs=[source,S2/'scripts/extract_geometry.py']
    for r in parts.values():
        p=REPO/r['path'];assert sha(p)==r['SHA256'];refs.extend([p,p.with_suffix('.stl')])
    dump(out/'inputs.json',dict(sources=[ref(p) for p in refs],producer=ref(out/'producer.py'),
        acceptance=dict(geometric_inertia_STL_relative_max=.01,peak_relative_max=1e-7,energy_absolute_J_max=1e-9),
        plan='Actual six AK drum parts; conditional unit-density geometry then finite-delay ideal zero-torque disconnect; independently integrated piecewise ODE and STL moments. No full physical cap.'))
    rows=[]
    for n,r in parts.items():
        v,c,j=properties(load(REPO/r['path']));C=float(j[1,1]+v*((c[0]-.110)**2+(c[2]-.020)**2))
        rho=7830 if 'BOLT' in n or 'FACTORY_NIPPLE' in n else 2700
        rows.append(dict(part=n,STEP=r,STL=ref((REPO/r['path']).with_suffix('.stl')),volume_m3=v,centroid_m=c.tolist(),axis_inertia_per_density_m5=C,scenario_density_kg_m3=rho,physical_density_kg_m3=None))
    J=sum(r['axis_inertia_per_density_m5']*r['scenario_density_kg_m3'] for r in rows)
    k=10000.;r=.011165;T0=.968626;F=1.25*T0;omega=2*math.pi;wn=r*math.sqrt(k/J);xeq=F/k;A=T0/k-xeq;v0=r*omega
    def state(t):return xeq+A*math.cos(wn*t)+v0/wn*math.sin(wn*t),-A*wn*math.sin(wn*t)+v0*math.cos(wn*t)
    turning=math.atan2(v0,wn*A)/wn
    trials=[]
    for delay in (0.,.001,.01,.05):
        x,v=state(delay);energy=.5*k*x*x+.5*J*(v/r)**2
        peak_before=k*state(min(delay,turning))[0]
        # After zero drive, positive extension turning peak follows energy.
        peak_after=math.sqrt(2*k*energy) if v>0 else k*x
        trials.append(dict(delay_s=delay,disconnect_x_m=x,disconnect_v_m_s=v,stored_plus_kinetic_J=energy,drive_work_J=F*(x-T0/k),peak_before_N=peak_before,peak_after_N=peak_after,disconnect_tensile_velocity_positive=bool(v>0),peak_N=max(peak_before,peak_after)))
    sustained=F+math.sqrt((T0-F)**2+k*J*omega**2)
    result=dict(status='CONDITIONAL_DISCONNECT_REQUIREMENTS_COMPUTED',candidate=ref(source),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),parts=rows,
        conditional_partial_J_kg_m2=J,k_scenario_N_m=k,r_scenario_m=r,T0_scenario_N=T0,F_scenario_N=F,omega_scenario_rad_s=omega,first_turning_s=turning,sustained_peak_N=sustained,trials=trials,
        ideal_instantaneous_disconnect_peak_N=math.sqrt(T0*T0+k*J*omega**2),
        maximum_additional_released_energy_for_ceiling='E_extra <= (T_allow^2 - T_peak_after^2)/(2*k); also require peak_before <= T_allow. No allowable assigned.',
        limitations=['Six drum solids only; bearing race, entrained cable and reflected upstream inertia unresolved',
        'Densities, EA, initial tension, radius and speed are scenarios, not bounds; purchased-envelope hardware is not physical mass',
        'Ideal disconnect removes drive torque after prescribed delay; no actual CAD, trigger, residual drag, stored spring release or fault bound',
        'Post-disconnect first tensile excursion terminates at zero extension; negative initial velocity peaks at disconnect, no later fictitious compression rebound',
        'No new material/source rating, structural allowable, actual load capacity, hardware or global assembly energy certification'],product_force_cap_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(J=J,sustained=sustained,trials=trials),indent=2))
if __name__=='__main__':main()
