"""Targeted alternatives after coarse surface and normal-direction transient gates fail."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from stabilization_grasp import run
from stabilization_common import OUT,write_json

def main():
    cases=[('sphere_quad32',dict(samples=32)),('sphere_mesh21_q16',dict(nodes=21,samples=16)),('sphere_mesh21_q32',dict(nodes=21,samples=32)),
           ('sphere_z_long_damped',dict(axis=2,duration=18,hold_until=14,rayleigh_mass=2)),('sphere_z_negative_long_damped',dict(axis=2,load=-1e-6,duration=18,hold_until=14,rayleigh_mass=2))]
    rows={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(run,name,**parameters):name for name,parameters in cases}
        for future in as_completed(futures):
            name=futures[future]
            try:rows[name]=future.result()
            except Exception as e:rows[name]=dict(status='FAIL',failure_reason=repr(e),grasp_certified=False)
            write_json(OUT/'grasp/refinement_summary.json',rows)

if __name__=='__main__':main()
