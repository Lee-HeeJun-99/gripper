"""Bounded independent benchmark;never reported as a SOFA measurement."""
import csv
import json
import shutil
from curve_common import ROOT,OUT,sha,write_json
from closure_validation_suite import logged


def main():
    out=OUT/'independent_slip_band_v1';out.mkdir(exist_ok=False);paths=[ROOT/'tests/test_slip_band.cpp',ROOT/'models/contact_energy/SlipBandReference.h',ROOT/'models/integrated/Kernels.h'];write_json(out/'source_hashes.json',{str(p.relative_to(ROOT)):sha(p)for p in paths})
    for p in paths:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for stage,cmd in[('build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',paths[0],'-o',out/'benchmark.bin']),('run',[out/'benchmark.bin'])]:
        r=logged(cmd,out/stage,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=stage,process=r));return
    with(out/'run/stdout.log').open()as f:rows=[{k:float(v)for k,v in r.items()}for r in csv.DictReader(f)]
    write_json(out/'summary.json',dict(status='PASS',reference_scope='independent prescribed parabolic capacity/virgin scalar material,NOT actual SOFA or real PET. Split Gauss3/analytic energy tests pass;point-sampling FAILs remain below.',results=rows,point_sampling_failures_at_one_percent=sum(r['relative_D']>.01 for r in rows),root_cause_inference='demonstrates that small normal/traction error can coexist with aliased thin slip-band dissipation;does NOT prove every current 3D history error has this cause',production_contact_changed=False))
    print([(r['displacement'],r['h'],r['relative_D'],r['relative_force'])for r in rows if r['grid_shift']==0])


if __name__=='__main__':main()
