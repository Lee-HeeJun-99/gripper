"""Publish compact measured evidence, plots and immutable artifact hashes.

No result is regenerated from old numerical values. Raw files stay on external
disk; source, binaries, failed runs and historical-metadata deltas stay explicit.
"""
import csv,json,hashlib,subprocess,platform,re,os
from pathlib import Path
from beam_common import ROOT,OUT,BUILD,PLUGIN,identity,write_json
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def compact(x):
    if isinstance(x,dict):return {k:compact(v) for k,v in x.items() if k not in ('identity','source_identity','provenance','source_sha256','artifacts','source_sha256_snapshot')}
    if isinstance(x,list):return [compact(v) for v in x]
    return x
def main():
    evidence=ROOT/'reports/beam_evidence';evidence.mkdir(exist_ok=False);identity()
    selected=['inherited_audit/summary.json','inherited_live/summary.json','single_campaign.json','dynamic_energy/summary.json','multilayer_campaign.json','multilayer_followup.json','precision/result.json','contact_convergence_audit.json','high_resolution_resource_plan.json','memory/summary.json','wrench.json','structural_optuna/summary.json','structural_optuna/reference_gate.json','optuna_contracts/summary.json','candidate_result.json','native_lat12/recovered_result.json','native_lat12/balance.json','native_lat24/result.json','native_lat24/balance.json','replay/result.json','validation_golden/summary.json','validation_unit_dependency/summary.json','legacy_units/summary.json','clean/summary.json','extra_unit/summary.json','asan/summary.json','asan_unrestricted/summary.json','large_kernel_corrected/summary.json','profile/summary.json','v2_profile/profile/summary.json']
    selected += ['native_physical'+str(lat)+'/'+name for lat in (12,24) for name in ('result.json','balance.json')]
    selected += ['packaging_check.json']
    selected += ['native_surface_comparison.json']
    selected += ['fair_reference.json']
    for name in selected:
        p=OUT/name
        if not p.is_file():raise FileNotFoundError(p)
        write_json(evidence/name.replace('/','__'),compact(json.loads(p.read_text())))
    records=[]
    for p in sorted(OUT.rglob('metrics.json')):
        r=json.loads(p.read_text());small=compact(r);small['raw_path']=str(p.parent.relative_to(ROOT));small['record_kind']='model_trial_attempt' if p.relative_to(OUT).parts[0] in ('single','multilayer','grasp') else 'automation_fault_injection_not_physics_qualification';small['metrics_sha256']=digest(p);small['compiled_binary_sha256']=r.get('identity',{}).get('plugin_sha256');small['compiled_source_sha256']=r.get('identity',{}).get('compiled_source_sha256',{});write_json(evidence/(str(p.parent.relative_to(OUT)).replace('/','__')+'.json'),small);records.append(small)
    fields=['raw_path','record_kind','status','equilibrium_validated','tip_deflection_mm','max_interface_slip_mm','relative_residual','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','bounded_hold_pass','recovery_pass','failure_reason','compiled_binary_sha256','metrics_sha256']
    for filename,kind in [('actual_sofa_trials.csv','model_trial_attempt'),('automation_trial_records.csv','automation_fault_injection_not_physics_qualification')]:
        with (evidence/filename).open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(r for r in records if r['record_kind']==kind)
    for folder in ('prototype','v2'):write_json(evidence/(folder+'_compiled_manifest.json'),json.loads((BUILD/folder/'build_manifest.json').read_text()))
    pairs=[('two_fixed_layer_section','L2_k0','L2_k100'),('four_fixed_layer_section','L4_k0','L4_k100'),('eight_same_compensated_scheme','L8_free_compensated','L8_k100_compensated'),('four_equal_total_material','L4_equal_total_free','L4_equal_total')];ratios={}
    for label,off,on in pairs:
        a=json.loads((OUT/'multilayer'/off/'metrics.json').read_text());b=json.loads((OUT/'multilayer'/on/'metrics.json').read_text());ok=a['status']=='PASS' and b['status']=='PASS';ratios[label]=dict(status='PASS' if ok else 'FAIL',ratio=a['tip_deflection_mm']/b['tip_deflection_mm'] if ok else None,off=off,on=on,origin='arithmetic of matched actual SOFA equilibrium values, elastic coupling not vacuum grasp benefit')
    write_json(evidence/'matched_structural_ratios.json',ratios)
    # Historical strict verifier must identify metadata changes instead of
    # rewriting its manifest to pretend all current sources still match.
    previous=json.loads((ROOT/'reports/CLOSURE_EVIDENCE_MANIFEST.json').read_text());checks=0;errors=[];expected=[]
    for group in ('source_sha256','binary_sha256','runtime_sha256','report_sha256','evidence_sha256'):
        for name,h in previous[group].items():
            path=Path(name) if Path(name).is_absolute() else ROOT/name;checks+=1
            if not path.is_file() or digest(path)!=h:
                (expected if group=='source_sha256' and name in ('.gitignore','README.md','AGENTS.md') else errors).append(group+':'+name)
    for name,r in previous['raw_files'].items():
        p=Path(previous['raw_root'])/name;checks+=1
        if not p.is_file() or p.stat().st_size!=r['bytes'] or digest(p)!=r['sha256']:errors.append('raw:'+name)
    write_json(evidence/'historical_preservation.json',dict(status='PASS' if not errors else 'FAIL',checked=checks,unexpected_errors=errors,expected_metadata_deltas=expected,strict_previous_manifest_current_tree_status='FAIL' if expected or errors else 'PASS',scope='historical source/binary/runtime/report/evidence/raw integrity; metadata deltas do not certify new physics'))
    os.environ.setdefault('MPLCONFIGDIR',str(OUT/'matplotlib_cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(12,3.5));single=json.loads((OUT/'single_campaign.json').read_text());axes[0].plot([11,21,41],[-single['force'+str(n)]['tip_displacement'][2] for n in (11,21,41)],'o-');axes[0].set(xlabel='Beam nodes',ylabel='Tip deflection (mm)',title='Actual SOFA cantilever')
    cv=json.loads((OUT/'contact_convergence_audit.json').read_text());subset=cv['comparisons'][1:7];axes[1].bar(range(len(subset)),[100*x['relative_errors']['hold_displacement_mm'] for x in subset]);axes[1].set_xticks(range(len(subset)),['q8-16','q16-32','n11-21','n21-41','dt/2','hist/2'],rotation=40);axes[1].set(ylabel='Translation difference (%)',title='Actual SOFA diagnostic errors');axes[1].axhline(1,color='red',ls='--',label='space/history 1%');axes[1].legend(fontsize=6)
    mem=json.loads((OUT/'memory/summary.json').read_text());rows=[r for r in mem['rows'] if r['phase']=='animated'];axes[2].plot([r['cycle']*60000+r['step'] for r in rows],[r['live_heap']/1024**2 for r in rows],'o-',label='live heap');axes[2].plot([r['cycle']*60000+r['step'] for r in rows],[r['rss_kib']/1024 for r in rows],label='RSS');axes[2].set(xlabel='Total steps across two cycles',ylabel='MiB',title='Matched SDK full-scene scope');axes[2].legend(fontsize=7);fig.tight_layout();fig.savefig(evidence/'measured_comparison.png',dpi=150);plt.close(fig)
    code=[p for pattern in ('models/conservative_beam/**/*','diagnostics/conservative_beam/*','tools/beam_*.py','tests/test_beam*','tests/test_conservative*','tests/conservative_beam/*','scenes/beam_*') for p in ROOT.glob(pattern) if p.is_file() and '__pycache__' not in p.parts];code += [ROOT/p for p in ('models/finite_rotation/Kernel.h','AGENTS.md','README.md','.gitignore')]
    reports=[p for pattern in ('BEAM_*.md','CONSERVATIVE_BEAM_*.md') for p in (ROOT/'reports').glob(pattern)];binaries=[PLUGIN,BUILD/'prototype/libReGripConservativeBeam.so',BUILD/'clean_final/libReGripConservativeBeam.so',BUILD/'native_beam/libReGripConservativeBeam.so',BUILD/'native_frame/libReGripFrameClosure.so',ROOT/'build/closure_20261115/frame/libReGripFrameClosure.so',ROOT/'build/grasp_20261115/sofa_patched/bin/graph_probe']
    raw={str(p.relative_to(ROOT)):dict(bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(OUT.rglob('*')) if p.is_file()}
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();manifest=dict(baseline_commit='b468346f3277369d92f25cd2f5d5044c29124737',verified_code_commit=commit,branch='development/regrip-conservative-beam-grasp',git_dirty_at_publication=bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)),source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(set(code))},report_sha256={str(p.relative_to(ROOT)):digest(p) for p in sorted(reports)},binary_sha256={str(p.relative_to(ROOT)):digest(p) for p in binaries},evidence_sha256={str(p.relative_to(ROOT)):digest(p) for p in evidence.iterdir() if p.is_file()},raw_files=raw,physical_qualification='FAIL',grasp_optimization='BLOCKED',origins=['actual SOFA','independent linear FEM','mathematical kernel analysis','assumed research parameters'],real_measurements=0,environment=dict(kernel=platform.platform(),python=platform.python_version(),workspace=str(ROOT)),provenance_caveat='queued prototype trials may contain v2 working-tree snapshots; git4d19774 anchored prototype binary/compiled manifest is authoritative; no mixed-version study qualification')
    runtime=dict(previous['runtime_sha256'])
    for p in OUT.rglob('stdout.log'):
        if 'ldd' not in str(p.relative_to(OUT)).lower():continue
        for line in p.read_text(errors='replace').splitlines():
            match=re.search(r'=> (/[^ ]+)',line)
            if match and Path(match[1]).is_file():runtime[match[1]]=digest(match[1])
    for relative in ('.runtime/sofa-source/Sofa/framework/Simulation/Core/src/sofa/simulation/MappingGraph.h','.runtime/sofa-source/Sofa/framework/Simulation/Core/src/sofa/simulation/MappingGraph.cpp'):
        runtime[relative]=digest(ROOT/relative)
    manifest['runtime_sha256']=runtime;manifest['sdk_source_origin']='archive matched to installed git-info7c18e95d5c5f2839079892c69e7d89a313c79603, official weak-parent patch; source archive is not a separate Git checkout';write_json(ROOT/'reports/CONSERVATIVE_BEAM_EVIDENCE_MANIFEST.json',manifest);print(dict(raw_files=len(raw),raw_bytes=sum(x['bytes'] for x in raw.values()),trial_records=len(records),historical_errors=errors))
if __name__=='__main__':main()
