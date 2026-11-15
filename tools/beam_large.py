from beam_common import OUT,BUILD,write_json
from closure_validation_suite import logged
def main():
    out=OUT/'large_kernel_corrected';out.mkdir(exist_ok=False);binary=BUILD/'test_beam_large';r=logged(['g++','-O3','-std=c++17','tests/test_beam_large.cpp','-o',str(binary)],out/'compile',120)
    if r['exit_code']:raise RuntimeError('large kernel compile')
    r=logged([str(binary)],out/'unit',60);write_json(out/'summary.json',dict(status='PASS' if r['exit_code']==0 else 'FAIL',process=r,scope='40 large relative-rotation kernel states plus noncommuting closed-loop midpoint integration, not whole-beam large-deformation validation'));print(r)
if __name__=='__main__':main()
