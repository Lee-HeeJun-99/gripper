"""Bounded, non-system-mutating recovery and previous-evidence verification."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from verification_common import ROOT, SOFA, sha, write_json, provenance, assert_build_current

OUT=ROOT/'results/next_phase/environment'

def run(name, cmd, timeout=35, env=None):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,env=env)
        text=p.stdout+p.stderr;code=p.returncode
    except (subprocess.TimeoutExpired,OSError) as e:text=str(e);code=None
    (OUT/(name+'.log')).write_text(text)
    return dict(command=cmd,exit_code=code,log=str(OUT/(name+'.log')))

def main():
    OUT.mkdir(parents=True,exist_ok=False)
    manifest=json.loads((ROOT/'reports/REVALIDATION_EVIDENCE_MANIFEST.json').read_text())
    failures=[p for p,h in manifest['files'].items() if sha(ROOT/p)!=h]
    failures += [p for p,h in manifest['report_sha256'].items() if sha(ROOT/'reports'/p)!=h]
    assert_build_current()
    from optimize import validate_gate
    gate=ROOT/'results/revalidation_20261114T132734Z/physics_release/gate.json'
    validate_gate(gate)
    dns={}
    for host in ('pypi.org','files.pythonhosted.org','repo.anaconda.com'):
        try:dns[host]=dict(addresses=sorted({a[4][0] for a in socket.getaddrinfo(host,443)}))
        except OSError as e:dns[host]=dict(error=str(e))
    # Record only presence, never credentials or proxy URLs.
    settings={key:bool(os.environ.get(key)) for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','PIP_INDEX_URL','PIP_EXTRA_INDEX_URL','PIP_NO_INDEX')}
    pip=run('pip_install',[sys.executable,'-m','pip','install','--isolated','--disable-pip-version-check',
        '--retries','0','--timeout','8','--target',str(ROOT/'.python-deps'),'optuna>=3.6,<5'])
    cache=run('pip_cache',[sys.executable,'-m','pip','cache','list','optuna'])
    # Do not dump pip config values (indexes may contain credentials).
    config=run('pip_config_keys',[sys.executable,'-c',
        'from pip._internal.configuration import Configuration; c=Configuration(isolated=False); c.load(); print("\\n".join(sorted(c.items_dict)) if hasattr(c,"items_dict") else "\\n".join(k for k,v in c.items()))'])
    libs=list((SOFA/'plugins/SofaPython3').rglob('libSofaPython3.so'))
    abi=[run('python_abi_'+str(i),['ldd',str(p)]) for i,p in enumerate(libs)]
    local=[]
    for root in (ROOT.parent,Path('/home/ubuntu/miniconda3/pkgs'),Path('/home/ubuntu/.cache/pip')):
        for pattern in ('*optuna*.whl','libpython3.12.so*','*python-3.12*.conda','*python-3.12*.tar.bz2'):
            local += [str(p) for p in root.rglob(pattern)]
    env=os.environ.copy();env['CONDA_PKGS_DIRS']=str(ROOT/'.conda-pkgs')
    runtime=run('python312_offline',['/home/ubuntu/miniconda3/bin/conda','create','--prefix',str(ROOT/'.venv-sofa-next'),
        '--offline','--solver','classic','--yes','python=3.12','numpy'],env=env)
    online=run('python312_online',['/home/ubuntu/miniconda3/bin/conda','create','--prefix',str(ROOT/'.venv-sofa-next'),
        '--solver','classic','--yes','python=3.12','numpy'],timeout=45,env=env)
    scene=ROOT/'scenes/python_smoke.py'
    smoke=run('python_scene',[str(SOFA/'bin/runSofa-26.06.00'),'--noautoload','--tmp','-g','batch','-a','-n','3',
         '-l','SofaPython3',str(scene)])
    record=dict(provenance=provenance(),evidence_failures=failures,validated_gate=sha(gate),
        dns=dns,configuration_presence=settings,pip=pip,pip_cache=cache,pip_config=config,
        local_candidates=local,python=sys.version,python_executable=sys.executable,site_paths=sys.path,
        optuna_available=importlib.util.find_spec('optuna') is not None,abi=abi,
        python312_offline=runtime,python312_online=online,python_scene=smoke)
    write_json(OUT/'summary.json',record)
    print(json.dumps(dict(evidence_failures=failures,dns=dns,optuna_available=record['optuna_available']),indent=2))

if __name__=='__main__':main()
