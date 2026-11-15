"""Recover completed runs after the specific original steps NameError.

The original short-circuit condition evaluates 'steps' ONLY after exit_code==0
and an ERROR-free log. This proves exit0 from that recorded exception; elapsed
wall time is not recoverable and remains None. Nothing is fabricated or rerun.
"""
import argparse,json
from history_common import OUT,ROOT,write_json,sha
from history_trial import analyze
def main():
    p=argparse.ArgumentParser();p.add_argument('names',nargs='+');a=p.parse_args();campaign=json.loads((OUT/'campaign_v3.json').read_text())
    for name in a.names:
        out=OUT/'grasp'/name;target=out/'recovered_metrics.json'
        if target.exists():raise FileExistsError(target)
        if campaign[name].get('failure_reason')!='NameError("name \'steps\' is not defined")':raise ValueError('not the independently established postprocessor failure')
        c=json.loads((out/'config.json').read_text());log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();steps=round(c['duration']/c['dt'])
        if '[ERROR]' in log or f'{steps} iterations done' not in log:raise ValueError('not complete/error-free')
        process=dict(exit_code=0,runtime_s=None,process_status='reconstructed_from_recorded_short_circuit_NameError',evidence='git fda0e80 history_trial.analyze evaluates undefined steps after exit_code==0 and ERROR-free checks; original campaign exception retained; wall time unknown')
        r=analyze(out,c,process);r['recovery']=dict(original_failure=campaign[name],original_analyzer_commit='fda0e8036fc1c4e8fe07d6fa8a2bf6b5319d3322',scope='same immutable actual states, no rerun, exit0 logically reconstructed, not directly persisted');r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(target,r);print(name,r['status'],r.get('hold_displacement_mm'),r.get('global_moment_residual'))
if __name__=='__main__':main()
