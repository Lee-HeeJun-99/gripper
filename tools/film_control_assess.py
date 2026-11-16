"""Actual applied tension agreement, not a temporal convergence certificate."""
import argparse,csv,json,math,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case)/'1';summary=json.loads((source.parent/'summary.json').read_text())
    if summary.get('status')!='PASS' or not summary.get('finite'):raise ValueError('complete finite case required')
    field=ET.parse(source/'scene.scn').find("Node[@name='assembly']/FilmRailTendon")
    maximum,ramp,release,end=(float(field.get(k)) for k in ('maximumTension','rampTime','releaseBegin','releaseEnd'))
    c2=field.get('c2Control','0')=='1';applied={}
    for line in (source/'coupled.csv.newton.log').read_text().splitlines():
        words=line.split()
        if words[:2]!=['applied_control','time']:continue
        time=float(words[2])
        if time in applied:raise ValueError('duplicate step control record')
        applied[time]=(float(words[4]),words[6]=='1')
    maximum_difference=0.;maximum_reference_ulps=0.;rows=list(csv.DictReader((source/'journal.csv').open()))
    for row in rows:
        time=float(row['time']);force=float(row['T_per_rail']);owner,flag=applied[time]
        if flag!=c2 or not math.isfinite(force) or not 0<=force<=maximum:raise ValueError('invalid or mismatched prescribed tension')
        maximum_difference=max(maximum_difference,abs(force-owner))
        if not c2:expected=maximum*min(max(time/ramp,0),1)*(1 if time<=release else min(max((end-time)/(end-release),0),1))
        elif time<=0 or time>=end:expected=0.
        elif ramp<=time<=release:expected=maximum
        else:
            closing=time<ramp;x=time/ramp if closing else (time-release)/(end-release);tail=x if x<=.5 else 1-x
            small=tail*tail*tail*(10+tail*(-15+6*tail))
            expected=maximum*((small if x<=.5 else 1-small) if closing else (1-small if x<=.5 else small))
        maximum_reference_ulps=max(maximum_reference_ulps,abs(force-expected)/math.ulp(expected))
    passed=len(applied)==len(rows) and maximum_difference==0 and maximum_reference_ulps<=4
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    result=dict(status='PASS' if passed else 'FAIL',scope='actual ForceField and accepted-owner tension equality/bounds;NOT time convergence or measured actuator capability',rows=len(rows),c2=c2,maximum_force_owner_difference=maximum_difference,maximum_independent_reference_ulps=maximum_reference_ulps,maximum_applied_tension=max(float(r['T_per_rail']) for r in rows),last_applied_tension=float(rows[-1]['T_per_rail']),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs={name:sha(source/name) for name in ('scene.scn','journal.csv','coupled.csv.newton.log')},script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
