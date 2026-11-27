"""Actual AO route requirement contrast and chosen micro-drive contract.
Prescribed geometry virtual work is NOT a solved grasp or Finger equilibrium.
"""
import json, math, shutil, sys
import numpy as np
from scipy.integrate import quad
from baseline_registry import ROOT, REPO, S1, S2, ref, dump, sha
sys.path.insert(0, str(S2/'scripts'))
from finger_structure import E_PET, E_RAIL, width

def route(theta):
    # Algebraic extraction of wire_motion path (avoids its unrelated mesh
    # dependency). P is the actual swivel pivot under prescribed tip transform.
    c=math.cos(theta);s=math.sin(theta)
    tx,tz=tip_position(theta)
    P=np.array([tx-7*c+8*s,0,tz+7*s+8*c])
    vx,vz=44-P[0],25-P[2]
    beta=-(math.atan2(vz,vx)-math.acos(11.25/math.hypot(vx,vz)))
    t=np.array([math.sin(beta),0,math.cos(beta)]);normal=np.array([math.cos(beta),0,-math.sin(beta)])
    Q=np.array([44.,0,25])-11.25*normal
    u=np.array([-66.,5.]);u/=np.linalg.norm(u);n=np.array([-u[1],u[0]])
    if n[1]<0:n=-n
    phi=math.atan2(n[1],n[0]);end=math.atan2(-normal[2],-normal[0])
    while end<phi:end+=2*math.pi
    end_nipple=P+16*t
    return float(math.hypot(66,5)+11.25*(end-phi)+np.linalg.norm(Q-end_nipple))*.001

def tip_position(theta):
    if abs(theta)<1e-9:
        # Stable analytic continuation needed by quadrature/derivatives at0.
        x=50-88*(theta/2-theta**3/24+theta**5/720)-5*math.sin(theta)
        z=-7-88*(1-theta**2/6+theta**4/120)-5*math.cos(theta)
    else:x=50-88/theta*(1-math.cos(theta))-5*math.sin(theta);z=-7-88/theta*math.sin(theta)-5*math.cos(theta)
    return x,z

def inward(theta):
    return .001*(50-tip_position(theta)[0])

