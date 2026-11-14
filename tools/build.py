"""Configure, compile and test while preserving complete command logs."""
import json
from pathlib import Path
import subprocess
from baseline_regression import ROOT, SOFA


def main():
    logs=ROOT/'results/build_logs';logs.mkdir(parents=True,exist_ok=True)
    for source in ('diagnostics','plugin'):
        for stage,cmd in [
            ('configure',['cmake','-S',str(ROOT/source),'-B',str(ROOT/'build'/source),
                          '-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DCMAKE_PREFIX_PATH='+str(SOFA)]),
            ('compile',['cmake','--build',str(ROOT/'build'/source),'-j','2'])]:
            run=subprocess.run(cmd,capture_output=True,text=True)
            (logs/f'{source}_{stage}.log').write_text(run.stdout+run.stderr)
            (logs/f'{source}_{stage}.command.json').write_text(json.dumps(cmd,indent=2))
            if run.returncode:raise RuntimeError(f'{source} {stage} failed; inspect {logs}')
    run=subprocess.run(['ctest','--test-dir',str(ROOT/'build/plugin'),'--output-on-failure'],capture_output=True,text=True)
    (logs/'ctest.log').write_text(run.stdout+run.stderr)
    print(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError('native tests failed')


if __name__=='__main__':main()
