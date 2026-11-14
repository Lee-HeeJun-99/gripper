"""Uncalibrated +/-10% one-at-a-time EB proxy sensitivity, NOT SOFA measurements."""
import csv
from dataclasses import replace,asdict
from integrated_common import OUT,write_json,provenance
from models.multilayer.beam import Design,solve

def main():
    out=OUT/'sensitivity';out.mkdir(parents=True,exist_ok=False)
    base=Design(nodes=11,layers=4,connectors=tuple(range(1,11)),coupling=100)
    rows=[]
    for variable in ('young','area','inertia','thickness','coupling'):
        for factor in (.9,1.,1.1):
            d=replace(base,**{variable:getattr(base,variable)*factor});on=solve(d);off=solve(replace(d,coupling=0))
            if not on['small_rotation_validated'] or on['normalized_residual']>=1e-6:raise RuntimeError('invalid proxy sensitivity')
            rows.append(dict(variable=variable,factor=factor,off_tip_mm=off['deflection_mm'],on_tip_mm=on['deflection_mm'],stiffness_ratio=off['deflection_mm']/on['deflection_mm'],max_nodal_slip_mm=on['max_interface_slip_mm']))
    with (out/'sensitivity.csv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
    write_json(out/'summary.json',dict(provenance=provenance(),base=asdict(base),rows=rows,scope='independent EB FEM uncalibrated OAT +/-10% assumed uncertainty; not measured probability bounds; A/I varied independently to identify axial/bending sensitivities, not necessarily realizable geometry'))
    print('PASS',len(rows),'proxy sensitivity solves')

if __name__=='__main__':main()
