"""Two bounded children maximum; failures never acquire objective values."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from grasp_common import OUT,write_json
from grasp_trial import Config,run

def main():
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['directions','directions_settled','controls','convergence','shapes']);args=parser.parse_args();c=Config() if args.stage=='directions' else replace(Config(),rayleigh_mass=2.);rows={}
    if args.stage in ('directions','directions_settled'):
        prefix='sphere_' if args.stage=='directions' else 'settled_sphere_'
        cases=[(prefix+a+sign,replace(c,axis=i,load=1e-6*s)) for i,a in enumerate('xyz') for sign,s in [('plus',1),('minus',-1)]]
    elif args.stage=='controls':cases=[('mu_zero',replace(c,mu=0)),('mu_low',replace(c,mu=.001)),('pressure_off',replace(c,pressure=0)),('tendon_off',replace(c,tension=0)),('overload',replace(c,load=1e-5)),('sparse_contact',replace(c,samples=1)),('misplaced_object',replace(c,object_x=110)),('insufficient_wrap',replace(c,base_z=5.5))]
    elif args.stage=='convergence':cases=[('sphere_repeat',c),('sphere_halfdt',replace(c,dt=.00025)),('sphere_q16',replace(c,samples=16)),('sphere_q32',replace(c,samples=32)),('sphere_n21q16',replace(c,nodes=21,samples=16)),('sphere_n21q32',replace(c,nodes=21,samples=32)),('sphere_n41q16',replace(c,nodes=41,samples=16))]
    else:cases=[('cylinder_x',replace(c,shape=1)),('box_x',replace(c,shape=2)),('normal_k_half',replace(c,normal_k=.0005)),('normal_k_double',replace(c,normal_k=.002)),('object_offset',replace(c,object_x=94.5)),('object_radius',replace(c,object_radius=5.01))]
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,name,config):name for name,config in cases}
        for task in as_completed(tasks):
            name=tasks[task]
            try:rows[name]=task.result()
            except Exception as e:rows[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/(args.stage+'.json'),rows)

if __name__=='__main__':main()
