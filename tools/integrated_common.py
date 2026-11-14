"""Independent campaign boundaries; legacy sources/gates are read-only."""
import os
from pathlib import Path
from verification_common import ROOT,SOFA,sha,write_json,provenance
OUT=Path(os.environ.get('REGRIP_INTEGRATED_OUT',str(ROOT/'results/integrated_20261115'))).resolve()
BUILD=ROOT/'build/integrated_20261115'
