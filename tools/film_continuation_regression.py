"""Selected bounded regression,not a whole-system qualification campaign."""
import argparse,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',help='Explicit completed new-build case,not inherited binaries');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    build=ROOT/'build/film_native_20261117_sphere_bdf_short345';commands={
        'python_geometry':['env','PYTEST_DISABLE_PLUGIN_AUTOLOAD=1',sys.executable,'-m','pytest','-q',ROOT/'tests/test_film_surface_distance.py'],
        'fresh_factor':[ROOT/'build/film_native_core_20261117_sphere_bdf_short345/test_film_native_be'],
        'assembly_api':[ROOT/'build/film_native_assembly_20261117_local_probe293/test_film_rail_tendon_api'],
        **{name:[build/name] for name in ('test_film_coupled_plane','test_film_coupled_contacts','test_film_sphere_step','test_film_sphere_bdf')},
        'historical_integrity':[sys.executable,ROOT/'tools/film_contact_evidence.py','--verify-historical'],
        'older_integrity':[sys.executable,ROOT/'tools/film_contact_evidence.py','--audit-old'],
        'patch_whitespace':['git','-C',ROOT,'diff','--check']}
    if a.case:
        source=ROOT/'results'/('autonomous_film_'+a.case)
        summary=json.loads((source/'summary.json').read_text());identity=json.loads((source/'identity.json').read_text())
        if summary.get('status')!='PASS' or not summary.get('finite'):raise ValueError('complete fresh-build qualification required')
        tree=ET.parse(source/'1/scene.scn');plugins={Path(n.get('pluginName','')).name:Path(n.get('pluginName','')) for n in tree.findall('RequiredPlugin')}
        core=plugins['libReGripFilmShell.so'];assembly=plugins['libReGripFilmRailTendon.so'];observer=plugins['libReGripFilmNativeObserver.so'];build=observer.parent
        for path,key in ((core,'core_sha256'),(assembly,'assembly_sha256'),(observer,'observer_sha256')):
            if sha(path)!=identity[key]:raise ValueError('qualified binary drift')
        commands['fresh_factor']=[core.parent/'test_film_native_be'];commands['assembly_api']=[assembly.parent/'test_film_rail_tendon_api']
        for name in ('test_film_coupled_plane','test_film_coupled_contacts','test_film_sphere_step','test_film_sphere_bdf','test_film_candidate_closure'):commands[name]=[build/name]
        commands['test_film_control_profile']=[assembly.parent/'test_film_control_profile']
    stages={};binaries={}
    for name,command in commands.items():
        stages[name]=logged(command,out/name,90)
        for item in command:
            if hasattr(item,'is_file') and item.is_file():binaries[str(item)]=sha(item)
    result=dict(status='PASS' if all(v['exit_code']==0 for v in stages.values()) else 'FAIL',scope='selected compiled API/math/geometry/inherited-byte regression;NOT all45 physics gates or grasp certification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__),stages=stages,command_file_identities=binaries,
        pytest_note='Third-party autoload disabled because ambient anyio/system pytest versions conflict;no dependencies or SDK changed')
    write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],tests={k:v['exit_code'] for k,v in stages.items()})))
if __name__=='__main__':main()
