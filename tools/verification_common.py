"""Shared provenance and exclusive-output helpers for independent verification."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import resource

ROOT = Path(__file__).resolve().parents[1]
SOFA = Path(os.environ.get('SOFA_ROOT', '/home/ubuntu/SOFA/v26.06.00'))
BUILD = Path(os.environ.get('REGRIP_BUILD_ROOT', str(ROOT/'build'))).resolve()
RUN = Path(os.environ.get('REGRIP_VERIFICATION_OUT', str(ROOT/'results/revalidation_20261114T132734Z'))).resolve()
PHYSICS = Path(os.environ.get('REGRIP_PHYSICS_OUT',str(RUN/'physics_release'))).resolve()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    paths = sorted(p for folder in ('plugin','diagnostics','tools','tests','reference_fem','scenes')
                   for p in (ROOT/folder).rglob('*')
                   if p.is_file() and p.suffix in ('.py','.cpp','.h','.txt','.scn') and '__pycache__' not in p.parts)
    return {str(p.relative_to(ROOT)): sha(p) for p in paths}


def provenance():
    def git(*args):
        return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
    return dict(git_commit=git('rev-parse','HEAD'),working_tree_dirty=bool(git('status','--porcelain')),
                source_sha256=source_hashes(),python=sys.executable)


def compiled_sources():
    paths=['plugin/CMakeLists.txt','plugin/src/TangentialRigidForceField.cpp',
           'diagnostics/CMakeLists.txt','diagnostics/PrecisionStateWriter.cpp',
           'handover/20261114/SOFA_V110_Native_Tangent/src/initPlugin.cpp',
           'tests/test_forcefield.cpp','tests/probe_forcefield.cpp']
    return {path:sha(ROOT/path) for path in paths}


def assert_build_current():
    manifest=BUILD/'build_manifest.json'
    if not manifest.is_file():raise RuntimeError('missing build manifest; run tools/build.py for this build root')
    record=json.loads(manifest.read_text())
    if record['source_sha256']!=compiled_sources():raise RuntimeError('C++ sources do not match the built binaries')
    for path,digest in record['binary_sha256'].items():
        if sha(BUILD/path)!=digest:raise RuntimeError('changed build artifact: '+path)
    return record


def write_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.partial')
    temporary.write_text(json.dumps(value,indent=2,allow_nan=False,ensure_ascii=False)+'\n')
    temporary.replace(path)


def command(label, args, timeout=90, env=None):
    directory=RUN/'commands';directory.mkdir(parents=True,exist_ok=True)
    logfile=directory/(label+'.log')
    if logfile.exists():raise FileExistsError(logfile)
    started=time.monotonic()
    with logfile.open('x') as stream:
        try:
            def limits():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
            run=subprocess.run(args,stdout=stream,stderr=subprocess.STDOUT,timeout=timeout,cwd=ROOT,env=env,preexec_fn=limits)
            code=run.returncode
        except (subprocess.TimeoutExpired,OSError) as exc:
            stream.write(str(exc)+'\n');code=None
    record=dict(command=list(map(str,args)),exit_code=code,runtime_s=time.monotonic()-started,log=str(logfile))
    write_json(directory/(label+'.json'),record)
    print(label,'exit=',code,flush=True)
    return record
