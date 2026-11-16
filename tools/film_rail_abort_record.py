"""Append cancellation evidence without modifying partial Raw or pretending completion."""
import argparse,csv,json,subprocess
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);cases={}
    for name,expected in [('20261116_rail_cycle200_79',200),('20261116_rail_cycle400_80',400),('20261116_rail_cycle800_81',800)]:
        base=ROOT/'results'/('autonomous_film_'+name);rows=list(csv.DictReader((base/'1/journal.csv').open()));profile=list(csv.DictReader((base/'1/profile.csv').open()));log=(base/'1/process/stdout.log').read_text()
        if 'Newton-Raphson method failed to converge' not in log:raise RuntimeError('no physical failure evidence')
        first=next((r for r in profile if int(r['newton_iterations'])>=30),None)
        record=dict(status='FAIL',process_status='manually_interrupted_after_observed_Newton_failure',driver_interrupt_exit_code=130,physics_exit_code=None,
            expected_rows=expected,actual_partial_rows=len(rows),first_newton_limit=first,warning_count=log.count('Newton-Raphson method failed to converge'),
            reason='Nonlinear failure followed by rapidly increasing energy/speed. Exact three tracked command sessions were interrupted;no invalid continuation is treated as physical data.',
            last_partial_state={k:v for k,v in rows[-1].items() if k!='x'},artifacts={str(p.relative_to(base)):sha(p) for p in base.rglob('*') if p.is_file() and 'sources' not in p.parts},
            source='actual partial SOFA journals and logs;driver interrupt130 reported by execution tool;missing physics exit is null,not invented')
        destination=base/'ABORTED.json'
        if destination.exists():raise FileExistsError('abort evidence already exists')
        write_json(destination,record);cases[name]=record
    write_json(out/'summary.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),cases=cases))
    print({k:v['first_newton_limit']['time'] for k,v in cases.items()})
if __name__=='__main__':main()
