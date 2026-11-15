"""Cold-start one-factor material refinement through the observed slip transient.

No checkpoint restart, no reduced load, no change to gates. This prefix is NOT
a full release/grasp qualification; it tests the independently observed 7--8.2s band.
"""
import argparse
import json
import shutil
import xml.etree.ElementTree as ET
from curve_common import ROOT, OUT, identity, sha, write_json
from curve_phase_grid import count
from curve_cycle_loss import sample
from run_trial import execute_process
from birth_monitor import Monitor


def immutable(value):
    """Exclude only Git/worktree provenance, never compiled/runtime hashes."""
    if isinstance(value, dict):
        return {key: immutable(item) for key, item in value.items() if key != 'provenance'}
    if isinstance(value, list):
        return [immutable(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', action='store_true')
    parser.add_argument('--full', action='store_true')
    args = parser.parse_args()
    if args.profile and args.full:raise ValueError('distinct profile/full modes')
    duration = 4 if args.profile else 24 if args.full else 8.2
    out = OUT / ('history1000nm_profile4_v1' if args.profile else 'history1000nm_full24_v1' if args.full else 'history1000nm_prefix82_v1')
    out.mkdir(exist_ok=False)
    source = OUT / 'full_coarse_history1250nm'
    prior = json.loads((source / 'metrics_same_grid_v2.json').read_text())
    if not prior['bounded_hold_pass'] or not prior['recovery_pass']:
        raise ValueError('actual parent physics prerequisite')
    runtime = identity()
    for key in ('curved', 'inherited'):
        if immutable(runtime[key]) != immutable(prior['identity'][key]):
            raise ValueError('compiled physical model mismatch ' + key)
    steps = count(duration, .0005)
    prediction = None
    wall = 480
    if not args.profile:
        profile = json.loads((OUT / ('history1000nm_prefix82_v1'if args.full else'history1000nm_profile4_v1') / 'summary.json').read_text())
        if profile['status'] != 'PASS':
            raise ValueError('own cold-start profile prerequisite')
        prediction = profile['process']['runtime_s'] * steps / profile['steps'] * 1.2
        bound=1320 if args.full else 900
        wall = 480 if prediction <= 480 else 900 if prediction<=900 else bound
        if prediction > bound:
            write_json(out / 'summary.json', dict(status='BLOCKED', reason=f'own profile exceeds bounded{bound}s policy;not actual system timeout', prediction=prediction,attempts=0))
            return
    tree = ET.parse(source / 'scene.scn')
    contact = tree.getroot().find('.//CurvedMaterialContact')
    if contact is None or float(contact.get('historySpacing')) != .00125:
        raise ValueError('exact parent material spacing')
    # Frozen component has a .001mm minimum plus a separate one-million-site
    # bound. Preserve both guards; the rejected .000625 run is retained.
    contact.set('historySpacing', '.001')
    for element in tree.getroot().iter():
        if 'filename' in element.attrib:
            element.set('filename', str(out / element.get('filename').rsplit('/', 1)[-1]))
    tree.write(out / 'scene.scn', encoding='utf-8', xml_declaration=True)
    command = json.loads((source / 'command.json').read_text())
    command[2], command[3] = str(out / 'scene.scn'), str(steps)
    shutil.copy2(__file__, out / 'RunnerSource.py')
    write_json(out / 'identity.json', dict(runtime=runtime, parent_metrics_sha256=sha(source / 'metrics_same_grid_v2.json'), parent_scene_sha256=sha(source / 'scene.scn'), source_sha256=sha(out / 'RunnerSource.py')))
    write_json(out / 'command.json', command)
    config=json.loads((source/'config.json').read_text());config.update(duration=duration,history_spacing=.001,actual_steps=steps,profile_only=not args.full)
    write_json(out/'config.json',config)
    write_json(out / 'resource_decision.json', dict(wall=wall, prediction=prediction, memory=4294967296, attempts=1))
    monitor = Monitor(out)
    monitor.thread.start()
    try:
        process = execute_process(command, out, wall)
    finally:
        monitor.finish()
    log = (out / 'stdout.log').read_text() + (out / 'stderr.log').read_text()
    passed = process['exit_code'] == 0 and '[ERROR]' not in log and f'{steps} iterations done' in log
    phases = {}
    if passed:
        endpoints = (0, .5, 2, 3, 4) if args.profile else (0, .5, 2, 3, 4, 6, 7, 8.2,14,15,16,16.5,18,24)if args.full else (0, .5, 2, 3, 4, 6, 7, 8.2)
        for left, right in zip(endpoints[:-1], endpoints[1:]):
            phases[f'{left}_{right}'] = sample(out, right)['total'] - sample(out, left)['total']
    if args.full:
        from curve_event_grid import analyze
        physical=analyze(out,config,process);write_json(out/'metrics.json',physical)
    write_json(out / 'summary.json', dict(status='PASS' if passed else 'FAIL', process=process, steps=steps, duration=duration, history_spacing_mm=.001, phase_losses_Fmm=phases, scope='actual bounded cold-start prefix execution ONLY;not convergence/full grasp/release approval'))
    print(passed, process, phases, flush=True)


if __name__ == '__main__':
    main()
