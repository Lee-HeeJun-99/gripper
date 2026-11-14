"""Compare prior SOFA V105 reference CSV with V106 independent static FEM.
This is a qualitative comparison only: V105 at 0.30s was not at equilibrium.
"""
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parent
fnames=['result_V105_00_BASELINE.csv','result_V105_01_ALL_ZERO_K01_DT05.csv']
print('SOFA V105 transient comparator (0.3s, NOT static equilibrium)')
for fn in fnames:
    p=ROOT/fn
    if not p.exists():
        print(fn,'NOT FOUND: copy from V105 output folder if needed');continue
    with p.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    r=rows[-1]
    print(fn,'status',r['status'],'time',r['time_s'],
          'tip',r['tip_deflection_mm'],'x_slip',r['max_x_slip_mm'],
          'tip_velocity',r['tip_velocity_z_mm_s'])
print('V106 Python static directional shear results: comparison_V106_static.csv')
