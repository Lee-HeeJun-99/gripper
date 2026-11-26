"""Strict acquisition-log validation; empty records are NOT MEASURED.
No machine/actuator communication. Force-extension fit is not a pullout PASS.
"""
import argparse,csv,json,math
from pathlib import Path
import numpy as np
FIELDS=['specimen_ID','calibration_ID','timestamp','time_s','force_N','extension_m','temperature_C']
def evaluate(rows):
    if not rows:return dict(status='NOT MEASURED',hardware_pass=False,reason='No recorded physical samples')
    try:
        for row in rows:
            if any(row.get(k) is None or row.get(k)=='' for k in FIELDS):raise ValueError('missing field')
            for k in FIELDS[3:]:
                if not math.isfinite(float(row[k])):raise ValueError('nonfinite measurement')
        if len({r['specimen_ID'] for r in rows})!=1:raise ValueError('mixed specimens')
        if len({r['calibration_ID'] for r in rows})!=1:raise ValueError('mixed calibrations')
        t=np.array([float(r['time_s']) for r in rows]);f=np.array([float(r['force_N']) for r in rows]);x=np.array([float(r['extension_m']) for r in rows])
        if len(t)<5 or np.any(np.diff(t)<=0):raise ValueError('need >=5 strictly time-ordered samples')
        if np.any(f<0) or np.ptp(x)<=1e-8:raise ValueError('invalid tensile force or extension range')
        slope,intercept=np.polyfit(x,f,1)
        if slope<=0:raise ValueError('nonpositive stiffness')
        return dict(status='VALID LOG ONLY',hardware_pass=False,linear_stiffness_N_m=float(slope),intercept_N=float(intercept),
            RMS_force_fit_N=float(np.sqrt(np.mean((f-slope*x-intercept)**2))),
            max_recorded_force_N=float(f.max()),warning='Fit range / extensometer gauge length / creep / pullout / retention qualification require protocol-specific review')
    except (ValueError,TypeError) as e:return dict(status='INVALID',hardware_pass=False,reason=str(e))
def main():
    p=argparse.ArgumentParser();p.add_argument('csv');a=p.parse_args();result=evaluate(list(csv.DictReader(open(a.csv))))
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['status']=='VALID LOG ONLY' else 2)
if __name__=='__main__':main()
