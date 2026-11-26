"""Independent STL moments and piecewise initial-value verification."""
import json,math,shutil
import numpy as np
import trimesh
from scipy.integrate import solve_ivp
from baseline_registry import ROOT,REPO,ref,sha,dump

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/overload/AK_disconnect_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/overload/AK_disconnect1/summary.json';d=json.loads(src.read_text());inp=json.loads((REPO/d['inputs']['path']).read_text())
    for r in inp['sources']+[inp['producer'],d['inputs']]:assert sha(REPO/r['path'])==r['SHA256']
    geom=[]
    for p in d['parts']:
        m=trimesh.load(REPO/p['STL']['path'],force='mesh');assert m.is_watertight and m.is_volume
        c=m.center_mass*.001;C=m.moment_inertia[1,1]*1e-15+m.volume*1e-9*((c[0]-.110)**2+(c[2]-.020)**2)
        err=abs(C/p['axis_inertia_per_density_m5']-1);assert err<.01
        geom.append(dict(part=p['part'],STL_axis_inertia_per_density_m5=float(C),relative_error=float(err)))
    J=d['conditional_partial_J_kg_m2'];k=d['k_scenario_N_m'];r=d['r_scenario_m'];F=d['F_scenario_N'];T0=d['T0_scenario_N'];w=d['omega_scenario_rad_s'];period=2*math.pi/(r*math.sqrt(k/J));rows=[]
    for t in d['trials']:
        refinements=[]
        for divisions in (100,200):
            y0=[T0/k,r*w];before=T0
            def event(t,y):return y[1]
            event.direction=-1
            def run(duration,y,force):
                return solve_ivp(lambda t,z:[z[1],r*r/J*(force-k*z[0])],[0,duration],y,rtol=1e-11,atol=1e-13,max_step=period/divisions,events=event)
            if t['delay_s']:
                s=run(t['delay_s'],y0,F);assert s.success;y0=s.y[:,-1]
                before=max([T0,k*y0[0]]+[k*y[0] for y in s.y_events[0]])
            energy=.5*k*y0[0]**2+.5*J*(y0[1]/r)**2
            balance=energy-(.5*T0*T0/k+.5*J*w*w+F*(y0[0]-T0/k));assert abs(balance)<1e-9
            post=run(period,y0,0);assert post.success and len(post.y_events[0])>=1
            after=max(k*y[0] for y in post.y_events[0]);peak=max(before,after)
            err=abs(peak/t['peak_N']-1);assert err<1e-7
            refinements.append(dict(peak_N=float(peak),relative_error=float(err),energy_residual_J=float(balance),steps=len(post.t)))
        assert abs(refinements[0]['peak_N']/refinements[1]['peak_N']-1)<1e-7
        rows.append(dict(delay_s=t['delay_s'],refinements=refinements))
    # A zero-force/zero-inertia correction must not erase initial kinetic energy.
    instant=d['ideal_instantaneous_disconnect_peak_N'];assert instant>T0
    tamper_rejected=abs(instant/T0-1)>1e-7;assert tamper_rejected
    result=dict(status='PASS',scope='ACTUAL AK GEOMETRY / CONDITIONAL DISCONNECT MODEL ONLY',source=ref(src),producer=ref(out/'producer.py'),geometry=geom,trials=rows,zero_kinetic_energy_negative_control_rejected=tamper_rejected,product_force_cap_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
