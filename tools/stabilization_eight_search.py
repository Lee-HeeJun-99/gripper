"""Separate static-Newton 8-layer EB proxy search; NOT Optuna/dynamic/grasp optimization."""
import json
import math
import random
import sqlite3
from dataclasses import replace
from models.multilayer.beam import Design,solve
from integrated_trial import Config
from integrated_slip import interior_slip
from integrated_search import digest
from stabilization_trials import run
from stabilization_common import ROOT,OUT,BUILD,sha,write_json
from trial_validation import read_states

def main():
    out=OUT/'eight_search';out.mkdir(parents=True,exist_ok=False)
    for name in ('L8_base','L8_halfdt','L8_quarterdt','L8_mesh','L8_repeat','L8_free'):
        directory=OUT/'static'/name;r=json.loads((directory/'metrics.json').read_text())
        if r['status']!='PASS' or r['binary_sha256']!=sha(BUILD/'plugin/libReGripStabilization.so'):raise RuntimeError('static family not eligible')
        for file,h in r['artifacts'].items():
            if sha(directory/file)!=h:raise RuntimeError('damaged gate artifact')
    extended=json.loads((OUT/'static_extras/extended18/metrics.json').read_text())
    if extended['status']!='PASS':raise RuntimeError('extended static gate failed')
    db=sqlite3.connect(out/'proxy.sqlite3');db.execute('CREATE TABLE trials (design TEXT PRIMARY KEY,config TEXT,status TEXT,result TEXT)')
    grid=[dict(k=k,points=p) for k in (.01,.1,1,10,100) for p in [(5,10),(2,4,6,8,10),tuple(range(1,11))]];random.Random(11).shuffle(grid);rows=[]
    for parameters in grid:
        key=digest(parameters);d=Design(layers=8,nodes=11,connectors=parameters['points'],coupling=parameters['k']);result=None
        try:
            on=solve(d);off=solve(replace(d,coupling=0))
            if not on['small_rotation_validated'] or on['normalized_residual']>=1e-6:raise ValueError('invalid static proxy')
            q=on['displacement'];x=[v for i in range(8*11) for v in (100*(i%11)/10+q[3*i],0,(i//11-3.5)*.4+q[3*i+1],0,math.sin(-q[3*i+2]/2),0,math.cos(q[3*i+2]/2))]
            result=dict(ratio=off['deflection_mm']/on['deflection_mm'],slip=interior_slip(x,8,11,100,.4)['max_reconstructed_slip_mm'],complexity=7*len(parameters['points']));status='complete'
        except (ValueError,RuntimeError) as e:status='failed';result=dict(objective_values=None,reason=str(e))
        db.execute('INSERT INTO trials VALUES (?,?,?,?)',(key,json.dumps(parameters),status,json.dumps(result)));db.commit();rows.append(dict(key=key,config=parameters,status=status,result=result))
    good=[r for r in rows if r['status']=='complete']
    def dominates(a,b):
        x,y=a['result'],b['result'];return x['ratio']>=y['ratio'] and x['slip']<=y['slip'] and x['complexity']<=y['complexity'] and x!=y
    front=[r for r in good if not any(dominates(s,r) for s in good)];write_json(out/'proxy_summary.json',dict(rows=rows,pareto=front,source_sha256=sha(__file__),fem_sha256=sha(ROOT/'models/multilayer/beam.py'),method='deterministic static FEM, not Optuna',seed=11))
    approved=[];off=json.loads((OUT/'static/L8_free/metrics.json').read_text())['tip_deflection_mm']
    for candidate in front:
        p=candidate['config'];c=Config(layers=8,k=p['k'],connectors=p['points'],duration=.15);records={}
        for name,config in [('base',c),('repeat',c),('halfdt',replace(c,dt=.00025)),('mesh',replace(c,nodes=21,connectors=tuple(2*i for i in c.connectors))),('extended',replace(c,duration=6.15))]:
            records[name]=run('eight_search/'+candidate['key'][:10]+'/'+name,config,static=True)
        checks={n:r['status']=='PASS' for n,r in records.items()}
        for name,tol in [('repeat',1e-10),('halfdt',.001),('mesh',.01),('extended',.001)]:checks[name+'_tip']=checks[name] and abs(records[name]['tip_deflection_mm']/records['base']['tip_deflection_mm']-1)<tol
        slips={}
        for name,r in records.items():
            if checks[name]:
                path=OUT/'eight_search'/candidate['key'][:10]/name/'state.txt';config=r['config'];slips[name]=interior_slip(read_states(path)[-1]['X'],8,config['nodes'],100,.4)['max_reconstructed_slip_mm']
        for name,tol in [('repeat',1e-10),('halfdt',.001),('mesh',.01),('extended',.001)]:checks[name+'_slip']=name in slips and abs(slips[name]-slips['base'])<1e-10+tol*abs(slips['base'])
        approved.append(dict(design=candidate,checks=checks,approved_for_static_scope=all(checks.values()),actual_ratio=off/records['base']['tip_deflection_mm'] if checks['base'] else None,actual_slip=slips.get('base')))
        write_json(out/'validation.json',dict(candidates=approved,scope='8-layer static Newton continuation only; original dynamic failures remain; NOT grasp/Optuna/global optimum'))
    db.close();print('proxy',len(good),'Pareto',len(front),'approved',sum(r['approved_for_static_scope'] for r in approved))

if __name__=='__main__':main()
