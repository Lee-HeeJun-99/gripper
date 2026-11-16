"""Seal/verify a NEW immutable vector-history cohort;never rewrite old indices."""
import argparse
import hashlib
import json
import platform
import subprocess
from pathlib import Path
from curve_common import ROOT,sha


def git_blob(commit,name):
    return hashlib.sha256(subprocess.check_output(['git','show',commit+':'+name],cwd=ROOT)).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--verify',action='store_true');args=p.parse_args()
    if not args.version.replace('_','').isalnum():raise ValueError('simple new index version')
    destination=ROOT/'reports/vector_history'/('manifest_'+args.version+'.json')
    if args.verify:
        data=json.loads(destination.read_text());errors=[]
        for name,expected in data['files'].items():
            file=Path(name)if name.startswith('/')else ROOT/name
            if not file.is_file()or sha(file)!=expected:errors.append(name)
        for name,expected in data['git_source_sha256'].items():
            if git_blob(data['source_commit'],name)!=expected:errors.append('git:'+name)
        result=dict(status='FAIL'if errors else'PASS',artifacts=len(data['files']),source_blobs=len(data['git_source_sha256']),errors=errors,scope='fixed-cohort integrity ONLY;physical failures unchanged')
        print(json.dumps(result));raise SystemExit(bool(errors))
    if destination.exists():raise ValueError('refuse existing evidence index')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    sources=[p for p in (ROOT/'models/yield_front_history').glob('*')if p.is_file()]
    sources+=list((ROOT/'tests').glob('test_vector_*.cpp'))+list((ROOT/'tools').glob('curve_vector_*.py'))
    sources += [ROOT/'models/contact_energy/SlipBandReference.h']
    sources += [ROOT/'tools'/n for n in ('run_trial.py','closure_validation_suite.py','curve_common.py','research_common.py','birth_common.py','history_common.py','beam_common.py','closure_common.py','verification_common.py')]
    source_hash={}
    for file in sources:
        name=str(file.relative_to(ROOT));actual=sha(file)
        if git_blob(commit,name)!=actual:raise ValueError('commit source before sealing: '+name)
        source_hash[name]=actual
    files={};outcomes={}
    def add(file):
        file=file.resolve()
        name=str(file.relative_to(ROOT))if file.is_relative_to(ROOT)else str(file)
        files[name]=sha(file)
    for directory in sorted((ROOT/'results').glob('vector_history_*')):
        if not directory.is_dir():continue
        for file in directory.rglob('*'):
            if file.is_file()and not file.is_symlink():add(file)
        summary=directory/'summary.json'
        if summary.exists():
            result=json.loads(summary.read_text());outcomes[directory.name]=dict(status=result.get('status'),stage=result.get('stage'),scope=result.get('scope'),actual_commits=result.get('actual_commits'))
        for runtime in [directory/'runtime.json',directory/'required_runtime.json']:
            if runtime.exists():
                for record in json.loads(runtime.read_text()).values():
                    file=Path(record['path'])
                    if sha(file)!=record['sha256']:raise ValueError('runtime dependency changed: '+str(file))
                    add(file)
        identity=directory/'identity.json'
        if identity.exists():
            data=json.loads(identity.read_text())
            if 'driver_sha256'in data:
                driver=Path(data['sdk'])/'bin/graph_probe'
                if sha(driver)!=data['driver_sha256']:raise ValueError('SDK driver changed')
                add(driver)
    for build in (ROOT/'build').glob('vector_history_sdk_*'):
        for name in ('libReGripVectorPatchReference.so','test_vector_patch','CMakeCache.txt'):
            file=build/name
            if file.is_file():add(file)
        for name in ('flags.make','link.txt'):
            for file in build.rglob(name):add(file)
    for file in sources:add(file)
    for name in ('cpp_int.hpp','cpp_dec_float.hpp'):
        file=Path('/usr/include/boost/multiprecision')/name
        if file.exists():add(file)
    add(Path('/usr/include/boost/version.hpp'))
    add(ROOT/'reports/vector_history/ROUNDING_MODEL.md')
    add(ROOT/'.runtime/sofa-source/Sofa/Component/ODESolver/Backward/src/sofa/component/odesolver/backward/NewmarkImplicitSolver.cpp')
    data=dict(schema=1,source_commit=commit,git_source_sha256=source_hash,files=files,outcomes=outcomes,
        environment=dict(platform=platform.platform(),python=platform.python_version(),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],cmake=subprocess.check_output(['cmake','--version'],text=True).splitlines()[0]),
        scope='immutable explicit cohort ONLY;future outputs excluded. PASS integrity is not PASS physics. Includes actual failed builds/API/limits/conditioning. Fixed-normal benchmark is NOT moving3Dcontact/grasp/Optuna certification.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with destination.open('x')as stream:json.dump(data,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps(dict(index=str(destination),artifacts=len(files),source_blobs=len(source_hash))))


if __name__=='__main__':main()
