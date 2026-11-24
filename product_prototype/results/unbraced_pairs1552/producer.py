"""Actual Native Guide-Guide response rows;do not hide indirect hardware bracing.
Scalar multiplier/dt is NOT a reconstructed Guide body resultant/wrench.
"""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.case;dt=float(ET.parse(src/'scene.scn').getroot().get('dt'));pairs={};maximum=0.;holdmax=0.;count=0;holdcount=0
 with (src/'response_rows.csv').open() as stream:
  for r in csv.DictReader(stream):
   paths=(r['model0'],r['model1']);matches=[re.match(r'/guides(\d+)/cable(\d+)/',x) for x in paths]
   if not all(matches) or matches[0][1]==matches[1][1]:continue
   value=abs(float(r['lambda_Ns']));t=float(r['time_s']);key=' | '.join(sorted(paths));p=pairs.setdefault(key,dict(rows=0,nonzero_rows=0,maximum_abs_scalar_multiplier_Ns=0.));p['rows']+=1;p['nonzero_rows']+=int(value!=0);p['maximum_abs_scalar_multiplier_Ns']=max(p['maximum_abs_scalar_multiplier_Ns'],value);maximum=max(maximum,value);count+=int(value!=0)
   if 1.6-1e-12<=t<=2.+1e-12:holdmax=max(holdmax,value);holdcount+=int(value!=0)
 d=dict(status='ACTUAL_INTERFINGER_GUIDE_CONTACT_PRESENT' if count else 'NO_NONZERO_INTERFINGER_GUIDE_RESPONSE_ROWS',case=a.case,pairs=pairs,nonzero_rows=count,hold_nonzero_rows=holdcount,maximum_abs_scalar_multiplier_Ns=maximum,maximum_abs_scalar_multiplier_div_dt_N=maximum/dt,hold_maximum_abs_scalar_multiplier_div_dt_N=holdmax/dt,Guide_body_resultant=None,scope='Actualconstraintprovenance/λ,notdetectorcounts or inferredarea. Nonzero hardware-hardware contact can brace fingers indirectly evenwhenGuideObjectforce0. Scalar rowλ/dt isnot fullbodyforce. Existingobject-onlyfunctionalverdict not altered;mechanismqualificationseparate.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','response_rows.csv')});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
