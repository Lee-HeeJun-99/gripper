"""Non-mutating host probes and isolated optional dependency installation attempts."""
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
from verification_common import ROOT, SOFA, RUN, command, provenance, write_json


def main():
    probes={
        'os':['cat','/etc/os-release'],'kernel':['uname','-a'],'gcc':['gcc','--version'],
        'gxx':['g++','--version'],'cmake':['cmake','--version'],'disk':['df','-h',str(ROOT)],
        'memory':['free','-h'],'cpu':['nproc'],'runsofa_help':[str(SOFA/'bin/runSofa-26.06.00'),'--help'],
        'sofa_ldd':['ldd',str(SOFA/'bin/runSofa-26.06.00')],
        'python_plugin_ldd':['ldd',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')],
        'python_plugin_cmake':['cat',str(SOFA/'plugins/SofaPython3/lib/cmake/SofaPython3/SofaPython3Config.cmake')],
        'default_python':['python3','--version'],'system_python':['/usr/bin/python3','--version'],
        'dns':['getent','hosts','pypi.org','repo.anaconda.com'],
        'network':['curl','--head','--max-time','10','https://pypi.org/simple/optuna/'],
        'offline_wheels':['find','/home/ubuntu','/tmp','-maxdepth','8','-type','f','(','-iname','*.whl','-o','-iname','*optuna*.conda','-o','-iname','python-3.12*.conda',')'],
        'python312_search':['find','/home/ubuntu/miniconda3','/opt','/usr/local','-name','libpython3.12.so*'],
    }
    results={name:command('env_'+name,args) for name,args in probes.items()}
    packages={}
    for name in ('numpy','scipy','matplotlib','optuna','ruff','pytest'):
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]=None
    env=os.environ.copy();env['PIP_CONFIG_FILE']='/dev/null'
    results['optuna_install']=command('optuna_install',[sys.executable,'-m','pip','--isolated','install',
        '--target',str(ROOT/'.python-deps'),'--index-url','https://pypi.org/simple','--no-cache-dir',
        '--retries','0','--timeout','10','optuna>=3.6,<5'],timeout=90,env=env)
    # Conda is not retried if DNS is unavailable; record a direct isolated command if it can connect.
    results['python312_install_status']='BLOCKED: DNS unavailable; no cached Python 3.12 runtime found' if results['dns']['exit_code'] else 'runtime search must be evaluated'
    write_json(RUN/'environment.json',dict(provenance=provenance(),packages=packages,probes=results))


if __name__=='__main__':main()
