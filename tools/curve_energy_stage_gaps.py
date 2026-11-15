"""Audit matched-state Begin versus previous Post-Commit inventories."""
import argparse
import csv
import json
from curve_common import OUT,write_json,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('journal',default='energy_after_arithmetic_48000_v9',nargs='?');a=p.parse_args();path=OUT/a.journal;target=path/'matched_stage_gaps_v1.json'
    if target.exists():raise ValueError('refuse overwritten matched-stage evidence')
    if json.loads((path/'summary.json').read_text())['status']!='PASS':raise ValueError('actual pure journal prerequisite')
    keys=('beam_U','layer_U','contact_U','K');acc={k:dict(total=0.,maximum_absolute=0.,maximum_step=None,nonzero=0)for k in keys};largest=[];last=None
    with(path/'energy.csv').open()as f:
        for row in csv.DictReader(f):
            if row['stage']=='begin'and last is not None:
                gaps={k:float(row[k])-float(last[k])for k in keys}
                for k,g in gaps.items():
                    s=acc[k];s['total']+=g;s['nonzero']+=g!=0
                    if abs(g)>s['maximum_absolute']:s.update(maximum_absolute=abs(g),maximum_step=int(row['step']))
                if any(gaps.values()):largest.append(dict(step=int(row['step']),time=float(row['time']),gaps=gaps))
            if row['stage']=='post_commit':last=row
    largest=sorted(largest,key=lambda r:max(abs(v)for v in r['gaps'].values()),reverse=True)[:20]
    write_json(target,dict(status='EXPERIMENTAL',source=sha(path/'energy.csv'),inventory_gaps=acc,largest_events=largest,scope='actual previous Post-Commit versus next Begin at nominally unchanged q/v. A nonzero return-candidate potential jump must not be silently called external parameter work or heat;component semantics require analysis.'))
    print(acc);print(largest[:5])


if __name__=='__main__':main()
