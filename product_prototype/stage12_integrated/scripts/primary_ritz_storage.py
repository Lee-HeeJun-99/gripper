"""Lossless per-file <50MB storage for dense actual Ritz basis; no precision change."""
import numpy as np
from baseline_registry import REPO

def load(s):
 a=dict(np.load(REPO/s['output']['path']))
 if 'V' not in a:a['V']=np.column_stack([np.load(REPO/r['path'])['V'] for r in s['basis_columns']])
 return a
