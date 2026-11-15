import argparse,json,shutil
from research_common import ROOT,OUT,sha,write_json
from closure_validation_suite import logged
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suffix',default='');args=parser.parse_args()
    out=OUT/('hermite_kernel'+args.suffix);out.mkdir(exist_ok=False);source=ROOT/'tests/test_hermite_map.cpp';header=ROOT/'models/contact_kinematics/HermiteMap.h';exe=ROOT/('build/autonomous_20261115_a01/test_hermite_map'+args.suffix)
    shutil.copy2(source,out/source.name);shutil.copy2(header,out/header.name)
    compile_result=logged(['g++','-O2','-std=c++17','-Wall','-Wextra','-Wpedantic',source,'-o',exe],out/'compile',120)
    if compile_result['exit_code']:raise RuntimeError('Hermite kernel compile')
    result=logged([exe],out/'run',60);lines=[json.loads(t[len('HERMITE '):])for t in(out/'run/stdout.log').read_text().splitlines()if t.startswith('HERMITE ')]
    sparse=[json.loads(t[len('SPARSE '):])for t in(out/'run/stdout.log').read_text().splitlines()if t.startswith('SPARSE ')]
    write_json(out/'summary.json',dict(status='PASS'if not result['exit_code']else'FAIL',origin='independent AD2 kinematic pullback/leaf contact,NOT a new SOFA component or equilibrium',metrics=lines[-1]if lines else None,sparse=sparse,source_sha256=sha(source),header_sha256=sha(header),binary_sha256=sha(exe),process=result));print(lines,sparse)
if __name__=='__main__':main()
