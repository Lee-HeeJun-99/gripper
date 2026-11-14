"""Compare CSV outputs; COMPLETE means 0.3-s run, not steady-state."""
import csv, math
from pathlib import Path
HERE=Path(__file__).resolve().parent
cases=["00_FREE_LDL","01_TAN_K001_LDL","02_TAN_K01_LDL","03_TAN_K1_LDL","04_FREE_LDL_AXIAL","05_TAN_K001_LDL_AXIAL","06_TAN_K01_LDL_AXIAL","07_TAN_K1_LDL_AXIAL","08_TAN_K001_LDL_DT025","09_FREE_LDL_DT025"]
rows=[]; bycase={}
for case in cases:
    path=HERE/("result_V109_"+case+".csv")
    if not path.exists():
        print("MISSING",path.name);continue
    with path.open(encoding="utf-8-sig",newline="") as f:
        data=list(csv.DictReader(f))
    if not data:
        print("EMPTY",path.name);continue
    last=data[-1]
    fields=["tip_deflection_mm","max_x_slip_mm","max_y_rel_mm","max_z_rel_mm", "max_applied_shear_force","nonzero_force_calls"]
    def num(name):
        try:return float(last.get(name,""))
        except:return float("nan")
    row={"case":case,"status":last.get("status",""),"time_s":last.get("time_s","")}
    row.update({field:num(field) for field in fields})
    rows.append(row);bycase[case]=row
for name,free in [("01_TAN_K001_LDL","00_FREE_LDL"),("02_TAN_K01_LDL","00_FREE_LDL"),
                  ("03_TAN_K1_LDL","00_FREE_LDL"),("05_TAN_K001_LDL_AXIAL","04_FREE_LDL_AXIAL"),
                  ("06_TAN_K01_LDL_AXIAL","04_FREE_LDL_AXIAL"),("07_TAN_K1_LDL_AXIAL","04_FREE_LDL_AXIAL")]:
    if name not in bycase or free not in bycase:continue
    a=bycase[name];b=bycase[free]
    if a["status"]!="COMPLETE" or b["status"]!="COMPLETE":continue
    bslip=b["max_x_slip_mm"]
    a["slip_reduction_pct"]=100*(1-a["max_x_slip_mm"]/bslip) if bslip>1e-12 else float('nan')
    btip=b["tip_deflection_mm"];atip=a["tip_deflection_mm"]
    a["tip_ratio_free_over_coupled"]=btip/atip if abs(atip)>1e-12 else float('nan')
path=HERE/"comparison_V109.csv"
fields=["case","status","time_s","tip_deflection_mm","max_x_slip_mm","max_y_rel_mm","max_z_rel_mm","max_applied_shear_force","nonzero_force_calls","slip_reduction_pct","tip_ratio_free_over_coupled"]
with path.open("w",encoding="utf-8-sig",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
    writer.writeheader();writer.writerows(rows)
print("OUTPUT",path)
for row in rows:print(row['case'], row['status'], 'tip=',row['tip_deflection_mm'], 'slip=',row['max_x_slip_mm'], 'nonzero=',row['nonzero_force_calls'])
base=bycase.get('00_FREE_LDL')
if base:
    tip=base['tip_deflection_mm']
    print('BASELINE_0.3s_~0.041214mm:', 'PASS' if base['status']=='COMPLETE' and abs(tip-0.041214)<0.002 else 'FAIL')
print('WARNING: sparse LDL matrix incorporation for Python ForceField is NOT established by these CSVs.')
