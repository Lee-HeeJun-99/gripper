"""Select an exclusive new run root without editing code between sessions."""
import os
from pathlib import Path
from verification_common import ROOT
NEXT=Path(os.environ.get('REGRIP_NEXT_OUT',str(ROOT/'results/next_phase'))).resolve()
