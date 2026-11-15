"""Independent structural-only Euler summation contrast; object never corrected."""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from curve_common import ROOT, OUT, PREFIX, identity, sha, write_json
from closure_validation_suite import logged
from curve_trial import run as prepare
from history_trial import analyze
from run_trial import execute_process
from birth_monitor import Monitor
BUILD = ROOT / 'build/autonomous_20261116_beam_compensation_a01/v1'
PLUGIN = BUILD / 'libReGripBeamTranslationCompensation.so'
SOURCES = [ROOT / 'models/beam_translation_compensation/CMakeLists.txt',
           ROOT / 'models/beam_translation_compensation/CompensatedBeamTranslations.cpp',
           ROOT / 'models/stabilization/Compensated.h',
           ROOT / 'tests/test_beam_translation_compensation.cpp']


def build():
    out = OUT / 'build_compensation_v1'; out.mkdir(parents=True, exist_ok=False)
    for p in SOURCES:
        target = out / 'sources' / p.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in SOURCES}
    write_json(out / 'source_identity.json', source_hashes)
    for name, command in [
        ('unit_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                        SOURCES[-1], '-o', out / 'unit.bin']),
        ('unit', [out / 'unit.bin']),
        ('configure', ['cmake', '-S', 'models/beam_translation_compensation', '-B', BUILD,
                       '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH='+str(PREFIX)]),
        ('build', ['cmake', '--build', BUILD, '-j2']),
        ('ldd', ['ldd', PLUGIN])]:
        result = logged(command, out / name, 180)
        if result['exit_code']:
            write_json(out / 'summary.json', dict(status='FAIL', stage=name, process=result)); return
    manifest = dict(sources=source_hashes, binary=sha(PLUGIN), runtime=identity(),
                    scope='structural free X/Z translation arithmetic only; no object/quaternion/root correction')
    write_json(BUILD / 'build_manifest.json', manifest)
    write_json(out / 'summary.json', dict(status='PASS', **manifest))
    print('compensation build/arithmetic PASS')


def run(name, dt=.0005, profile=False, wall=480, duration=18, nodes=21, history=.0025):
    manifest = json.loads((BUILD / 'build_manifest.json').read_text())
    if sha(PLUGIN) != manifest['binary'] or any(sha(ROOT/p) != h for p,h in manifest['sources'].items()):
        raise ValueError('compensation compiled source/binary changed')
    out = prepare(name, nodes=nodes, history=history, dt=dt, profile=profile, duration=duration,
                  fixed_layout=True, tributary_mass=True, prepare_only=True)
    tree = ET.parse(out / 'scene.scn'); root = tree.getroot(); body = root.find('Node')
    root.insert(0, ET.Element('RequiredPlugin', name='NumericalSummation', pluginName=str(PLUGIN)))
    config = json.loads((out / 'config.json').read_text()); obj = config['object_index']; nodes = config['nodes']
    indices = [i for i in range(obj) if i % nodes]
    component = ET.Element('CompensatedBeamTranslations', name='structuralSummation',
        indices=' '.join(map(str,indices)), objectIndex=str(obj), nodesPerLayer=str(nodes),
        filename=str(out/'compensation.csv'))
    body.insert(list(body).index(body.find('ConservativeBeam')), component)
    if list(body).index(component) >= list(body).index(body.find('CurvedMaterialContact')):
        raise ValueError('compensation must precede history Commit')
    tree.write(out / 'scene.scn', encoding='utf-8', xml_declaration=True)
    config['integration_arithmetic']='independent_structural_XZ_compensated_Euler;object_rotation_roots_untouched'
    write_json(out/'config.json',config)
    ident=json.loads((out/'identity.json').read_text());ident['structural_compensation']=manifest
    write_json(out/'identity.json',ident);command=json.loads((out/'command.json').read_text())
    monitor=Monitor(out);monitor.thread.start()
    try:process=execute_process(command,out,wall)
    finally:monitor.finish()
    write_json(out/'execution_result.json',process)
    if profile:
        log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text()
        steps=round(4/dt);result=dict(status='EXPERIMENTAL'if process['exit_code']==0 and '[ERROR]'not in log and f'{steps} iterations done'in log else'FAIL',config=config,identity=ident,process=process,scope='actual4s arithmetic contrast,not hold qualification')
    else:result=analyze(out,config,process)
    result['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()}
    write_json(out/'metrics.json',result);print(name,result['status'],process['runtime_s'],result.get('global_moment_residual'),flush=True)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('name');parser.add_argument('--dt',type=float,default=.0005);parser.add_argument('--profile',action='store_true');parser.add_argument('--wall',type=int,default=480);parser.add_argument('--duration',type=float,default=18);parser.add_argument('--nodes',type=int,default=21);parser.add_argument('--history',type=float,default=.0025);args=parser.parse_args()
    if args.name=='build':build()
    else:run(args.name,dt=args.dt,profile=args.profile,wall=args.wall,duration=args.duration,nodes=args.nodes,history=args.history)
