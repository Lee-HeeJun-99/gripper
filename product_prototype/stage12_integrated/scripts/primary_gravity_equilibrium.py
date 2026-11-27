"""Same actual P1 gravity-loaded corner branch; all inherited inequalities retained."""
import json,sys,shutil,argparse
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
import primary_terminal_corner_v2 as corner
import primary_finger_tangent_v5 as tangent
from primary_gravity_pullback import Gravity,G,ROOT_POINT,C

def main():
 ap=argparse.ArgumentParser();ap.add_argument('tag');ap.add_argument('--mass',required=True);ap.add_argument('--n',type=int,required=True);ap.add_argument('--factor',type=float,default=1);a=ap.parse_args();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/finger'/a.tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 mass=ROOT/'validation/finger'/a.mass/'mass_points.json';points=json.loads(mass.read_text());gravity=Gravity(points);base=tangent.gradient
 def gradient(v,n,T,E1,E2,width):return base(v,n,T,E1,E2,width)+gravity.evaluate(v,n,a.factor)[1]
 tangent.gradient=gradient
 source=ROOT/'validation/finger/primaryP1_corner_demand1/cases.json';seed=next(r for r in json.loads(source.read_text()) if r['n']==a.n);candidate=ROOT/'cad/exports/primaryP1_fixture15/summary.json'
 deps=[mass,source,candidate,ROOT/'scripts/primary_gravity_pullback.py',ROOT/'scripts/primary_terminal_corner_v2.py',ROOT/'scripts/primary_finger_equilibrium_v5.py',ROOT/'scripts/primary_finger_tangent_v5.py',ROOT/'scripts/rod_point_jacobian.py',ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py']
 dump(out/'inputs.json',dict(candidate=ref(candidate),inputs=[ref(p) for p in deps],producer=ref(out/'producer.py'),gravity_factor=a.factor,criteria=dict(force_N_max=1e-8,gap_m_min=-1e-9,mesh_relative_max=.01,time_relative_max=.001),scope='Actual P1 distributed CAD sliced masses,rigid terminal/swivel/rotor transforms,ideal taut cable gravity potential; fixed Root and motor axes,frictionless planar prescribed20mm stop. Conditional densities and moduli.'))
 r=corner.solve(seed,seed['T_N']);v=np.array(r['state']);U,grad,positions=gravity.evaluate(v,a.n,a.factor,True);r.update(gravity_factor=a.factor,gravity_potential_J=U,gravity_gradient_J=grad.tolist(),deformed_mass_points=positions)
 # Gravity-free endpoint traction T is the actuator's generalized cable-length work.
 # Cable gravitational potential adds an endpoint force via dUg/dP and motor work;
 # root force/couple reconstructed from the entire moving subsystem, never hidden.
 t=np.array(r['cable_direction']);P=np.array(r['cable_port_m']);tip=np.array(r['terminal_tip_m']);moving=[p for p in positions if p['mode'] in ('rail','pet','terminal','swivel')];mg=sum(p['mass_kg'] for p in moving)*G*a.factor
 F=r['T_N']*t+np.array([r['normal_N'],-mg]);moment=np.cross(P-ROOT_POINT,r['T_N']*t)+np.cross(tip-ROOT_POINT,[r['normal_N'],0.])+sum(np.cross(np.array(p['position_m'])[[0,2]]-ROOT_POINT,[0.,-p['mass_kg']*G*a.factor]) for p in moving)
 r.update(moving_finger_mass_kg=sum(p['mass_kg'] for p in moving),finger_external_force_before_cable_gravity_N=F.tolist(),finger_external_scalar_XZ_moment_before_cable_gravity_Nm=float(moment),port_scope='Provisional finger balance excludes cable/rotor gravity pullback port split; do not apply as final Root/Motor loads until independent port reconstruction.')
 dump(out/'cases.json',[r]);dump(out/'summary.json',dict(status='ACTUAL_P1_GRAVITY_LOADED_CONDITIONAL_EQUILIBRIUM' if r['status']=='CONDITIONAL_CORNER_EQUILIBRIUM' else 'ACTUAL_P1_GRAVITY_LOADED_EQUILIBRIUM_FAIL',task_id='goal_primary_gravity_loaded_chain',candidate=ref(candidate),inputs=ref(out/'inputs.json'),cases=ref(out/'cases.json'),n=a.n,T_N=r['T_N'],normal_N=r['normal_N'],baseline_normal_N=seed['normal_N'],normal_change_N=r['normal_N']-seed['normal_N'],force_equivalent_N=r['KKT_force_equivalent_N'],minimum_dense_gap_m=r['minimum_dense_gap_m'],gravity_potential_J=U,whole_system_release=False,newly_qualified_system_gate_ids=[],SOFA_runs=0,limitations=['Conditional mass/typical moduli,ideal clamp/rigid terminal and motor,cable prescribed taut geometry rather than catenary','Gravityloadedstaticcandidate,not fullFrame/Ground compliant equilibrium,friction,dt/globalenergy orstrength','Independent force/virtualwork/CAD geometry verification and loadport split required']))
 print(json.dumps(dict(n=a.n,status=r['status'],T_N=r['T_N'],normal_N=r['normal_N'],force=r['KKT_force_equivalent_N'],gap=r['minimum_dense_gap_m'])))
 raise SystemExit(0 if r['status']=='CONDITIONAL_CORNER_EQUILIBRIUM' else 2)
if __name__=='__main__':main()
