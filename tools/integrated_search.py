"""SQLite deterministic proxy search, explicitly NOT Optuna or grasp optimization.

Keep original two performance objectives and report an additional complexity cost.
Only same-area/inertia static proxies checked against actual SOFA are eligible.
"""
import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import random
import sqlite3
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from models.multilayer.beam import Design,solve,assemble
from integrated_common import OUT,ROOT,sha,write_json,provenance
from integrated_integrity import verify_trial

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=OUT/'deterministic_search');p.add_argument('--limit',type=int,default=90);p.add_argument('--inject-failure',action='store_true');p.add_argument('--delay-after-running',type=float,default=0,help='bounded fault-injection hook, seconds');a=p.parse_args()
    if a.limit<1:raise ValueError('positive bounded limit required')
    if not 0<=a.delay_after_running<=2:raise ValueError('fault delay resource bound')
    gate=json.loads((OUT/'multilayer/summary.json').read_text());eligible=[]
    for L in (2,4,8):
        if all(gate['checks'].get(f'L{L}_k{k}_equilibrium') and gate['checks'].get(f'L{L}_k{k}_FEM') for k in (0,1,100)):
            if L>=4 and not all(gate['checks'].get(f'L{L}_{kind}_convergence') for kind in ('mesh','halfdt')):continue
            if L==2:
                extra=json.loads((OUT/'additional_convergence/summary.json').read_text());base=gate['records']['L2_k100']
                if any(r['status']!='PASS' for r in extra.values()):continue
                if abs(extra['L2_mesh']['tip_deflection_mm']/base['tip_deflection_mm']-1)>=.01 or abs(extra['L2_halfdt']['tip_deflection_mm']/base['tip_deflection_mm']-1)>=.001:continue
            for k in (0,1,100):verify_trial(OUT/'multilayer'/f'L{L}_k{k}')
            eligible.append(L)
    if not eligible:raise RuntimeError('no SOFA-validated proxy family')
    patterns=[(5,10),(2,4,6,8,10),tuple(range(1,11))]
    grid=[dict(layers=L,k=k,connectors=c,equal_material=equal) for L in eligible for k in (.01,.1,1.,10.,100.) for c in patterns for equal in (False,True)]
    grid=[c for c in grid if not (c['layers']==2 and c['equal_material'])] # identical physical design, not another trial
    # Equal-material proxies require their own corresponding SOFA family gate.
    grid=[c for c in grid if not c['equal_material'] or c['layers']==2 or all(gate['checks'].get(f'equal_material_L{c["layers"]}_k{k}_equilibrium') and gate['checks'].get(f'equal_material_L{c["layers"]}_k{k}_FEM') for k in (0,100))]
    random.Random(11).shuffle(grid)
    identity=dict(method='deterministic_static_FEM_grid_NOT_OPTUNA',seed=11,source=sha(__file__),fem_source=sha(ROOT/'models/multilayer/beam.py'),grid_sha256=digest(grid),
        reference_binary_sha256=gate['records']['L2_k100']['binary_sha256'])
    a.out.mkdir(parents=True,exist_ok=True);db=sqlite3.connect(a.out/'research_grid.sqlite3',timeout=10)
    db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS trials (design TEXT PRIMARY KEY, config TEXT NOT NULL, status TEXT NOT NULL, result TEXT, result_hash TEXT, runtime REAL)')
    old=db.execute('SELECT value FROM metadata WHERE key="identity"').fetchone()
    if old and json.loads(old[0])!=identity:raise RuntimeError('study identity mismatch')
    db.execute('INSERT OR IGNORE INTO metadata VALUES (?,?)',('identity',json.dumps(identity,sort_keys=True)))
    db.execute('UPDATE trials SET status="interrupted" WHERE status="running"');db.commit()
    for config in ([dict(layers=2,k=-1.,connectors=(5,10),equal_material=False,injected_failure=True)] if a.inject_failure else [])+grid:
        key=digest(config);db.execute('INSERT OR IGNORE INTO trials (design,config,status) VALUES (?,?,?)',(key,json.dumps(config,sort_keys=True),'pending'))
    db.commit();attempted=0
    ordered=([dict(layers=2,k=-1.,connectors=(5,10),equal_material=False,injected_failure=True)] if a.inject_failure else [])+grid
    for config in ordered:
        key=digest(config);status=db.execute('SELECT status FROM trials WHERE design=?',(key,)).fetchone()[0]
        if status in ('complete','failed'):continue
        if attempted>=a.limit and not config.get('injected_failure'):break
        db.execute('UPDATE trials SET status="running" WHERE design=?',(key,));db.commit();started=time.monotonic()
        if a.delay_after_running:time.sleep(a.delay_after_running)
        try:
            L=config['layers'];ratio=math.sqrt(2/L) if config['equal_material'] else 1.;I=8*.4**3/12*ratio**4;A=.7322329862910148*ratio**2
            d=Design(nodes=11,layers=L,connectors=tuple(config['connectors']),coupling=config['k'],area=A,inertia=I,thickness=.4*ratio)
            on=solve(d);off=solve(replace(d,coupling=0))
            if not on['small_rotation_validated'] or on['normalized_residual']>=1e-6:raise ValueError('invalid static physics')
            K,f,B,free,tips=assemble(d);K+=d.coupling*B.T@B
            result=dict(stiffness_ratio=off['deflection_mm']/on['deflection_mm'],max_interface_slip_mm=on['max_interface_slip_mm'],
                complexity=(L-1)*len(d.connectors),material_volume_mm3=L*A*d.length,
                off_tip_mm=off['deflection_mm'],on_tip_mm=on['deflection_mm'],normalized_residual=on['normalized_residual'],
                condition_number_raw_mm_rad=float(np.linalg.cond(K[np.ix_(free,free)])),
                condition_number_scope='raw mixed mm/rad coordinates; NOT a dimensionless physical stability certificate')
            state='complete'
        except (ValueError,RuntimeError,np.linalg.LinAlgError) as e:result=dict(reason=str(e),objective_values=None);state='failed'
        db.execute('UPDATE trials SET status=?,result=?,result_hash=?,runtime=? WHERE design=?',(state,json.dumps(result,sort_keys=True),digest(result),time.monotonic()-started,key));db.commit()
        if not config.get('injected_failure'):attempted+=1
    rows=[]
    for key,config,status,result,result_hash,runtime in db.execute('SELECT design,config,status,result,result_hash,runtime FROM trials ORDER BY design'):
        r=json.loads(result) if result else None
        if r is not None and digest(r)!=result_hash:raise RuntimeError('damaged study metric hash')
        rows.append(dict(design_sha256=key,config=json.loads(config),status=status,metrics=r,runtime_s=runtime))
    valid=[r for r in rows if r['status']=='complete']
    def dominates(a,b):
        x,y=a['metrics'],b['metrics'];return x['stiffness_ratio']>=y['stiffness_ratio'] and x['max_interface_slip_mm']<=y['max_interface_slip_mm'] and x['complexity']<=y['complexity'] and (x['stiffness_ratio']>y['stiffness_ratio'] or x['max_interface_slip_mm']<y['max_interface_slip_mm'] or x['complexity']<y['complexity'])
    pareto=[r for r in valid if not any(dominates(s,r) for s in valid)]
    write_json(a.out/'summary.json',dict(identity=identity,provenance=provenance(),eligible_layer_families=eligible,grid_count=len(grid),complete=len(valid),failed=sum(r['status']=='failed' for r in rows),pending=sum(r['status'] in ('pending','interrupted') for r in rows),
        trials=rows,pareto=pareto,claim='preliminary deterministic static-FEM proxy front, NOT Optuna and NOT validated grasp optimization',global_optimum_claimed=False))
    db.close();print('Deterministic FEM complete',len(valid),'failed',sum(r['status']=='failed' for r in rows),'Pareto',len(pareto))

if __name__=='__main__':main()
