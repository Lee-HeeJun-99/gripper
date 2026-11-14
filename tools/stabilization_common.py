"""Campaign boundaries: original integrated code/build/results remain read-only."""
import os
from pathlib import Path
from verification_common import ROOT,SOFA,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_STABILIZATION_OUT',str(ROOT/'results/stabilization_20261115'))).resolve()
BUILD=ROOT/'build/stabilization_20261115'
PLUGIN=BUILD/'plugin/libReGripStabilization.so'
