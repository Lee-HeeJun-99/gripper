"""Configure, compile and test while preserving complete command logs."""
import json
import argparse
import datetime
from verification_common import BUILD,compiled_sources,sha,write_json
from pathlib import Path
import subprocess
from baseline_regression import ROOT, SOFA


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build-root',type=Path,default=BUILD)
    parser.add_argument('--logs',type=Path)
    parser.add_argument('--sanitize',action='store_true')
    a=parser.parse_args()
    logs=a.logs or ROOT/'results'/('revalidation_build_'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    logs.mkdir(parents=True,exist_ok=False)
    before=compiled_sources()
    extra=['-DCMAKE_CXX_FLAGS=-Wall -Wextra -Wpedantic']
    if a.sanitize:
        extra=['-DCMAKE_CXX_FLAGS=-Wall -Wextra -Wpedantic -fsanitize=address,undefined -fno-omit-frame-pointer',
               '-DCMAKE_SHARED_LINKER_FLAGS=-fsanitize=address,undefined','-DCMAKE_EXE_LINKER_FLAGS=-fsanitize=address,undefined']
    for source in ('diagnostics','plugin'):
        for stage,cmd in [
            ('configure',['cmake','-S',str(ROOT/source),'-B',str(a.build_root/source),
                          '-DCMAKE_BUILD_TYPE=RelWithDebInfo','-DBUILD_TESTING=ON','-DCMAKE_PREFIX_PATH='+str(SOFA)]+extra),
            ('compile',['cmake','--build',str(a.build_root/source),'-j','2'])]:
            run=subprocess.run(cmd,capture_output=True,text=True)
            (logs/f'{source}_{stage}.log').write_text(run.stdout+run.stderr)
            (logs/f'{source}_{stage}.command.json').write_text(json.dumps(cmd,indent=2))
            if run.returncode:raise RuntimeError(f'{source} {stage} failed; inspect {logs}')
    run=subprocess.run(['ctest','--test-dir',str(a.build_root/'plugin'),'--output-on-failure'],capture_output=True,text=True)
    (logs/'ctest.log').write_text(run.stdout+run.stderr)
    print(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError('native tests failed')
    if before!=compiled_sources():raise RuntimeError('sources changed during build; manifest not issued')
    files=['plugin/bin/libSofaTangentialV110.so','diagnostics/libReGripDiagnostics.so','plugin/test_forcefield','plugin/probe_forcefield']
    write_json(a.build_root/'build_manifest.json',dict(source_sha256=before,
        binary_sha256={name:sha(a.build_root/name) for name in files},logs=str(logs),sanitized=a.sanitize))


if __name__=='__main__':main()
