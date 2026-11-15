"""Independent translation-only validation before applying old accumulator to rod."""
from beam_common import OUT,BUILD,write_json
from closure_validation_suite import logged
from beam_multilayer import run
from integrated_trial import Config
def main():
    out=OUT/'precision';out.mkdir(exist_ok=False);binary=BUILD/'test_beam_precision'
    r=logged(['g++','-std=c++17','-O3','tests/test_beam_precision.cpp','-o',str(binary)],out/'compile',120)
    if r['exit_code']:raise RuntimeError('precision unit compile')
    r=logged([str(binary)],out/'unit',30)
    if r['exit_code']:raise RuntimeError('precision validation')
    result=run('L8_k100_compensated',Config(layers=8,k=100,load=1e-6,duration=12.),compensated=True);write_json(out/'result.json',result)
if __name__=='__main__':main()
