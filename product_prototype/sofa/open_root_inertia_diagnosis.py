"""Read-only orientation-factor diagnosis; never reclassifies original FAILs."""
import argparse,json
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from open_parallel_free_root import mass_reference
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
    for case in a.cases:
        src=BASE/'results'/case/'summary.json';d=json.loads(src.read_text())
        theta=d['initial_joint_angle_rad'];R=Rotation.from_euler('xyz',d['initial_root_euler_deg'],degrees=True).as_matrix()
        physical=mass_reference(theta,R);fixed=mass_reference(theta,R,world_fixed_inertia=True)
        errors=[[],[]]
        for r in d['records']:
            v=np.array(r['actual_generalized_velocity']);f=np.array(r['load'])*d['dt_s']
            for j,M in enumerate((physical,fixed)):errors[j].append(float(abs(v-np.linalg.solve(M,f)).max()))
        records.append(dict(case=case,input_sha256=sha(src),original_status=d['status'],
            physical_body_rotated_inertia_velocity_error=max(errors[0]),
            installed_world_fixed_inertia_velocity_error=max(errors[1])))
    header=Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Mass/sofa/component/mass/UniformMass.inl')
    functor=header.parent/'AddMToMatrixFunctor.h'
    d=dict(status='DIAGNOSTIC_WORLD_FIXED_ASSEMBLY_EXPLAINS_COLUMNS' if all(r['installed_world_fixed_inertia_velocity_error']<=1e-12 for r in records) else 'DIAGNOSIS_INCOMPLETE',
        records=records,source_sha256=sha(Path(__file__)),reference_source_sha256=sha(Path(__file__).parent/'open_parallel_free_root.py'),
        installed_headers=[dict(path=str(p),sha256=sha(p)) for p in (header,functor)],
        scope='Original1786/1787/1788physical orientation FAILs unchanged. Alternative world-fixed tensor reproduces installed UniformMass assembly contract, NOT physical anisotropic body inertia. Initial mass-only response, not a new ODE or correction. No Native replay/state edits. Existing general inertia work remains separate; this diagnoses the new articulated coupon configuration.')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))

if __name__=='__main__':main()
