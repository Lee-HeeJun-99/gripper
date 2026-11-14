"""Finite 2-worker campaign; each child <=4GiB/180s, immutable output per trial."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from stabilization_common import OUT,write_json
from stabilization_grasp import run

def main():
    cases=[('sphere_x_negative',dict(axis=0,load=-1e-6)),('sphere_y_positive',dict(axis=1)),('sphere_y_negative',dict(axis=1,load=-1e-6)),
           ('sphere_z_positive',dict(axis=2)),('sphere_z_negative',dict(axis=2,load=-1e-6)),
           ('sphere_repeat',{}),('sphere_halfdt',dict(dt=.00025)),('sphere_mesh',dict(nodes=21)),('sphere_quadrature',dict(samples=16)),
           ('sphere_mu_zero',dict(mu=0)),('sphere_overload',dict(load=4e-6)),('cylinder_x',dict(shape=1)),('box_x',dict(shape=2))]
    records={}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures={pool.submit(run,name,**parameters):name for name,parameters in cases}
        for future in as_completed(futures):
            name=futures[future]
            try:records[name]=future.result()
            except Exception as e:records[name]=dict(status='FAIL',failure_reason=repr(e),grasp_certified=False)
            write_json(OUT/'grasp/suite_summary.json',dict(max_workers=2,records=records,grasp_certified=False))

if __name__=='__main__':main()
