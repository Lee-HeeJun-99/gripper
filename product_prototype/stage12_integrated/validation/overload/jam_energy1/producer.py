"""Independent jam-energy control: a static torque limiter is NOT a tension cap.

One load-side inertia, linear tension spring, blocked distal end, constant
positive clutch torque until first turning point. No damping. Assumed stiffness
and provisional inertia are explicit. This is not actual cable/contact dynamics.
"""
import argparse,json,math,shutil,sys
import numpy as np
from scipy.integrate import solve_ivp
from baseline_registry import ROOT,S2,ref,dump
def peak(F,T0,k,J,omega):return F+math.sqrt((T0-F)**2+k*J*omega**2)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/overload'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    original=S2/'validation/integrated/torsion_dynamic1/summary.json'
    J=json.loads(original.read_text())['J_provisional_load_kg_m2']
    # Published HPMC torque is MINIMUM in its drawing, not maximum safety torque.
    tau_ref=2.5*.00706155183333;r=.011165;F=tau_ref/r
    rows=[]
    for k in (1000.,10000.): # same declared EA scenarios as prior study; NOT supply bounds
        for rpm in (0.,60.,300.): # prescribed test scenarios, NOT approved operating speed
            omega=rpm*2*math.pi/60;T0=.968626 # prior conditional no-object corner maximum, not grasp requirement
            wn=r*math.sqrt(k/J)
            # x is cable extension; initial spring load T0. Drive force F persists.
            def rhs(t,y):return [y[1],(F-k*y[0])*r*r/J]
            duration=2*math.pi/wn
            def stop(t,y):return y[1]
            stop.direction=-1;stop.terminal=True
            results=[]
            for step in (duration/100,duration/200):
                sol=solve_ivp(rhs,[0,duration],[T0/k,r*omega],rtol=1e-11,atol=1e-13,max_step=step,events=stop)
                assert sol.success and len(sol.t_events[0])==1
                x,v=sol.y_events[0][0];numeric=k*x
                energy=.5*J*(v/r)**2+.5*k*x*x-(.5*J*omega**2+.5*T0*T0/k+F*(x-T0/k))
                results.append(dict(peak_N=float(numeric),energy_residual_J=float(energy),steps=len(sol.t)))
            exact=peak(F,T0,k,J,omega)
            rows.append(dict(assumed_stiffness_N_m=k,scenario_rpm=rpm,initial_tension_N=T0,
                constant_clutch_reference_force_N=F,exact_peak_N=exact,numerical=results,
                reference_relative=abs(results[-1]['peak_N']-exact)/exact,
                refinement_relative=abs(results[0]['peak_N']-results[1]['peak_N'])/exact))
    ok=all(x['reference_relative']<.001 and x['refinement_relative']<.001 and max(abs(v['energy_residual_J']) for v in x['numerical'])<1e-8 for x in rows)
    # Independent units check: J omega^2 is twice rotor kinetic energy.
    assert abs(peak(F,F,1000,J,10)-F-math.sqrt(2*1000*(.5*J*100)))<1e-12
    result=dict(status='PASS' if ok else 'FAIL',scope='CONDITIONAL JAM ENERGY MODEL VERIFICATION ONLY',
        product_force_cap_status='NOT QUALIFIED',rows=rows,J_provisional_load_kg_m2=J,
        published_torque_Nm=tau_ref,published_rating_kind='MINIMUM; NOT A GUARANTEED MAXIMUM',
        source='https://www.magtrol.com/wp-content/uploads/hpmc-25.pdf',
        data_source=ref(original),producer=ref(Path(__file__)),
        limitations=['Five-part provisional inertia omits rotating hardware; limiter inertia not included',
          'Wire EA and speed are scenarios, not certified bounds','No friction, shaft elasticity, wave propagation or impact contact',
          'Initial no-object load is not grasp demand','Motor holding torque and clutch minimum rating do not certify a force cap'],
        required='Maximum torque vs temperature/rate, complete downstream inertia, measured/qualified EA, allowable structural peak, bounded operating speed; hardware jam validation')
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));sys.exit(0 if ok else 2)
if __name__=='__main__':main()
