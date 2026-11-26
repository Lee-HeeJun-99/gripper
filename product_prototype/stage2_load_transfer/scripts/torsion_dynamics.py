"""Fixed-axis two-inertia CONDITIONAL torsion coupon, analytic vs Newmark.
No SOFA/SDK changes; no imposed q/v; not whole Rev AA dynamics approval.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from load_requirements import ROOT,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    geompath=ROOT/'models/geometry/revAA_extract2/summary.json';geometry=json.loads(geompath.read_text())
    compliancepath=ROOT/'validation/convergence/torsion1/summary.json';spring=1/json.loads(compliancepath.read_text())['shaft_torsional_compliance_rad_Nm']
    inventory=[]
    for x in geometry['parts']:
        if x['part_ID'] not in ('F0_DRUM','F0_DRUM_NIPPLE_CAP','F0_SHAFT','F0_COUPLING_UPPER','F0_COUPLING_LOWER'):continue
        rho=7830 if x['part_ID']=='F0_SHAFT' else 2700
        c=np.array(x['centroid_m']);J=np.array(x['central_geometric_inertia_m5'])
        inertia=rho*(J[1,1]+x['volume_m3']*((c[0]-.080)**2+(c[2]-.020)**2))
        inventory.append(dict(part=x['part_ID'],assumed_nominal_density_kg_m3=rho,CAD_envelope_mass_kg=rho*x['volume_m3'],axis_inertia_kg_m2=float(inertia)))
    Jm=54e-7 # manufacturer rotor54 g cm^2, not motor body mass inertia
    Jd=sum(x['axis_inertia_kg_m2'] for x in inventory)
    omega=math.sqrt(spring*(1/Jm+1/Jd));duration=20*2*math.pi/omega
    # Average acceleration phase-lag: O(omega^3 * t * dt^2 /12).
    # Choose dt BEFORE calculation from a 1e-4 phase-error budget, not scan.
    n=math.ceil(duration/math.sqrt(12e-4/(omega**3*duration)))
    torque=.010;M=np.diag([Jm,Jd]);K=spring*np.array([[1.,-1.],[-1.,1.]])
    f=np.array([torque,-torque]);records=[];trajectories=[]
    for steps in (n,2*n):
        dt=duration/steps;inv=np.linalg.inv(M+.25*dt*dt*K)
        q=np.zeros(2);v=np.zeros(2);acc=np.linalg.solve(M,f)
        qe=[];ve=[];pe=[];ee=[];deltas=[]
        for i in range(steps+1):
            t=i*dt;delta=q[0]-q[1]
            exact=torque/spring*(1-math.cos(omega*t));exactv=torque/spring*omega*math.sin(omega*t)
            energy=.5*float(v@M@v+q@K@q);work=torque*delta
            qe.append(abs(delta-exact)/(torque/spring));ve.append(abs(v[0]-v[1]-exactv)/(torque/spring*omega))
            pe.append(abs(Jm*v[0]+Jd*v[1]));ee.append(abs(energy-work)/(torque**2/spring));deltas.append(delta)
            if i==steps:break
            pred=q+dt*v+.25*dt*dt*acc;newacc=inv@(f-K@pred)
            q=pred+.25*dt*dt*newacc;v=v+.5*dt*(acc+newacc);acc=newacc
        records.append(dict(steps=steps,dt_s=dt,max_displacement_reference_relative=max(qe),max_velocity_reference_relative=max(ve),
            max_angular_momentum_residual_Nms=max(pe),max_energy_work_relative=max(ee),
            status='PASS' if max(qe)<.001 and max(ve)<.001 and max(ee)<1e-8 and max(pe)<1e-12 else 'FAIL'))
        trajectories.append(np.array(deltas))
    convergence=float(np.max(abs(trajectories[0]-trajectories[1][::2]))/(torque/spring))
    np.savez_compressed(out/'trajectory.npz',coarse_relative_angle_rad=trajectories[0],fine_relative_angle_rad=trajectories[1])
    result=dict(status='PASS' if all(r['status']=='PASS' for r in records) and convergence<.001 else 'FAIL',
        scope='CONDITIONAL FIXED-AXIS TWO-INERTIA TORSION COUPON ONLY; NOT FULL REV AA DYNAMICS',
        case='revAA_heel_relief2',J_motor_kg_m2=Jm,J_provisional_load_kg_m2=Jd,inventory=inventory,spring_Nm_rad=spring,
        applied_motor_torque_Nm=torque,opposing_drum_torque_Nm=-torque,omega_rad_s=omega,duration_s=duration,
        records=records,time_refinement_relative=convergence,
        physical_mass_qualified=False,
        omitted=['pin/fastener/inner-race inertia','actual coupling contact/compliance','bearing friction','wire compliance','real motor torque curve','material density/lot tolerance'],
        density_basis={'6061':'Nominal2.70 g/cm3 Aluminum Association Teal Sheets; not lot certificate','303':'Carpenter typical7.83 g/cm3'},
        sources=['https://www.aluminum.org/sites/default/files/2026-01/Teal%20Sheets%20December%202025.pdf','https://www.carpentertechnology.com/hubfs/7407324/Material%20Saftey%20Data%20Sheets/303.pdf','https://files.omc-stepperonline.com/17HS15-1504S1_Full_Datasheet.pdf'],
        source_SHA256=sha(Path(__file__)),geometry_SHA256=sha(geompath),compliance_SHA256=sha(compliancepath),
        trajectory_SHA256=sha(out/'trajectory.npz'),command='python scripts/torsion_dynamics.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
