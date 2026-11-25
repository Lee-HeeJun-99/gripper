"""Read actual endpoint constraint rows and multiplier from1795; no rerun.
Force/impulse/instantaneous power scope only, not global energy closure.
"""
import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/open_parallel_cable1795'
    row=list(csv.DictReader((src/'cable.csv').open()))[0]
    solver=list(csv.DictReader((src/'constraints.csv').open()))[0]
    actual=[]
    for item in row['child_J'].split(';'):
        if not item:continue
        rid,pid,vector=item.split(':');assert int(rid)==0
        actual.append((int(pid),np.fromstring(vector,sep=' ')))
    actual.sort();assert [k for k,_ in actual]==[0,1]
    J=np.array([v for _,v in actual]);lam=np.fromstring(solver['impulses_Ns'],sep=' ');assert len(lam)==1
    dt=.001;F=J*lam[0]/dt;initial=np.array([[0,0,0],[.005,.0015,0]])
    force=F.sum(0);moment=np.cross(initial,F).sum(0)
    expected=(initial[1]-initial[0]);expected/=np.linalg.norm(expected)
    row_error=float(abs(J-np.array([expected,-expected])).max())
    vc=np.fromstring(row['child_v'],sep=' ').reshape(2,3)
    b=list(csv.DictReader((src/'base.csv').open()))[0];body=list(csv.DictReader((src/'body.csv').open()))[0]
    vb=np.fromstring(b['rigid_v'],sep=' ');vr=np.fromstring(body['rigid_v'],sep=' ').reshape(-1,6)
    generalized=np.r_[force,moment,F[1]@np.array([0,.005,0])]
    v=np.r_[vb,vr[1,5]-vb[5]]
    endpoint_power=float(np.sum(F*vc));generalized_power=float(generalized@v)
    residual=abs(endpoint_power-generalized_power)
    valid=row_error<=1e-12 and abs(force).max()<=1e-12 and abs(moment).max()<=1e-12 and residual<=1e-12
    d=dict(status='PASS_ENDPOINT_ROW_WRENCH_SCOPE_ONLY' if valid else 'FAIL_ENDPOINT_ROW_WRENCH',
        actual_endpoint_J=J.tolist(),actual_multiplier_Ns=float(lam[0]),actual_endpoint_force_N=F.tolist(),
        previous_geometry_net_force_N=force.tolist(),previous_geometry_net_moment_Nm=moment.tolist(),
        endpoint_J_error=row_error,endpoint_instantaneous_power_W=endpoint_power,
        frozen_geometry_generalized_power_W=generalized_power,power_pullback_residual_W=residual,
        cable_work_J=None,global_energy_balance_J=None,
        inputs=[dict(path=str(p.relative_to(BASE.parent)),sha256=sha(p)) for p in [Path(__file__),src/'cable.csv',src/'constraints.csv',src/'base.csv',src/'body.csv',src/'scene.scn']],
        scope='Actual Native child Vec3 endpoint rows + actual solver impulse/dt, not command treated as measurement. Previous accepted initial geometry used for its assembled row; accepted velocities only for instantaneous power consistency. parent_J here is also Vec3, NOT a complete global Rigid3 Guide reaction/mass observation. All1step, no integrated work/global energy, wire friction, joint or grasp qualification.')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='inputs'},indent=2))

if __name__=='__main__':main()
