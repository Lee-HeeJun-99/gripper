"""Preserve exact-state equivalence separately from rejected performance gain."""
import argparse,csv,json
from curve_common import ROOT,sha,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);metrics={};journals={};hashes={}
    for tag in ('profile28','gradient29'):
        campaign=ROOT/'results'/('autonomous_film_20261116_'+tag);summary=json.loads((campaign/'summary.json').read_text());timings=list(csv.DictReader((campaign/'1/profile.csv').open()));journal=campaign/'1/journal.csv';journals[tag]=list(csv.DictReader(journal.open()));hashes[tag]=sha(journal)
        if len(timings)!=150 or len(journals[tag])!=150:raise RuntimeError('incomplete profile')
        metrics[tag]=dict(runtime_s=summary['stages']['1']['runtime_s'],stage_s={key:sum(float(row[key]) for row in timings) for key in timings[0] if key!='time'})
    report=dict(source='Actual SOFA and passive stage timers;not grasp',metrics=metrics,raw_sha256=hashes,state_equivalence='PASS' if journals['profile28']==journals['gradient29'] else 'FAIL',runtime_ratio=metrics['gradient29']['runtime_s']/metrics['profile28']['runtime_s'],performance_status='FAIL',decision='Reject runtime gradient-order variant;restore default AD/FilmShell. Variant source preserved in Git eebbb45 and campaign29/sources. residual_s includes force_damping_s and mass_product_s, so do not sum overlapping timers.')
    write_json(out/'summary.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
