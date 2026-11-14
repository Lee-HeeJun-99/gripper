"""Stricter nonzero-load residual audit of historical raw-derived CSV, read-only."""
import csv
import json
from integrated_common import OUT,write_json,sha
from integrated_trial import Config

def main():
    out=OUT/'residual_audit';out.mkdir(parents=True,exist_ok=False);rows={}
    for group in ('tendon','friction','contact','objective_connector'):
        for p in sorted((OUT/group).glob('*/metrics.json')):
            r=json.loads(p.read_text());c=Config(**r['config']);force=max(abs(c.load),abs(c.moment)/c.length,c.cable_tension*abs(c.cable_offset)/c.length,c.cable_k*c.shortening*abs(c.cable_offset)/c.length,*(map(abs,c.load_values) or [0]))
            scale=max(force,1e-6)/(force or 1e-6)
            with (p.parent/'metrics_series.csv').open() as stream:series=list(csv.DictReader(stream))
            tail=series[-max(2,round(.1/(c.dt*c.stride))):]
            strict=max(float(s['residual']) for s in tail)*scale
            status='PASS' if r['status']=='PASS' and strict<1e-3 else ('FAIL' if c.kind=='equilibrium' else 'EXPERIMENTAL')
            rows[str(p.parent.relative_to(OUT))]=dict(original_status=r['status'],strict_status=status,nonzero_force_reference=force,
                strict_tail_max_residual=strict,source_metrics_sha256=sha(p),source_series_sha256=sha(p.parent/'metrics_series.csv'),
                reason='nonzero-load normalization without 1e-6 floor; physical tolerances unchanged; historical data unmodified')
    write_json(out/'summary.json',dict(records=rows,scope='stronger post-audit, overrides weak-normalizer physical claims but not original execution evidence'))
    print([(k,v['strict_status'],v['strict_tail_max_residual']) for k,v in rows.items()])

if __name__=='__main__':main()
