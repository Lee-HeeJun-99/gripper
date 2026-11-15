"""Publish measured small evidence/plots and a read-only integrity manifest.

No simulation or success fabrication: snapshots are copies, CSVs are projections
of metrics, figures read recorded states. Raw data stay ignored on external disk.
"""
import csv,json,subprocess,platform,shutil,hashlib
from pathlib import Path
from grasp_common import ROOT,OUT,BUILD,SOFA,write_json

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    evidence=ROOT/'reports/grasp_evidence';evidence.mkdir(exist_ok=True)
    selected=['gate.json','fast_campaign.json','final_sequence.json','directions.json','directions_settled.json','remaining.json','release_criteria.json','fem/summary.json','optuna_v2/summary.json','optuna_v2/mechanisms.json','optuna_v2/commands.json','candidate_extra/summary.json','python_recovery/summary.json','python_xml_compare/summary.json','sdk_regression_v2/summary.json','sdk_probe/result.json','audits/sdk_memory/result.json','audits/beam/result.json','sanitizer/summary.json','sanitizer/commands.json','final_checks/result.json','final_checks/structural.json','python_tests_isolated/result.json','python_tests_isolated/command.json','legacy_units/summary.json','legacy_units_v2/summary.json','visualization_final/result.json','visualization_final_v2/result.json','native_surface/result.json','native_surface_v2/result.json','native_surface_v3/result.json','native_surface_v4/result.json','native_surface_v5/result.json','sdk_build/result.json','sdk_build_resume/result.json']
    selected+=['sanitizer/'+n+'.log' for n in ('configure','build','asan_ubsan','lsan')]
    selected+=['final_checks/'+str(i)+'/'+n for i in range(3) for n in ('command.json','stdout.log','stderr.log')]
    selected+=['python_tests_isolated/tests.log','final_checks/python_tests.log','audits/beam/stdout.log','audits/sdk_memory/stdout.log','sdk_probe/ldd.log','sdk_probe/stdout.log','visualization_final_v2/gui_command.json','visualization_final_v2/environment.json','visualization_final_v2/stdout.log','visualization_final_v2/stderr.log']
    selected+=[str(p.relative_to(OUT)) for p in (OUT/'trials').glob('*/metrics.json')]
    selected+=[str(p.relative_to(OUT)) for p in (OUT/'structural').glob('*/metrics.json')]
    selected+=[str(p.relative_to(OUT)) for p in (OUT/'optuna_v2/actual').glob('pareto_00021*/*/metrics.json')]
    for name in selected:
        source=OUT/name
        if not source.is_file():continue
        if source.stat().st_size>800000:raise ValueError('small evidence cap: '+name)
        destination=evidence/name.replace('/','__');shutil.copy2(source,destination)
    shutil.copy2(ROOT/'.runtime/MappingGraph.patch',evidence/'official_PR6259.patch')
    cache=BUILD/'sofa_patched/CMakeCache.txt';shutil.copy2(cache,evidence/'patched_CMakeCache.txt')
    records={p.parent.name:json.loads(p.read_text()) for p in (OUT/'trials').glob('*/metrics.json')}
    versions={}
    for folder,commit in [('stick','6b838c5'),('stick_v2','9395845'),('stick_v4','3f0b735')]:
        binary=BUILD/folder/'libReGripStickSlip.so';h=digest(binary);sources={}
        for source in ('models/grasp/StickSlip.h','models/grasp/StickSlip.cpp'):
            content=subprocess.check_output(['git','show',commit+':'+source],cwd=ROOT);sources[source]=hashlib.sha256(content).hexdigest()
        versions[h]=dict(binary=str(binary.relative_to(ROOT)),source_commit=commit,compiled_core_sha256=sources,trials=[])
    for name,r in records.items():
        version=versions[r['identity']['binary_sha256']]
        for source,h in version['compiled_core_sha256'].items():
            if r['identity']['source_sha256'][source]!=h:raise ValueError('source/binary version mismatch: '+name)
        version['trials'].append(name)
    write_json(evidence/'binary_source_versions.json',versions)
    fields=['trial','status','execution_completed','bounded_hold_pass','hold_displacement_mm','object_force_residual','object_moment_residual','object_speed','release_contacts','friction_dissipation']
    with (evidence/'measured_trials.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for name,r in sorted(records.items()):writer.writerow(dict(trial=name,**{k:r.get(k) for k in fields[1:]}))
    environment=dict(os=platform.platform(),python=platform.python_version(),campaign=str(OUT),sofa=str(SOFA),commands={})
    for label,command in [('kernel',['uname','-a']),('compiler',['g++','--version']),('cmake',['cmake','--version']),('storage',['df','-h',str(ROOT),'/home/ubuntu']),('memory',['free','-h']),('cpu',['nproc'])]:
        p=subprocess.run(command,capture_output=True,text=True,timeout=10);environment['commands'][label]=dict(command=command,exit_code=p.returncode,stdout=p.stdout)
    write_json(evidence/'environment.json',environment)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from trial_validation import read_states
    figures=ROOT/'reports/grasp_figures';figures.mkdir(exist_ok=True)
    fig,axes=plt.subplots(1,2,figsize=(10,3.6),layout='constrained')
    names=['settled_sphere_xplus','sphere_q16','sphere_q32','sphere_n21q16','fast_n21q32','fast_n41q16','fast_n41q32']
    axes[0].plot(range(len(names)),[records[n]['hold_displacement_mm'] for n in names],'o-');axes[0].set_xticks(range(len(names)),['11/8','11/16','11/32','21/16','21/32','41/16','41/32'],rotation=35);axes[0].set(xlabel='beam nodes / segment subdivisions',ylabel='held displacement [mm]',title='SOFA: spatial convergence NOT established')
    for a in 'xyz':
        r=records['final_sphere_'+a+'plus'];axes[1].bar(a,r['hold_displacement_mm'])
    axes[1].set(ylabel='held displacement [mm]',title='SOFA: same-condition positive directions')
    fig.savefig(figures/'convergence_and_directions.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,3.5),layout='constrained')
    for a in 'xyz':
        name='final_sphere_'+a+'plus';raw=read_states(OUT/'trials'/name/'state.txt');obj=records[name]['config']['object_index'];t=[p['time'] for p in raw];origin=raw[0]['X'][7*obj:7*obj+3];delta=[sum((p['X'][7*obj+j]-origin[j])**2 for j in range(3))**.5 for p in raw];ax.plot(t,delta,label=a+' load')
    for t,label in [(6,'load ON'),(14,'load OFF'),(15,'jam OFF'),(16,'cable OFF')]:ax.axvline(t,color='grey',lw=.6);ax.text(t,ax.get_ylim()[1]*.95,label,rotation=90,va='top',fontsize=7)
    ax.set(xlabel='recorded SOFA time [s]',ylabel='object translation from initial [mm]',title='Free object is NOT reset after release');ax.legend();fig.savefig(figures/'measured_sequence.png',dpi=150);plt.close(fig)
    # Every raw file, including failures and SQLite, is covered. No writers may
    # run concurrently with this final snapshot.
    raw={str(p.relative_to(OUT)):dict(sha256=digest(p),bytes=p.stat().st_size) for p in sorted(OUT.rglob('*')) if p.is_file() and not p.name.endswith('.partial')}
    sources={str(p.relative_to(ROOT)):digest(p) for folder in ('models','diagnostics','tools','tests','scenes') for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.cpp','.h','.txt','.scn','.md','.patch')}
    sources.update({n:digest(ROOT/n) for n in ('AGENTS.md','README.md','PROGRESS.md','VALIDATION.md','.gitignore')})
    binaries={str(p.relative_to(ROOT)):digest(p) for p in sorted(BUILD.rglob('*')) if p.is_file() and (p.name in ('test_grasp_stick','memory_lifetime','graph_probe','beam_energy_probe') or p.name.endswith('.so') or '.so.26.06' in p.name) and not p.is_symlink()}
    reports={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/'reports').glob('GRASP_*.md')}
    small={str(p.relative_to(ROOT)):digest(p) for directory in (evidence,figures) for p in directory.iterdir() if p.is_file()}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    external=[ROOT/'.runtime/sofa-source.tar.gz',ROOT/'.runtime/MappingGraph.patch',ROOT/'.runtime/python312/lib/libpython3.12.so.1.0',SOFA/'bin/runSofa-26.06.00',SOFA/'plugins/SofaPython3/lib/libSofaPython3.so']
    external += [ROOT/'.runtime/sofa-source/Sofa/framework/Simulation/Core/src/sofa/simulation'/p for p in ('MappingGraph.cpp','mappinggraph/BaseMappingGraphNode.h','mappinggraph/BaseMappingGraphNode.cpp')]
    write_json(ROOT/'reports/GRASP_EVIDENCE_MANIFEST.json',dict(schema=1,start_commit='9b95d0c03e0557829ec3f6bab095935144bb9a63',evidence_code_commit=commit,git_dirty=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),branch='development/regrip-validated-grasp',raw_root=str(OUT),source_sha256=sources,binary_sha256=binaries,external_runtime_sha256={str(p):digest(p) for p in external},report_sha256=reports,evidence_sha256=small,raw_files=raw,full_grasp_certified=False,classification='SOFA execution / independent FEM / mathematics / assumed research parameters; real measurements=0',note='final documentation commit is a descendant of evidence_code_commit; manifest excludes its own self-hash'))
    print('PUBLISHED',len(records),'trials,',len(raw),'raw files,',sum(r['bytes'] for r in raw.values()),'raw bytes')
if __name__=='__main__':main()