def derivative(f,x,h):return (f(x-2*h)-8*f(x-h)+8*f(x+h)-f(x+2*h))/(12*h)

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/batch6_operating1';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'models/standard_drive/batch6_sources1/reviewed.json'
    parent=ROOT/'cad/exports/revAO_root2/summary.json'
    deps=[source,parent,ROOT/'scripts/drive_system_layout.py',S1/'scripts/wire_motion.py',S1/'scripts/mechanism_motion.py',S2/'scripts/finger_structure.py',S2/'models/materials/evidence.json',ROOT/'validation/overload/JH1M_interval1/summary.json']
    dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),dependencies=[ref(p) for p in deps],
        predeclared_checks=dict(derivative_relative_max=1e-6,work_relative_max=1e-6),
        assumptions='100g vertical static load; three equal horizontal normal forces; friction0.2/0.4/0.8 scenarios, no measured lower bound; prescribed tip trajectory0..60deg. No force closure or Stage3 operation.',
        elastic_reference='Unbonded separate-layer prescribed common curvature, Rail88mm and PET86.2mm. Energy reference only, NOT actual coupled equilibrium, contact, strength or grasp demand.'))
    facts=json.loads(source.read_text());motor=facts['motor'];r=.01125
    stall=motor['extrapolated_stall_torque_kgcm']*.0980665
    # Linear ideal motor relation is a screening assumption, not a supplier curve fit.
    recommend_I=.25*motor['extrapolated_stall_current_A']
    recommend_tau=stall*(recommend_I-motor['no_load_current_A'])/(motor['extrapolated_stall_current_A']-motor['no_load_current_A'])
    krot=2*E_RAIL*.003*.0002**3/12/.088+quad(lambda s:E_PET*width(s)*.0003**3/12,0,.0862,epsabs=1e-14)[0]/.0862**2
    rows=[];check=[];start=route(0)
    for deg in (0,15,30,45,60):
        x=math.radians(deg);ds=-derivative(route,x,1e-4);dx=derivative(inward,x,1e-4)
        ds2=-derivative(route,x,5e-5);dx2=derivative(inward,x,5e-5)
        check.append(max(abs(ds-ds2)/abs(ds),abs(dx-dx2)/abs(dx)))
        for mu in (.2,.4,.8):
            normal=.1*9.80665/(3*mu);moment_contact=normal*dx;moment_elastic=krot*x
            tension=(moment_contact+moment_elastic)/ds;torque=tension*r
            current=.1+1.5*torque/stall;rpm=310*(1-torque/stall)
            rows.append(dict(angle_deg=deg,assumed_mu=mu,normal_per_finger_N=normal,stroke_m=start-route(x),
                stroke_derivative_m_rad=ds,inward_derivative_m_rad=dx,
                reference_elastic_moment_Nm=moment_elastic,reference_contact_moment_Nm=moment_contact,
                conditional_tension_N=tension,conditional_motor_torque_Nm=torque,
                ideal_linear_motor_current_A=current,ideal_linear_motor_rpm=rpm,
                within_general_current_recommendation=current<=recommend_I))
    work=[]
    end=math.pi/3
    for mu in (.2,.4,.8):
        normal=.1*9.80665/(3*mu)
        integrated=quad(lambda x:((normal*derivative(inward,x,1e-4)+krot*x)/(-derivative(route,x,1e-4)))*(-derivative(route,x,1e-4)),0,end,epsabs=1e-11)[0]
        expected=normal*(inward(end)-inward(0))+.5*krot*end**2
        work.append(dict(mu=mu,tendon_work_J=integrated,contact_work_J=normal*(inward(end)-inward(0)),stored_reference_J=.5*krot*end**2,relative_error=abs(integrated-expected)/expected))
    checks_pass=max(check)<=1e-6 and max(w['relative_error'] for w in work)<=1e-6 and all(x['stroke_derivative_m_rad']>0 for x in rows)
    result=dict(status='CONDITIONAL_ROUTE_REQUIREMENT_CHECK_PASS' if checks_pass else 'FAIL',scope='ACTUAL AO ROUTE / PRESCRIBED VIRTUAL-WORK REQUIREMENT CONTRAST, NOT GRASP EQUILIBRIUM',
        producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),source=ref(source),parent=ref(parent),rows=rows,derivative_refinement_relative_errors=check,work=work,
        conditional_rotational_stiffness_Nm_rad=krot,stroke_0_to_60_m=start-route(end),
        motor_screen=dict(item=1101,extrapolated_stall_torque_Nm=stall,extrapolated_stall_tension_N=stall/r,
            recommended_current_scenario_A=recommend_I,ideal_torque_at_current_scenario_Nm=recommend_tau,ideal_tension_at_current_scenario_N=recommend_tau/r,
            guaranteed_maximum_N=None,continuous_torque_rating_Nm=None,shaft_radial_rating_N=None,shaft_axial_rating_N=None),
        decision='Select1101+1996+bolted annular spool for finite interface evaluation only. Retain11.25mm cable center radius and110,0,20 axis. No installed limiter or current command qualifies protection.',
        comparison=[dict(architecture='AO17HS15-1504S1+custom clutch',holding_torque_Nm=.45,running_torque_Nm=None,reason='Existing holding torque is not normal demand or a maximum output bound; many custom friction/preload/alignment parts'),
            dict(architecture='1101 direct standard hub',advantage='Smaller standard motor and stock hub replace custom clutch interfaces, spring/liner/adjuster and clamp-bolt process',unresolved='Motor mount, rated bearing support, axial/set-screw retention, cable anchor, overload and actual operating demand'),
            dict(architecture='1101+JH-1M',decision='Deferred',reason='Additional couplings; catalog interval still lacks installed energy/fault/thermal maximum')],
        actual_operating_requirement_qualified=False,protection_qualified=False,actual_capacity_qualified=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],stroke_m=result['stroke_0_to_60_m'],peak_conditional_tension_N=max(x['conditional_tension_N'] for x in rows),current_recommendation_failures=sum(not x['within_general_current_recommendation'] for x in rows))))
    assert all(sha(REPO/r['path'])==r['SHA256'] for r in json.loads((out/'inputs.json').read_text())['dependencies'])
    raise SystemExit(0 if checks_pass else 2)
if __name__=='__main__':main()
