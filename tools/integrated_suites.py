"""Run finite, bounded, model-labelled suites and retain every failed experiment."""
import argparse
import csv
import json
from dataclasses import replace
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from integrated_trial import Config,run,geometry
from integrated_common import ROOT,OUT,write_json,sha,provenance
from models.multilayer.beam import Design,solve,assemble
import numpy as np

def reference(c):
    _,A,I,h=geometry(c)
    return solve(Design(length=c.length,layers=c.layers,nodes=c.nodes,thickness=h,area=A,inertia=I,
        load=c.load,coupling=c.k,connectors=tuple(c.connectors) or tuple(range(1,c.nodes))))

def execute(phase,cases):
    directory=OUT/phase;directory.mkdir(parents=True,exist_ok=False);records={};checks={}
    for name,c in cases:
        r=run(directory/name,c);records[name]=r;checks[name+'_execution']=r['execution_completed']
        if c.kind=='equilibrium':checks[name+'_equilibrium']=r['status']=='PASS'
        if phase=='multilayer' and r['status']=='PASS':
            ref=reference(c);error=abs(r['tip_deflection_mm']/ref['deflection_mm']-1)
            r['reference']=dict(deflection_mm=ref['deflection_mm'],relative_difference=error,method='independent linear EB FEM; same A/I/connector positions')
            checks[name+'_FEM']=error<.005;checks[name+'_force_balance']=abs(r['reaction_z']/c.load-1)<1e-3
            checks[name+'_moment_balance']=abs(r['reaction_y']+c.length*c.load)/(c.load*c.length)<1e-3
        if phase=='tendon' and name=='small_tension' and r['status']=='PASS':
            exact=c.cable_tension*abs(c.cable_offset)*c.length**2/(2*c.layers*250*geometry(c)[2]);checks['small_tension_EB_limit']=abs(r['tip_deflection_mm']/exact-1)<.005
        write_json(directory/'summary.json',dict(provenance=provenance(),checks=checks,records=records,all_current_checks_passed=all(checks.values())))
    if phase=='multilayer':
        for layers in (4,8):
            base=records[f'L{layers}_k100'];
            for suffix,tol in [('mesh',.01),('halfdt',.001)]+([('repeat',1e-10),('extended',.001)] if layers==8 else []):
                r=records[f'L{layers}_{suffix}'];checks[f'L{layers}_{suffix}_convergence']=r['status']==base['status']=='PASS' and abs(r['tip_deflection_mm']/base['tip_deflection_mm']-1)<tol
        for layers in (2,4,8):
            vals=[records[f'L{layers}_k{k}'] for k in (0,1,100)]
            checks[f'L{layers}_monotone']=all(v['status']=='PASS' for v in vals) and vals[0]['tip_deflection_mm']>vals[1]['tip_deflection_mm']>vals[2]['tip_deflection_mm']
    if phase in ('tendon','friction','contact'):
        for name,r in records.items():
            if r['execution_completed']:
                with (directory/name/'state.txt.csv').open() as stream:series=list(csv.DictReader(stream))
                diss=[float(v['friction_dissipation']) for v in series]
                checks[name+'_nonnegative_dissipation']=min(diss)>=-1e-15 and all(b>=a-1e-15 for a,b in zip(diss,diss[1:]))
                r['component_metrics']=series[-1]
                if phase=='contact' and name!='free_object_negative_control':checks[name+'_contact_detected']=max(float(v['contact_count']) for v in series)>0
    write_json(directory/'summary.json',dict(provenance=provenance(),checks=checks,records=records,all_current_checks_passed=all(checks.values())))
    print(phase,'checks',sum(checks.values()),'/',len(checks),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['multilayer','tendon','friction','contact']);a=p.parse_args();d=Config()
    if a.phase=='multilayer':
        cases=[(f'L{L}_k{k}',replace(d,layers=L,k=k)) for L in (2,4,8) for k in (0,1,100)]
        for L in (4,8):cases += [(f'L{L}_mesh',replace(d,layers=L,k=100,nodes=21,connectors=tuple(range(2,21,2)))),(f'L{L}_halfdt',replace(d,layers=L,k=100,dt=.00025))]
        cases += [('L8_repeat',replace(d,layers=8,k=100)),('L8_extended',replace(d,layers=8,k=100,duration=18))]
        cases += [(f'equal_material_L{L}_k{k}',replace(d,layers=L,k=k,equal_total_material=True,duration=18)) for L in (4,8) for k in (0,100)]
    elif a.phase=='tendon':
        d=replace(d,k=0,load=0,normal_k=.001)
        cases=[('zero',d),('small_tension',replace(d,cable_tension=1e-6)),('tension_1e5',replace(d,cable_tension=1e-5)),('tension_1e4',replace(d,cable_tension=1e-4)),
            ('length_control',replace(d,cable_k=.01,shortening=.0001)),('release',replace(d,kind='transient',duration=18,cable_times=(0,1,8),cable_values=(0,1e-5/2,0)))]
    elif a.phase=='friction':
        d=replace(d,mode=1,k=1)
        cases=[('off',replace(d,pressure=0)),('low',replace(d,pressure=1e-9)),('high',replace(d,pressure=1e-3)),
            ('mu_low',replace(d,pressure=1e-8,mu=.1)),('mu_high',replace(d,pressure=1e-8,mu=.6)),
            ('on_off_cycle',replace(d,kind='transient',duration=30,pressure_times=(0,6,18,24),pressure_values=(0,1e-8,0,1e-8),load_times=(0,12,24),load_values=(-1e-6,0,-1e-6))),
            ('wire_jamming',replace(d,normal_k=.001,load=0,cable_tension=1e-5,pressure=1e-8))]
    else:
        d=replace(d,mode=1,k=1,pressure=1e-8,cable_tension=1e-5,normal_k=.001,object_x=100,object_z=-5.305)
        cases=[('sphere',replace(d,object_shape=0)),('cylinder',replace(d,object_shape=1)),('box',replace(d,object_shape=2)),
            ('free_object_negative_control',replace(d,object_shape=0,object_fixed=False,object_load=1e-7,kind='transient',duration=6))]
    execute(a.phase,cases)

if __name__=='__main__':main()
