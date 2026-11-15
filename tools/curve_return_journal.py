"""Read-only actual SOFA pre-Commit radial-return energy diagnostic."""
import csv
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT, OUT, BUILD, SDK, FRAME, BEAM, PLUGIN, PREFIX, identity, sha, write_json
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states


def main():
    out = OUT / 'return_journal_v4'
    out.mkdir(exist_ok=False)
    build = ROOT / 'build/autonomous_20261116_return_energy_a01/v4'
    sources = list((ROOT / 'diagnostics/contact_return_energy').iterdir()) + [
        ROOT / 'models/contact_energy/ReturnAudit.h', ROOT / 'tests/test_return_energy.cpp']
    for p in sources:
        if p.is_file():
            shutil.copy2(p, out / p.name)
    write_json(out / 'source_identity.json', {str(p.relative_to(ROOT)): sha(p) for p in sources if p.is_file()})
    write_json(out / 'identity.json', identity())
    commands = [
        ('unit_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                        ROOT / 'tests/test_return_energy.cpp', '-o', out / 'unit_test']),
        ('unit', [out / 'unit_test']),
        ('configure', ['cmake', '-S', 'diagnostics/contact_return_energy', '-B', build,
                       '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(PREFIX),
                       '-DFROZEN_CURVE_BUILD=' + str(BUILD)]),
        ('build', ['cmake', '--build', build, '-j2']),
        ('symbols', ['nm', '-D', '--defined-only', '--demangle', build / 'libContactReturnBridge.so']),
        ('ldd', ['ldd', build / 'contact_return_journal'])]
    for name, command in commands:
        result = logged(command, out / name, 180)
        if result['exit_code']:
            write_json(out / 'summary.json', dict(status='FAIL', stage=name, process=result))
            return
    symbols = (out / 'symbols/stdout.log').read_text()
    if 'regrip_integrated::' in symbols or 'CurvedMaterialContact' in symbols:
        raise ValueError('unsafe symbol interposition')
    source = OUT / 'grasp/n21'
    tree = ET.parse(source / 'scene.scn')
    for e in tree.getroot().iter():
        if 'filename' in e.attrib:
            e.set('filename', str(out / e.get('filename').rsplit('/', 1)[-1]))
    tree.write(out / 'scene.scn', encoding='utf-8', xml_declaration=True)
    command = list(map(str, [build / 'contact_return_journal', SDK, out / 'scene.scn',
                            16000, out / 'return.csv', FRAME, BEAM, PLUGIN]))
    write_json(out / 'command.json', command)
    write_json(out / 'binary_identity.json', {p.name: sha(p) for p in [
        build / 'contact_return_journal', build / 'libContactReturnBridge.so']})
    process = execute_process(command, out, 480)
    log = (out / 'stdout.log').read_text() + (out / 'stderr.log').read_text()
    markers = [json.loads(s[len('RETURN_AUDIT '):]) for s in log.splitlines()
               if s.startswith('RETURN_AUDIT ')]
    passed = not process['exit_code'] and '[ERROR]' not in log and bool(markers)
    errors = {}
    count = 0
    if passed:
        with (out / 'return.csv').open() as f:
            count = sum(1 for _ in csv.DictReader(f))
        before = [r for r in read_states(source / 'state.txt') if r['time'] <= 8 + 1e-8]
        after = read_states(out / 'state.txt')
        passed = len(before) == len(after) and count == 16000
        if len(before) == len(after):
            errors = {k: float(np.max(np.abs(np.array([r[k] for r in before]) -
                                               np.array([r[k] for r in after]))))
                      for k in ('X', 'V', 'R')}
            passed &= all(v < 1e-12 for v in errors.values())
        passed &= markers[-1]['max_residual'] < 1e-18
    write_json(out / 'summary.json', dict(
        status='PASS' if passed else 'FAIL', process=process, actual_rows=count,
        transactions=markers, instrumentation_state_difference=errors,
        global_energy='BLOCKED', scope='actual pre-Commit immutable material-point '
        'radial-return identity; derived endpoint term is not fitted heat; '
        'material increment work is not yet identified with global nodal work'))
    print(passed, markers, errors)


if __name__ == '__main__':
    main()
