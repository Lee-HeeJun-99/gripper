from pathlib import Path
import csv, math
HERE=Path(__file__).resolve().parent
rows=[]
for f in sorted(HERE.glob('result_V108_*.csv')):
    with f.open(encoding='utf-8-sig',newline='') as h:data=list(csv.DictReader(h))
    if not data:continue
    x=data[-1]
    rows.append({**{'file':f.name},**{k:x.get(k,'') for k in ['case','time_s','status','tip_deflection_mm','tip_velocity_z_mm_s','max_x_slip_mm','max_mapped_movement_mm','mean_abs_rotation_quat_xyz','shear_energy_proxy','addForce_calls','addDForce_calls']}})
if not rows:raise SystemExit('No result_V108_*.csv files: run SOFA scenes first')
with (HERE/'comparison_V108.csv').open('w',encoding='utf-8-sig',newline='') as fp:
    w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for r in rows: print(r['case'],r['status'],'t=',r['time_s'],'tip=',r['tip_deflection_mm'],'slip=',r['max_x_slip_mm'])
ref=next((r for r in rows if r['case']=='01_COMBINED_FREE_LDL'),None)
base=next((r for r in rows if r['case']=='02_COMBINED_FREE_CG'),None)
if ref and base and ref['status']=='COMPLETE' and base['status']=='COMPLETE':
    a=float(ref['tip_deflection_mm']);b=float(base['tip_deflection_mm']);
    print('LDL-vs-CG rel difference:', abs(a-b)/max(abs(a),1e-12))
print('IMPORTANT: reference V105 output is result_V105_V108_00_REFERENCE.csv, not result_V108_*.csv')
