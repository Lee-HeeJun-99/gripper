"""Bounded torque reduction. Empty/synthetic records never produce hardware PASS."""
import argparse,csv,json,math
from pathlib import Path
from baseline_registry import ROOT,ref,dump
FIELDS=['specimen','operator','timestamp','force_gauge_calibration','length_gauge_calibration','force_N','zero_N','force_uncertainty_N','zero_uncertainty_N','lever_m','lever_uncertainty_m','angle_rad','angle_uncertainty_rad','temperature_C','record_kind']
def reduce(row):
    for k in FIELDS:
        if str(row.get(k,''))=='':raise ValueError('missing '+k)
    keys=FIELDS[5:14];d={k:float(row[k]) for k in keys}
    if not all(math.isfinite(x) for x in d.values()):raise ValueError('nonfinite')
    if any(d[k]<0 for k in ('force_uncertainty_N','zero_uncertainty_N','lever_uncertainty_m','angle_uncertainty_rad')):raise ValueError('negative uncertainty')
    if d['lever_m']<=d['lever_uncertainty_m']:raise ValueError('invalid lever interval')
    if abs(d['angle_rad'])+d['angle_uncertainty_rad']>math.radians(5):raise ValueError('outside declared fixture travel')
    if row['record_kind'] not in ('ACTUAL','SYNTHETIC'):raise ValueError('unknown record kind')
    lo=d['angle_rad']-d['angle_uncertainty_rad'];hi=d['angle_rad']+d['angle_uncertainty_rad'];cosines=[math.cos(lo),math.cos(hi)]
    if lo<=0<=hi:cosines.append(1.)
    force=d['force_N']-d['zero_N'];u=d['force_uncertainty_N']+d['zero_uncertainty_N']
    candidates=[f*l*c for f in (force-u,force+u) for l in (d['lever_m']-d['lever_uncertainty_m'],d['lever_m']+d['lever_uncertainty_m']) for c in (min(cosines),max(cosines))]
    return dict(torque_Nm=force*d['lever_m']*math.cos(d['angle_rad']),torque_interval_Nm=[min(candidates),max(candidates)],
        hardware_release=False,force_cap_qualified=False,record_kind=row['record_kind'])
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'hardware_test/inspection'/a.tag;out.mkdir(parents=True,exist_ok=False)
    blank=out/'TORQUE_RECORDS.csv'
    with blank.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerow(dict.fromkeys(FIELDS,''))
    good=dict.fromkeys(FIELDS,'SYNTHETIC');good.update(force_N=.2,zero_N=.001,force_uncertainty_N=.001,zero_uncertainty_N=.001,lever_m=.1,lever_uncertainty_m=.0001,angle_rad=0.,angle_uncertainty_rad=.001,temperature_C=20.)
    control=reduce(good);assert control['hardware_release'] is False
    cases=[{},dict(good,force_N='NaN'),dict(good,lever_m=-1),dict(good,angle_rad=.2),dict(good,force_uncertainty_N=-.1),dict(good,force_gauge_calibration='')]
    rejected=[]
    for row in cases:
        try:reduce(row);rejected.append(False)
        except (ValueError,TypeError):rejected.append(True)
    assert all(rejected)
    dump(out/'summary.json',dict(status='SOFTWARE_CONTROLS_PASS',physical_status='HARDWARE_NOT_MEASURED',actual_measurements=0,blank_records=ref(blank),negative_controls_rejected=rejected,synthetic_example=control,producer=ref(Path(__file__))))
    print(json.dumps(dict(status='SOFTWARE_CONTROLS_PASS',actual_measurements=0,negative_controls=len(cases))))
if __name__=='__main__':main()
