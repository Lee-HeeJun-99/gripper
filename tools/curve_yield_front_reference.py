"""Independent stateful scalar yield-front reference;not a SOFA3D replacement."""
import json
import shutil
from curve_common import ROOT,OUT,sha,write_json
from closure_validation_suite import logged


def main():
    out=OUT/'yield_front_history_v1';out.mkdir(exist_ok=False)
    paths=[ROOT/'tests/test_yield_front_history.cpp',ROOT/'models/yield_front_history/ScalarField.h',ROOT/'models/contact_energy/SlipBandReference.h']
    write_json(out/'sources.json',{str(p.relative_to(ROOT)):sha(p)for p in paths})
    for p in paths:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for name,cmd in [('build',['g++','-std=c++17','-O2','-ffp-contract=off','-Wall','-Wextra','-Wpedantic',paths[0],'-o',out/'yield_front.bin']),('unit',[out/'yield_front.bin'])]:
        process=logged(cmd,out/name,180)
        if process['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=process));return
    text=(out/'unit/stdout.log').read_text();markers=[json.loads(line[len('YIELD_FRONT '):])for line in text.splitlines()if line.startswith('YIELD_FRONT ')]
    if len(markers)!=1:raise ValueError('actual reference result marker missing')
    write_json(out/'summary.json',dict(status='PASS',measurements=markers[0],scope='independent fixed-domain/fixed-normal1Dpiecewise quadratic material-history reference. Exact smooth-branch integration and stateful Coulomb return,NOT3Dobjectivity,birth/death,moving-contact,SOFAintegration or grasp certification.',sofa_integration='NOT RUN'))
    print(markers[0])


if __name__=='__main__':main()
