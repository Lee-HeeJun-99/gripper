"""Three physical guided fingers, separate model/outputs; matched SDK only."""
from closure_common import ROOT,SOFA,BUILD,sha,write_json,provenance
from closure_common import OUT as CAMPAIGN
OUT=CAMPAIGN/'threefinger'
PLUGIN=BUILD/'frame/libReGripFrameClosure.so'
SDK=ROOT/'build/grasp_20261115/sofa_patched'
def identity():
    files=[p for folder in ('models/closure_frame','models/closure','models/grasp','models/integrated','models/finite_rotation','models/stabilization') for p in (ROOT/folder).glob('*') if p.is_file()]
    files += [ROOT/'tools'/n for n in ('closure_frame_trial.py','closure_frame_common.py','run_trial.py','trial_validation.py','integrated_trial.py')]
    return dict(source_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},binary_sha256=sha(PLUGIN),engine='matched-patched',sofa_source_commit='7c18e95d5c5f2839079892c69e7d89a313c79603',sdk_root=str(SDK),global_energy_available=False)
