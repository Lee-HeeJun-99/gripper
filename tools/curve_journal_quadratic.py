"""Measure the derived conservative-Beam Euler projection separately."""
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT, OUT, BUILD, SDK, FRAME, BEAM, PLUGIN, PREFIX, identity, sha, write_json
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states


def main():
    out = OUT / 'transaction_journal_8s_v6'; out.mkdir(exist_ok=False)
    build = ROOT / 'build/autonomous_20261116_curve_a01/transaction_v6'
    sources = list((ROOT / 'diagnostics/transaction_energy').iterdir()) + list(
        (ROOT / 'diagnostics/contact_return_energy').iterdir()) + [ROOT / 'models/contact_energy/ReturnAudit.h']
    for p in sources:
        if p.is_file():
            target = out / 'sources' / p.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
    write_json(out / 'sources.json', {str(p.relative_to(ROOT)): sha(p) for p in sources if p.is_file()})
    for name, command in [('configure', ['cmake', '-S', 'diagnostics/transaction_energy',
            '-B', build, '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_PREFIX_PATH=' + str(PREFIX),
            '-DREGRIP_NORMAL_AUDIT=ON', '-DFROZEN_CURVE_BUILD=' + str(BUILD)]),
            ('build', ['cmake', '--build', build, '-j2'])]:
        r = logged(command, out / name, 180)
        if r['exit_code']:
            write_json(out / 'summary.json', dict(status='FAIL', stage=name, process=r)); return
    source = OUT / 'grasp/n21'; tree = ET.parse(source / 'scene.scn')
    for e in tree.getroot().iter():
        if 'filename' in e.attrib:
            e.set('filename', str(out / e.get('filename').rsplit('/', 1)[-1]))
    tree.write(out / 'scene.scn', encoding='utf-8', xml_declaration=True)
    binary = build / 'transaction_journal'
    command = list(map(str, [binary, SDK, out / 'scene.scn', 16000, out / 'energy.csv', FRAME, BEAM, PLUGIN]))
    write_json(out / 'command.json', command); write_json(out / 'identity.json', identity())
    process = execute_process(command, out, 480)
    log = (out / 'stdout.log').read_text() + (out / 'stderr.log').read_text()
    marks = [json.loads(s[len('TRANSACTIONS '):]) for s in log.splitlines() if s.startswith('TRANSACTIONS ')]
    passed = not process['exit_code'] and '[ERROR]' not in log and bool(marks); errors = {}
    if passed:
        before = [r for r in read_states(source / 'state.txt') if r['time'] <= 8+1e-8]
        after = read_states(out / 'state.txt')
        passed = len(before) == len(after)
        if passed:
            errors = {k: float(np.max(np.abs(np.array([r[k] for r in before]) -
                                              np.array([r[k] for r in after])))) for k in ('X','V','R')}
            passed &= not any(errors.values())
    write_json(out / 'summary.json', dict(status='PASS' if passed else 'FAIL', process=process,
        transactions=marks, instrumentation_state_difference=errors, binary_sha256=sha(binary),
        global_energy='BLOCKED', scope='Beam quadratic projection from actual BEGIN force '
        'Jacobian; nonlinear remainder recorded separately,not declared heat'))
    print(passed, errors)


if __name__ == '__main__':
    main()
