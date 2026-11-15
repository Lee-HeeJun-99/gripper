"""New closure campaign namespaces, no writes to old evidence/builds."""
import os
from pathlib import Path
from verification_common import ROOT,SOFA,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_CLOSURE_OUT',ROOT/'results/closure_20261115')).resolve()
BUILD=ROOT/'build/closure_20261115'
PLUGIN=Path(os.environ.get('REGRIP_CLOSURE_PLUGIN',BUILD/'release/libReGripClosure.so')).resolve()
SDK=Path(os.environ['REGRIP_CLOSURE_SDK']).resolve() if os.environ.get('REGRIP_CLOSURE_SDK') else None
PYTHON='/home/ubuntu/miniconda3/envs/robot_ws/bin/python'
def identity():
    files=[p for folder in ('models/closure','models/grasp','models/integrated','models/stabilization','models/finite_rotation') for p in (ROOT/folder).glob('*') if p.is_file()]
    files += [ROOT/'tools'/n for n in ('closure_trial.py','closure_common.py','integrated_trial.py','run_trial.py','trial_validation.py')]
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},binary_sha256=sha(PLUGIN),sofa_source_commit='7c18e95d5c5f2839079892c69e7d89a313c79603',engine='matched-patched' if SDK else 'installed',sdk_root=str(SDK) if SDK else str(SOFA),global_energy_available=False)
