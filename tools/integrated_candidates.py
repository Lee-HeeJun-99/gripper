"""Independently validate every preliminary Hermite-metric proxy Pareto candidate.

dt, original connector positions/count, repeated equilibrium and +6s extension.
This is deterministic static-proxy candidate validation, never Optuna/grasp output.
"""
from dataclasses import replace
import json
import sys
from integrated_trial import Config,run
from integrated_common import OUT,write_json,sha,provenance
from integrated_slip import interior_slip
from integrated_integrity import verify_trial
from trial_validation import read_states

def metric(directory):
    r=verify_trial(directory);c=r['config'];return interior_slip(read_states(directory/'state.txt')[-1]['X'],c['layers'],c['nodes'],c['length'],c['height'])['max_reconstructed_slip_mm']

def main():
    study=json.loads((OUT/'search_hermite/summary.json').read_text());out=OUT/'candidate_validation';out.mkdir(parents=True,exist_ok=False);rows=[]
    for candidate in study['pareto']:
        p=candidate['config'];key=candidate['design_sha256'][:12];target=out/key;target.mkdir();base=Config(layers=p['layers'],k=p['k'],connectors=tuple(p['connectors']))
        cases=[('base',base),('repeat',base),('halfdt',replace(base,dt=.00025)),('mesh',replace(base,nodes=21,connectors=tuple(2*i for i in base.connectors))),('extended',replace(base,duration=18))]
        records={};slips={}
        for name,c in cases:
            records[name]=run(target/name,c)
            if records[name]['status']=='PASS':slips[name]=metric(target/name)
            write_json(target/'summary.json',dict(records=records,reconstructed_slip=slips))
        checks={name:r['status']=='PASS' for name,r in records.items()}
        for name,tol in [('repeat',1e-10),('halfdt',.001),('mesh',.01),('extended',.001)]:
            checks[name+'_tip']=checks[name] and checks['base'] and abs(records[name]['tip_deflection_mm']/records['base']['tip_deflection_mm']-1)<tol
            checks[name+'_slip']=name in slips and 'base' in slips and abs(slips[name]-slips['base'])<1e-10+tol*abs(slips['base'])
        off=verify_trial(OUT/'multilayer'/f'L{p["layers"]}_k0')
        ratio=off['tip_deflection_mm']/records['base']['tip_deflection_mm'] if checks['base'] else None
        row=dict(design=candidate,checks=checks,approved_for_scope=all(checks.values()),actual_SOFA_stiffness_ratio=ratio,actual_reconstructed_slip=slips.get('base'),
            actual_nodal_slip=records['base'].get('max_interface_slip_mm'),scope='static small-planar spring-coupling research, not vacuum or grasp optimum')
        rows.append(row);write_json(target/'decision.json',row);write_json(out/'summary.json',dict(provenance=provenance(),study_sha256=sha(OUT/'search_hermite/summary.json'),candidates=rows))
        print(key,'approved',row['approved_for_scope'],flush=True)

if __name__=='__main__':main()
