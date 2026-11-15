"""Finite, two-child closure experiments; no objective values on failed gates."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from closure_trial import Config,run
from closure_common import OUT,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['convergence','wrenches','shapes','jamming','controls','preload']);p.add_argument('--workers',type=int,choices=[1,2],default=2);p.add_argument('--suffix',default='');args=p.parse_args();c=Config();cases=[]
    label=args.stage+('_'+args.suffix if args.suffix else '')
    if args.stage=='convergence':
        cases=[(f'n{n}q{q}',replace(c,nodes=n,samples=q)) for n in (11,21,41) for q in (8,16,32)]
        cases += [('repeat',c),('halfdt',replace(c,dt=.00025)),('history_half',replace(c,history_spacing=.005))]
    elif args.stage=='wrenches':
        cases=[(a+sign,replace(c,axis=i,load=(1e-6 if i<3 else 5e-6)*s,duration=24.)) for i,a in enumerate(('Fx','Fy','Fz','Tx','Ty','Tz')) for sign,s in [('plus',1),('minus',-1)]]
    elif args.stage=='shapes':
        cases=[(shape+'_'+a,replace(c,shape=j,axis=i,load=1e-6 if i<3 else 5e-6,duration=24.)) for j,shape in [(1,'cylinder'),(2,'box')] for i,a in [(0,'Fx'),(3,'Tx'),(5,'Tz')]]
    elif args.stage=='jamming':
        cases=[('p'+str(p)+'_f'+str(f),replace(c,pressure=p,load=f)) for p in (0.,.0001,.001,.01) for f in (1e-6,1e-5)]
    elif args.stage=='preload':
        write_json(OUT/(label+'_criteria.json'),dict(tensions=[.003,.01],torque=5e-6,axis='Tz',dt=.0005,duration=24,unchanged_limits=dict(angle=.01,force_moment_relative=1e-3,velocity=1e-5),scope='distinct physical preload designs, not baseline reclassification; planar layer domain.005 unchanged'))
        cases=[('Tz_T'+str(t),replace(c,tension=t,axis=5,load=5e-6,duration=24.)) for t in (.003,.01)]
    else:cases=[('mu0',replace(c,mu=0)),('mulow',replace(c,mu=.001)),('wireoff',replace(c,tension=0)),('badposition',replace(c,object_x=110)),('overload',replace(c,load=1e-5))]
    results={}
    with ThreadPoolExecutor(args.workers) as pool:
        pending={pool.submit(run,label+'_'+name.replace('.','p'),config,480):name for name,config in cases}
        for task in as_completed(pending):
            name=pending[task]
            try:results[name]=task.result()
            except Exception as e:results[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/(label+'.json'),results)
if __name__=='__main__':main()
