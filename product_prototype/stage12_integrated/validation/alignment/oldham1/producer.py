"""Ideal Oldham translation reference, NOT actual hub/contact capacity.
Independent loop solve vs closed form and finite differences. Translation
inertia is constant for fixed offset; do not omit sliding friction in product.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,ref,dump
def position(theta,e):
    u=np.array([math.cos(theta),math.sin(theta)]);v=np.array([-u[1],u[0]])
    # Disc centre on input tongue line u and output tongue line v.
    A=np.vstack((v,u));return np.linalg.solve(A,np.array([0.,e*u[0]]))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/alignment'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    e=.0002;m=.00115;omega=300*2*math.pi/60;rows=[]
    for h in (.001,.0005):
        pe=[];ve=[];ae=[];ee=[]
        for t in np.linspace(0,2*math.pi,361):
            x=position(t,e);x1=position(t+h,e);x0=position(t-h,e)
            v=(x1-x0)/(2*h)*omega;acc=(x1-2*x+x0)/h**2*omega**2
            exact=e/2*np.array([1+math.cos(2*t),math.sin(2*t)])
            exactv=e*omega*np.array([-math.sin(2*t),math.cos(2*t)])
            exacta=-2*e*omega**2*np.array([math.cos(2*t),math.sin(2*t)])
            pe.append(np.linalg.norm(x-exact));ve.append(np.linalg.norm(v-exactv)/(e*omega));ae.append(np.linalg.norm(acc-exacta)/(2*e*omega**2));ee.append(abs(.5*m*v@v/(.5*m*e*e*omega**2)-1))
        rows.append(dict(angular_FD_step_rad=h,max_loop_position_error_m=float(max(pe)),velocity_relative=float(max(ve)),acceleration_relative=float(max(ae)),translation_energy_relative=float(max(ee))))
    result=dict(status='PASS' if all(r['max_loop_position_error_m']<1e-12 and max(r['velocity_relative'],r['acceleration_relative'],r['translation_energy_relative'])<.001 for r in rows) else 'FAIL',
        scope='IDEAL ZERO-FRICTION SLIDING KINEMATICS / TRANSLATIONAL INERTIA REFERENCE ONLY',
        rows=rows,nominal_disc_mass_kg=m,offset_m=e,scenario_rpm=300,translation_inertia_kg_m2=m*e*e,
        nominal_disc_translation_force_magnitude_N=2*m*e*omega**2,
        manufacturer_source='https://www.huco.com/shop/couplings/oldham-couplings/oldham-disc/238-19',
        published_disc=dict(OD_mm=19.1,parallel_compensation_mm=.2,angular_compensation_deg=.5,axial_compensation_mm=.10,peak_torque_Nm=.43,static_break_torque_Nm=2.,torsional_stiffness_Nm_rad=115.),
        product_alignment_reaction_qualified=False,force_cap_qualified=False,
        missing=['Actual two hubs, bores and shaft4.4mm adaptation','Contact/friction/preload and actual restoring force','Combined offset/angular/axial derating and motor bearing load envelope','Actual rotor inertia and thermal/life'],
        warning='Disc-only data; peak/static break are not guaranteed torque-limiter release. Nominal mass is not an inertia upper bound. Translation force is NOT total motor reaction.',producer=ref(out/'producer.py'))
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
