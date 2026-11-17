"""Immutable continuation ledger, separate from inherited v2 certification.

This verifies bytes and provenance, not physical qualification. In particular,
PASS execution, negative-guard PASS and whole-system PASS are not synonymous.
"""
import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json


def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--verify',action='store_true');p.add_argument('--min-campaign',type=int,default=147);a=p.parse_args()
    if not 147<=a.min_campaign<=999:raise ValueError('continuation campaign range147..999')
    if not re.fullmatch(r'[A-Za-z0-9_]+',a.name):raise ValueError('ledger name')
    ledger=ROOT/'reports'/('FILM_CONTACT_EVIDENCE_'+a.name+'.json')
    if a.verify:
        data=json.loads(ledger.read_text());changed=[]
        for name,expected in data['files'].items():
            path=Path(name) if Path(name).is_absolute() else ROOT/name
            if not path.is_file() or sha(path)!=expected:changed.append(name)
        print(json.dumps(dict(status='PASS' if not changed else 'FAIL',checked=len(data['files']),changed=changed,
            scope='byte integrity only;NOT physics certification',source_commit=data['source_commit'])))
        raise SystemExit(bool(changed))
    if ledger.exists():raise RuntimeError('immutable ledger exists;choose a NEW name')
    files={};campaigns={}
    def record(path):
        path=Path(path)
        try:name=str(path.relative_to(ROOT))
        except ValueError:name=str(path)
        if path.is_file():files[name]=sha(path)
    # Repository-native implementations and reports, not an invented global
    # SDK certificate. Dynamic dependency logs remain part of every trial.
    for top in ('models/film_shell','models/film_rail_tendon','models/film_native_contact',
                'models/film_sphere_contact','models/film_impact','models/rigid_impact_reference','models/film_coupled_contact','models/film_coupled_adaptive','models/film_coupled_restart','models/film_coupled_reintegrated','models/film_value_energy','diagnostics/film_coupled_reintegrated','diagnostics/film_coupled_adaptive','diagnostics/film_impact','diagnostics/film_sphere_contact','diagnostics/film_rail_tendon'):
        for path in (ROOT/top).rglob('*'):
            if path.is_file():record(path)
    for pattern in ('tools/film_*.py','tests/test_film*','tests/test_coupled*.cpp','tests/test_sustained_birth*.cpp','tests/test_persistent_contact*.cpp','tests/test_event_budget.cpp','tests/test_modal_rational.py','tests/test_surface_roundoff.cpp','tests/test_*impact*.cpp','tests/test_whole_surface*.cpp','reports/*FILM*.md',
                    'reports/AUTONOMOUS_RESEARCH_*.md','reports/REGRIP_*.md',
                    'reports/LONG_RUN_RESEARCH_CHECKPOINT.md'):
        for path in ROOT.glob(pattern):record(path)
    for directory in sorted((ROOT/'results').glob('autonomous_film_*')):
        match=re.search(r'(\d+)$',directory.name)
        if not match or not a.min_campaign<=int(match.group())<=999:continue
        summary=directory/'summary.json'
        state=json.loads(summary.read_text()) if summary.exists() else {}
        campaigns[directory.name]=dict(status=state.get('status',state.get('time_status',state.get('discrete_identity_status','NOT ASSESSED'))),
            has_prebuild_source_guard=(directory/'launch_sources.json').is_file(),
            scope=state.get('scope'),has_source_snapshot=(directory/'sources').is_dir(),
            provenance_note='Use archived identity/sources for compiled identity;post-run hashes alone do not prove launch identity')
        for path in directory.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:record(path)
        for scene in directory.rglob('scene.scn'):
            tree=ET.parse(scene)
            for node in tree.findall('RequiredPlugin'):
                for plugin in node.get('pluginName','').split():
                    if Path(plugin).is_absolute():
                        record(plugin);record(Path(plugin).parent/'CMakeCache.txt')
                        for generated in Path(plugin).parent.rglob('*'):
                            if generated.is_file() and ('value_models' in generated.parts or generated.name=='generated_value_manifest.tsv'):record(generated)
        for path in directory.rglob('command.json'):
            command=json.loads(path.read_text())
            if isinstance(command,list) and command and Path(str(command[0])).is_absolute():record(command[0])
            if isinstance(command,list) and '-B' in command:
                generated_build=Path(command[command.index('-B')+1])
                if generated_build.is_relative_to(ROOT/'build'):
                    for generated in generated_build.rglob('*'):
                        if generated.is_file() and ('value_models' in generated.parts or generated.name=='generated_value_manifest.tsv'):record(generated)
    for directory in (ROOT/'designs/visualizations').glob('film_native_*'):
        for path in directory.rglob('*'):
            if path.is_file() and 'matplotlib_cache' not in path.parts:record(path)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    write_json(ledger,dict(schema='film-continuation-byte-evidence-v1',source_commit=commit,
        scope='new research continuation;NOT whole physical/grasp certification',minimum_campaign=a.min_campaign,campaigns=campaigns,
        sdk_note='Installed and matched SDK trials are separate;inspect each identity and ldd log;no SDK edits',
        preserved_inherited_ledger='reports/FILM_CONTACT_EVIDENCE_20261116_v2.json',
        physical_status=dict(time='FAIL',whole_energy='BLOCKED',free_grasp='NOT RUN',grasp_optuna='BLOCKED'),
        files=dict(sorted(files.items()))))
    print(json.dumps(dict(ledger=str(ledger.relative_to(ROOT)),files=len(files),campaigns=len(campaigns),source_commit=commit)))


if __name__=='__main__':main()
