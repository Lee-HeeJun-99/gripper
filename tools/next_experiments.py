"""Bounded staged new-model experiments; each phase owns a fresh output folder."""
import argparse
import csv
from dataclasses import replace
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verification_common import ROOT,sha,write_json,provenance
from research_trial import run,model_hashes
from models.multilayer.beam import Design,solve,friction_path
from next_common import NEXT

OUT=NEXT

def static():
    directory=OUT/'static';directory.mkdir(parents=True,exist_ok=False)
    d=Design();rows=[]
    for L in (30.,60.,100.):
        for layers in (1,2,4,8):
            for k in (0.,1.,100.):
                design=replace(d,length=L,layers=layers,coupling=k);r=solve(design);r.pop('displacement')
                rows.append(dict(case=f'L{L}_layers{layers}_k{k}',**r))
    for name,design in [('wire',replace(d,wire_tension=1e-5,wire_eccentricity=.1)),
                        ('contact',replace(d,contact_gap=.005,contact_stiffness=.1)),
                        ('timoshenko',replace(d,timoshenko=True))]:
        r=solve(design);r.pop('displacement');rows.append(dict(case=name,**r))
    sensitivity=[]
    base=solve(d)
    for field in ('length','thickness','young','area','inertia','coupling','load'):
        for factor in (.8,1.2):
            r=solve(replace(d,**{field:getattr(d,field)*factor}));sensitivity.append(dict(parameter=field,factor=factor,
                tip_mm=r['deflection_mm'],relative_change=r['deflection_mm']/base['deflection_mm']-1,
                log_elasticity=__import__('math').log(r['deflection_mm']/base['deflection_mm'])/__import__('math').log(factor)))
    # Geometry-consistent film thickness variation changes A, I and layer spacing together.
    film=[]
    for factor in (.8,1.,1.2):
        design=replace(d,thickness=d.thickness*factor,area=d.area*factor,inertia=d.inertia*factor**3)
        r=solve(design);r.pop('displacement');film.append(dict(thickness_factor=factor,**r))
    loads=[i*1e-7 for i in range(21)]+[i*1e-7 for i in range(19,-21,-1)]+[i*1e-7 for i in range(-19,1)]
    pressure={str(p):friction_path(d,loads,p,.3,8) for p in (0.,1e-9,1e-8,1e-6)}
    grid=[]
    # Distinct, explicitly deterministic enumeration, not Optuna.
    for k in (.01,.1,1.,10.,100.):
        for positions in ((10,20),(4,8,12,16,20),tuple(range(2,21,2)),tuple(range(1,21))):
            on=solve(replace(d,coupling=k,connectors=positions));off=solve(replace(d,coupling=0))
            grid.append(dict(k=k,connectors=positions,ratio=off['deflection_mm']/on['deflection_mm'],slip=on['max_interface_slip_mm'],
                valid=on['small_rotation_validated'] and on['normalized_residual']<1e-6))
    pareto=[r for r in grid if r['valid'] and not any(s['valid'] and s['ratio']>=r['ratio'] and s['slip']<=r['slip'] and (s['ratio']>r['ratio'] or s['slip']<r['slip']) for s in grid)]
    write_json(directory/'summary.json',dict(provenance=provenance(),model_hashes=model_hashes(),
        scope='Independent linear static FEM and prescribed-pressure slider research; not SOFA optimization or real PET',
        cases=rows,sensitivity=sensitivity,geometry_consistent_thickness=film,pressure_cycles=pressure,
        search_method='deterministic 20-point static FEM enumeration, NOT Optuna',search=grid,pareto=pareto))
    with (directory/'summary.csv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=['case','deflection_mm','max_connector_slip_mm','max_rotation_rad','normalized_residual','contact_reaction'])
        writer.writeheader();writer.writerows({k:r[k] for k in writer.fieldnames} for r in rows)
    print('static',len(rows),'cases;',len(grid),'enumeration;',len(pareto),'Pareto')

def sofa():
    directory=OUT/'sofa';directory.mkdir(parents=True,exist_ok=False)
    cases=[('L30_free',dict(length=30,k=0,duration=6)),('L100_free',dict(k=0,duration=12)),
        ('L100_on',dict(k=100,duration=12)),('L100_repeat',dict(k=100,duration=12)),
        ('L100_halfdt',dict(k=100,dt=.00025,duration=12)),('L100_mesh',dict(k=100,n=21,connectors=list(range(2,21,2)),duration=12)),
        ('L100_extended',dict(k=100,duration=18)),
        ('finite_L30',dict(length=30,k=1,load=1e-4,duration=3,finite=True)),
        ('finite_L30_halfdt',dict(length=30,k=1,load=1e-4,dt=.00025,duration=3,finite=True)),
        ('finite_L30_mesh',dict(length=30,k=1,n=21,connectors=list(range(2,21,2)),load=1e-4,duration=3,finite=True))]
    records={}
    for name,kw in cases:
        records[name]=run(directory/name,**kw)
        write_json(directory/'summary.json',records)
    checks={name:r['status']=='PASS' for name,r in records.items()}
    if checks['L30_free'] and checks['L100_free']:
        ratio=records['L100_free']['tip_deflection_mm']/records['L30_free']['tip_deflection_mm']
        checks['length_cubic_scaling']=abs(ratio/(100/30)**3-1)<.005
    for key,tol in [('L100_repeat',1e-10),('L100_halfdt',.001),('L100_extended',.001),('L100_mesh',.01)]:
        if checks[key] and checks['L100_on']:checks[key+'_convergence']=abs(records[key]['tip_deflection_mm']/records['L100_on']['tip_deflection_mm']-1)<tol
    for key,tol in [('finite_L30_halfdt',.001),('finite_L30_mesh',.01)]:
        if checks[key] and checks['finite_L30']:checks[key+'_convergence']=abs(records[key]['tip_deflection_mm']/records['finite_L30']['tip_deflection_mm']-1)<tol
    write_json(directory/'gate.json',dict(checks=checks,scope='experimental extension; mesh uses identical physical connector positions',
        passed=all(checks.values())))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['static','sofa']);p.add_argument('--out',type=Path,default=OUT);a=p.parse_args();OUT=a.out;globals()[a.phase]()
