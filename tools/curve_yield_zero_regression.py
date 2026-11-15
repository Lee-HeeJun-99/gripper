import shutil
from curve_common import ROOT,OUT,sha,write_json
from closure_validation_suite import logged


def main():
    out=OUT/'yield_front_zero_capacity_before_v1';out.mkdir(exist_ok=False)
    for name in('tests/test_yield_front_zero.cpp','models/yield_front_history/ScalarField.h'):
        p=ROOT/name;target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    write_json(out/'sources.json',{name:sha(ROOT/name)for name in('tests/test_yield_front_zero.cpp','models/yield_front_history/ScalarField.h')})
    build=logged(['g++','-std=c++17','-O2',ROOT/'tests/test_yield_front_zero.cpp','-o',out/'regression.bin'],out/'build',180)
    unit=logged([out/'regression.bin'],out/'unit',180)if not build['exit_code']else None
    write_json(out/'summary.json',dict(status='PASS'if unit and unit['exit_code']==0 else'FAIL',build=build,unit=unit,scope='actual pre-fix zero-capacity tangent regression;failure is preserved,not converted to PASS'))


if __name__=='__main__':main()
