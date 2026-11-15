"""Finite additional campaign: at most3 simulation children, no automatic retries."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from grasp_common import OUT,write_json
from grasp_trial import Config,run

def main():
    c=replace(Config(),rayleigh_mass=2.)
    cases=[('sphere_repeat',c),('sphere_halfdt',replace(c,dt=.00025)),('sphere_q16',replace(c,samples=16)),('sphere_q32',replace(c,samples=32)),('sphere_n21q16',replace(c,nodes=21,samples=16)),('sphere_n21q32',replace(c,nodes=21,samples=32)),('sphere_n41q16',replace(c,nodes=41,samples=16)),
           ('mu_zero',replace(c,mu=0)),('mu_low',replace(c,mu=.001)),('pressure_off',replace(c,pressure=0)),('tendon_off',replace(c,tension=0)),('overload',replace(c,load=1e-5)),('sparse_contact',replace(c,samples=1)),('misplaced_object',replace(c,object_x=110)),('insufficient_wrap',replace(c,base_z=5.5)),
           ('cylinder_x',replace(c,shape=1)),('box_x',replace(c,shape=2)),('normal_k_half',replace(c,normal_k=.0005)),('normal_k_double',replace(c,normal_k=.002)),('object_offset',replace(c,object_x=94.5)),('object_radius',replace(c,object_radius=5.01))]
    rows={}
    with ThreadPoolExecutor(3) as pool:
        tasks={pool.submit(run,name,config):name for name,config in cases}
        for task in as_completed(tasks):
            name=tasks[task]
            try:rows[name]=task.result()
            except Exception as e:rows[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'remaining.json',rows)

if __name__=='__main__':main()
