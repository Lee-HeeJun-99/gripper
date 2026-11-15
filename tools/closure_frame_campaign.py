"""Finite3-finger research validation, not Optuna or a fabricated objective."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from closure_frame_trial import Config,run
from closure_frame_common import OUT,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['wrenches','convergence','controls']);p.add_argument('--workers',type=int,choices=[1,2,3,4],default=2);args=p.parse_args();c=Config(duration=24.);cases=[]
    if args.stage=='wrenches':cases=[(a+sign,replace(c,axis=i,load=(1e-6 if i<3 else 5e-6)*s)) for i,a in enumerate(('Fx','Fy','Fz','Tx','Ty','Tz')) for sign,s in [('plus',1),('minus',-1)]]
    elif args.stage=='convergence':
        c=replace(c,axis=5,load=5e-6,duration=18.)
        cases=[(f'n{n}q{q}',replace(c,nodes=n,samples=q)) for n in (11,21,41) for q in (8,16,32)]
        cases+=[('repeat',c),('halfdt',replace(c,dt=.00025)),('history_half',replace(c,history_spacing=.005))]
    else:cases=[('mu0_Fy',replace(c,axis=1,mu=0)),('low_mu_Fy',replace(c,axis=1,mu=.001)),('wireoff_Fy',replace(c,axis=1,tension=0)),('overload_Fy',replace(c,axis=1,load=1e-5))]
    results={};OUT.mkdir(parents=True,exist_ok=True);write_json(OUT/(args.stage+'_plan.json'),dict(physical_design='three100mm fingers/equal120deg/per-finger properties unchanged/totalmaterial+50%',cases=[dict(name=n,config=vars(cfg)) for n,cfg in cases],maximum_children=args.workers,maximum_wall_per_child=480,grasp_certified=False))
    with ThreadPoolExecutor(args.workers) as pool:
        pending={pool.submit(run,args.stage+'_'+n,cfg,480):n for n,cfg in cases}
        for task in as_completed(pending):
            n=pending[task]
            try:results[n]=task.result()
            except Exception as e:results[n]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/(args.stage+'.json'),results)
if __name__=='__main__':main()
