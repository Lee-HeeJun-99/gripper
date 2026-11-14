from pathlib import Path
import csv
p=Path(__file__).resolve().parent/'scenes'
out=[]
for f in sorted(p.glob('result_V110_*.csv')):
 with f.open(encoding='utf-8-sig',newline='') as fh:
  rows=list(csv.DictReader(fh))
 if rows:
  row=rows[-1]
  out.append({key:row[key] for key in ['case','time_s','stiffness','dt_s','tip_deflection_mm','max_shear_x_mm','shear_energy','status']})
if out:
 dst=Path(__file__).resolve().parent/'comparison_V110.csv'
 with dst.open('w',encoding='utf-8-sig',newline='') as fh:
  w=csv.DictWriter(fh,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 print('Saved',dst)
else:print('No result_V110_*.csv in scenes directory yet')
