"""Record SDK dependencies, optional Python packages and the original build failure."""
import importlib.metadata
import json
import platform
import subprocess
import sys
from baseline_regression import ROOT, SOFA


def main():
    out=ROOT/'results/development_environment';out.mkdir(exist_ok=True)
    commands={
        'kernel':['uname','-a'],
        'compiler':['g++','--version'],
        'cmake':['cmake','--version'],
        'make':['make','--version'],
        'plugin_dependencies':['ldd',str(ROOT/'build/plugin/bin/libSofaTangentialV110.so')],
        'diagnostics_dependencies':['ldd',str(ROOT/'build/diagnostics/libReGripDiagnostics.so')],
        'sofa_python_dependencies':['ldd',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')],
        'original_build':['cmake','--build',str(ROOT/'build/v110_original'),'-j','2'],
    }
    report=dict(python_executable=sys.executable,python_version=platform.python_version(),packages={},commands={})
    for package in ('numpy','matplotlib','optuna'):
        try:report['packages'][package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:report['packages'][package]=None
    for name,command in commands.items():
        result=subprocess.run(command,capture_output=True,text=True)
        (out/(name+'.log')).write_text(result.stdout+result.stderr)
        report['commands'][name]=dict(command=command,exit_code=result.returncode)
    report['python312_install_attempt']='conda create failed: repo.anaconda.com DNS resolution'
    report['optuna_install_attempt']='pip target install failed: no matching distribution available in this execution environment'
    (out/'environment.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
