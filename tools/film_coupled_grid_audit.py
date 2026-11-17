"""Measured grid reproduction,without replaying physical state."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True);p.add_argument('--case',required=True);a=p.parse_args();left=ROOT/'results'/('autonomous_film_'+a.source);right=ROOT/'results'/('autonomous_film_'+a.case)
    for folder in (left,right):
        if json.loads((folder/'summary.json').read_text())['status']!='PASS':raise ValueError('complete actual experiments required')
    meta=json.loads((right/'identity.json').read_text())
    if meta.get('grid_factor')!=1 or meta.get('frozen_grid')!=a.source:raise ValueError('factor1 reproduction required')
    l=list(csv.DictReader((left/'coupled.states.csv').open()));r=list(csv.DictReader((right/'coupled.states.csv').open()));physical=[k for k in l[0] if k not in ('time','force_time')];checks={k:len(l)==len(r) and all(x[k]==y[k] for x,y in zip(l,r)) for k in physical};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(l,r));valid=all(checks.values()) and clock<=64*np.finfo(float).eps*meta['duration']
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');write_json(out/'summary.json',dict(status='PASS' if valid else 'FAIL',scope='all physical columns exact on reconstructed grid;clock-only representational roundoff;NOT state replay/physics qualification',source=a.source,case=a.case,rows=len(l),checks=checks,maximum_clock_difference_s=clock,clock_bound_s=64*np.finfo(float).eps*meta['duration'],hashes={str(folder/name):sha(folder/name) for folder in (left,right) for name in ('identity.json','coupled.states.csv','summary.json')}));print(json.dumps(dict(status='PASS' if valid else 'FAIL',clock_error=clock,failed_columns=[k for k,v in checks.items() if not v])))
if __name__=='__main__':main()
