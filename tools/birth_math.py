from birth_common import ROOT,OUT,write_json,sha
from closure_validation_suite import logged
def main():
    out=OUT/'math_events';out.mkdir(exist_ok=False);exe=ROOT/'build/birth_20261115/test_birth_math';source=ROOT/'tests/test_birth_events_math.cpp'
    r=logged(['g++','-O2','-std=c++17','-Wall','-Wextra','-Wpedantic',source,'-o',exe],out/'compile',120)
    if r['exit_code']:raise RuntimeError('math compile')
    r=logged([exe],out/'run',60);write_json(out/'summary.json',dict(status='PASS' if r['exit_code']==0 else 'FAIL',source_sha256=sha(source),binary_sha256=sha(exe),process=r,scope='independent prescribed contact mathematics, NOT integrated energy closure'));print(r['exit_code'])
if __name__=='__main__':main()
