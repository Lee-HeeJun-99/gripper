"""Correct the finite-rotation postprocessor without rewriting historical raw data."""
import csv
import json
import argparse
from integrated_common import OUT,write_json,sha
from integrated_trial import Config,interface_slips,run
from trial_validation import read_states

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rerun',action='store_true');args=parser.parse_args()
    out=OUT/('finite_metric_correction_rerun' if args.rerun else 'finite_metric_correction');out.mkdir(parents=True,exist_ok=False);rows={}
    for name in ('small','moderate','moderate_halfdt'):
        source=OUT/'objective_connector'/name;r=json.loads((source/'metrics.json').read_text());c=Config(**r['config']);raw=read_states(source/'state.txt')
        with (source/'state.txt.csv').open() as stream:series=list(csv.DictReader(stream))
        values=[max(map(abs,interface_slips(frame['X'],c,c.height))) for frame in raw]
        error=max(abs(value-float(row['max_connector_slip'])) for value,row in zip(values,series))
        if len(values)!=len(series) or error>1e-11:raise RuntimeError('finite metric disagrees with independently evaluated C++ kernel')
        rows[name]=dict(final_exact_interface_slip_mm=values[-1],peak_exact_interface_slip_mm=max(values),max_CPP_recorder_difference_mm=error,
                       source_metrics_sha256=sha(source/'metrics.json'),source_state_sha256=sha(source/'state.txt'),old_small_planar_metric_excluded=True)
    if args.rerun:
        source=OUT/'objective_connector/moderate/metrics.json';c=Config(**json.loads(source.read_text())['config'])
        fresh=run(out/'rerun',c)
        if fresh['status']!='PASS' or abs(fresh['max_interface_slip_mm']-rows['moderate']['final_exact_interface_slip_mm'])>1e-10:raise RuntimeError('corrected metric actual SOFA regression failed')
        rows['rerun']=fresh
    write_json(out/'summary.json',dict(passed=True,records=rows,scope='new postprocessing and optional fresh SOFA regression, no historical raw/model changes'))
    print(rows)

if __name__=='__main__':main()
