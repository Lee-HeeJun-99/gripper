"""Geometry-coupled feasibility requirements, NOT a certified force cap.

Use actual RevAF rotating-part geometric integrals. Report inertia coefficients
per density, not purchased-bearing/motor-envelope fabricated physical inertia.
Illustrative force ceilings are NOT a structural allowable or grasp demand.
"""
import argparse,json,math,shutil,sys
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump
from jam_energy import peak

def allowed_force(Tmax,T0,k,J,omega):
    if Tmax<=T0:raise ValueError('Ceiling must exceed initial tension')
    return (Tmax*Tmax-T0*T0-k*J*omega*omega)/(2*(Tmax-T0))

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/overload'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/stage1/AF_geometry1/parts.json';parts=json.loads(source.read_text())
    coefficients=[]
    for row in parts:
        n=row['part_ID']
        if not (n.startswith('F0_DRUM') or n=='F0_CLUTCH_RETAINING_CLIP'):continue
        v=row['volume_m3'];c=np.array(row['centroid_m']);I=np.array(row['central_geometric_inertia_m5'])
        axis=I[1,1]+v*((c[0]-.110)**2+(c[2]-.020)**2)
        coefficients.append(dict(part=n,STEP=row['STEP'],volume_m3=v,axis_inertia_per_density_m5=float(axis),density_kg_m3=None,actual_mass_kg=None))
    # Explicit conditional make-material scenario, NOT a physical upper bound.
    J=0
    for r in coefficients:
        rho=7830 if 'BOLT' in r['part'] or r['part'].endswith('FACTORY_NIPPLE') or 'CLIP' in r['part'] else 2700
        J+=rho*r['axis_inertia_per_density_m5']
        r['illustrative_density_kg_m3']=rho
    ri=.0083;ro=.0096;radius=.01125
    reff_pressure=(2/3)*(ro**3-ri**3)/(ro**2-ri**2);reff_wear=(ri+ro)/2
    T0=.968626 # inherited CONDITIONAL no-object rod corner, not grasp demand
    rows=[]
    # No friction coefficient is fabricated. Maximum permissible variation
    # ratio is a REQUIREMENT on future measured/rated clutch/drag/preload.
    for ceiling in (2.,3.,5.):
        F=allowed_force(ceiling,T0,10000,J,0)
        zero_speed_ratio=F/T0
        Fscenario=1.25*T0
        budget=(ceiling-Fscenario)**2-(T0-Fscenario)**2
        speed=math.sqrt(max(0,budget)/(10000*J))
        analytic_peak=peak(F,T0,10000,J,0)
        rows.append(dict(illustrative_ceiling_NOT_allowable_N=ceiling,
            allowable_total_drive_torque_at_zero_speed_Nm=F*radius,
            max_total_torque_to_min_operating_torque_ratio_at_zero_speed=zero_speed_ratio,
            reference_back_substitution_N=analytic_peak,
            illustrative_constant_force_N=Fscenario,
            illustrative_k_N_m=10000,illustrative_speed_budget_rad_s=speed,
            illustrative_speed_budget_rpm=speed*60/(2*math.pi),
            note='No bearing drag, extra rotating inertia, delay, measured wire EA, spring/friction range or structural allowable included; not a safe operating envelope'))
        assert abs(analytic_peak-ceiling)<1e-12
        assert abs(peak(Fscenario,T0,10000,J,speed)-ceiling)<1e-12
    # Independent energy inversion control, rejects an unattainable request.
    assert allowed_force(2,T0,10000,J,1e6)<0
    result=dict(status='CONDITIONAL_DESIGN_REQUIREMENTS_VERIFIED',scope='Actual CAD inertia coefficients and algebraic protection-window requirements only',
        source=ref(source),candidate=ref(ROOT/'cad/exports/revAF_layout6/summary.json'),producer=ref(out/'producer.py'),
        coefficients=coefficients,conditional_partial_loadside_J_kg_m2=J,
        friction_annulus=dict(inner_m=ri,outer_m=ro,faces=2,uniform_pressure_reff_m=reff_pressure,uniform_wear_reff_m=reff_wear,torque_law='2*mu*N*reff plus parasitic bearing torque; mu and N NOT qualified'),
        scenario_initial_tension_N=T0,nominal_drum_radius_m=radius,requirements=rows,
        required_product_inputs=['actual normal operating load and preload','guaranteed/calibrated min/max slip torque vs temperature/rate','maximum bearing drag including jam/seizure failure analysis','complete rotating inertia including bearing outer race and entrained cable','actual cable EA and initial tension','bounded speed and detection/delay energy','qualified structural peak allowable'],
        product_force_cap_status='NOT QUALIFIED',motor_alignment_status='Separate rigid shaft-coupling path removed in CAD candidate; motor shaft/bearing overhang reactions NOT qualified',whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
