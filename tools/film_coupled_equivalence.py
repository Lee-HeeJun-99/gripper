"""Exact physical CSV preservation and measured wall-clock contrast."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--before',required=True);p.add_argument('--after',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');left=ROOT/'results'/('autonomous_film_'+a.before);right=ROOT/'results'/('autonomous_film_'+a.after);lm=json.loads((left/'identity.json').read_text());rm=json.loads((right/'identity.json').read_text());ls=json.loads((left/'summary.json').read_text());rs=json.loads((right/'summary.json').read_text())
    if ls['status']!='PASS' or rs['status']!='PASS':raise ValueError('completed actual trials required')
    for key in ('mode','duration','steps','body_mass','inertia_per_mass','rayleigh_mass','initial_body_center','initial_body_velocity'):
        if lm[key]!=rm[key]:raise ValueError('physical input differs:'+key)
    names=('coupled.states.csv','coupled.events.csv','coupled.rows.csv','film.csv','displacement.csv');checks={name:sha(left/name)==sha(right/name) for name in names};baseline=ls['process']['runtime_s'];optimized=rs['process']['runtime_s'];status='PASS' if all(checks.values()) and optimized<baseline else 'FAIL';write_json(out/'summary.json',dict(status=status,scope='exact physical CSVs and single measured runtime contrast;NOT statistical benchmark or physics qualification',before=a.before,after=a.after,checks=checks,before_s=baseline,after_s=optimized,observed_speedup=baseline/optimized,binaries=[lm['binary_sha256'],rm['binary_sha256']],changed_archived_sources=[k for k in set(lm['sources'])|set(rm['sources']) if lm['sources'].get(k)!=rm['sources'].get(k)]));print(json.dumps(dict(status=status,checks=checks,observed_speedup=baseline/optimized)))
if __name__=='__main__':main()
