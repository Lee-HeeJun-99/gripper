"""NEW bounded sphere-history chart experiment;keeps vector v1 index immutable."""
import argparse
import json
import shutil
import subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);args=p.parse_args()
    if not args.tag.replace('_','').isalnum():raise ValueError('unique simple tag')
    out=ROOT/'results'/('vector_history_general_'+args.tag);out.mkdir(exist_ok=False)
    sources=list((ROOT/'models/yield_front_history').glob('*.h'))
    sources += [ROOT/name for name in ('models/conservative_beam/EnergyKernel.h','models/conservative_beam/AutoDiff.h','models/finite_rotation/Kernel.h','tests/test_sphere_history_chart.cpp','tools/curve_general_reference.py')]
    before={str(path.relative_to(ROOT)):sha(path)for path in sources}
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=before,scope='prescribed old Hermite geometry/sphere chart mathematics;NOT SOFA dynamic contact'))
    for path in sources:
        target=out/'sources'/path.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    binary=out/'chart.bin';stages={}
    stages['build']=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-Wall','-Wextra','-Wpedantic','-Werror',ROOT/'tests/test_sphere_history_chart.cpp','-o',binary],out/'build',120)
    if not stages['build']['exit_code']:
        if before!={str(path.relative_to(ROOT)):sha(path)for path in sources}:raise ValueError('source changed during compilation')
        stages['chart']=logged([binary],out/'chart',180);stages['chart']['binary_sha256']=sha(binary)
    result=dict(status='PASS'if all(s['exit_code']==0 for s in stages.values())else'FAIL',stages=stages,sofa_adapter='NOT RUN',grasp='NOT RUN');write_json(out/'summary.json',result);print(json.dumps(dict(out=str(out),status=result['status'])))

if __name__=='__main__':main()
