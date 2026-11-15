"""New campaign only; prior model sources, binaries and raw evidence are immutable."""
import os
from pathlib import Path
from verification_common import ROOT,SOFA,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_GRASP_OUT',ROOT/'results/grasp_20261115')).resolve()
BUILD=ROOT/'build/grasp_20261115'
PLUGIN=Path(os.environ.get('REGRIP_STICK_PLUGIN',BUILD/'stick_v2/libReGripStickSlip.so')).resolve()
PYTHON='/home/ubuntu/miniconda3/envs/robot_ws/bin/python'

def identity():
    files=[p for folder in ('models/grasp','models/integrated','models/stabilization','models/finite_rotation') for p in (ROOT/folder).glob('*') if p.is_file()]
    files += [ROOT/'tools/grasp_trial.py',ROOT/'tools/integrated_trial.py',ROOT/'tools/run_trial.py',ROOT/'tools/trial_validation.py']
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},binary_sha256=sha(PLUGIN),sofa_git_info=(SOFA/'git-info.txt').read_text())
