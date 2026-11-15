"""Exercise the synchronized journal through cable, pressure and applied torque.

This is an instrumentation test, not global stored-energy certification.
"""
import csv
import json
import shutil
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT, OUT, SDK, FRAME, BEAM, PLUGIN, identity, sha, write_json
from run_trial import execute_process
from trial_validation import read_states


def main():
    out = OUT / 'transaction_journal_8s_v3'
    out.mkdir(exist_ok=False)
    source = OUT / 'grasp/n21'
    binary = ROOT / 'build/autonomous_20261116_curve_a01/transaction_v3/transaction_journal'
    frozen = ROOT / 'results/autonomous_20261116_curve_a01/transaction_journal_v3'
    for p in (ROOT / 'diagnostics/transaction_energy').iterdir():
        if p.is_file():
            if sha(p) != sha(frozen / p.name):
                raise ValueError('journal binary/source snapshot no longer matched')
            shutil.copy2(p, out / p.name)
    tree = ET.parse(source / 'scene.scn')
    for e in tree.getroot().iter():
        if 'filename' in e.attrib:
            e.set('filename', str(out / e.get('filename').rsplit('/', 1)[-1]))
    tree.write(out / 'scene.scn', encoding='utf-8', xml_declaration=True)
    steps = 16000
    command = list(map(str, [binary, SDK, out / 'scene.scn', steps,
                            out / 'energy.csv', FRAME, BEAM, PLUGIN]))
    write_json(out / 'command.json', command)
    write_json(out / 'identity.json', identity())
    process = execute_process(command, out, 480)
    log = (out / 'stdout.log').read_text() + (out / 'stderr.log').read_text()
    markers = [json.loads(s[len('TRANSACTIONS '):]) for s in log.splitlines()
               if s.startswith('TRANSACTIONS ')]
    errors = {}
    passed = not process['exit_code'] and '[ERROR]' not in log and bool(markers)
    rows = []
    if passed:
        with (out / 'energy.csv').open() as f:
            rows = list(csv.DictReader(f))
        before = [r for r in read_states(source / 'state.txt') if r['time'] <= 8 + 1e-8]
        after = read_states(out / 'state.txt')
        passed = len(before) == len(after) and len(rows) == 3 * steps
        if len(before) == len(after):
            errors = {k: float(np.max(np.abs(np.array([r[k] for r in before]) -
                                               np.array([r[k] for r in after]))))
                      for k in ('X', 'V', 'R')}
            passed &= all(v < 1e-12 for v in errors.values())
    write_json(out / 'summary.json', dict(
        status='PASS' if passed else 'FAIL', process=process, transactions=markers,
        raw_rows=len(rows), instrumentation_state_difference=errors,
        binary_sha256=sha(binary), global_energy='BLOCKED',
        unknown_terms=['pressure parameter work', 'per-step friction', 'stored-energy closure'],
        scope='actual eight seconds includes wire ramp, pressure ramp and applied torque; '
              'synchronized kinetic algorithmic identity is not global energy closure'))
    print(passed, errors, markers)


if __name__ == '__main__':
    main()
