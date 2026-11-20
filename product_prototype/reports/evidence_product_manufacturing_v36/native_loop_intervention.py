"""Causal Native loop intervention; no solver, force or state implementation.

Hold the actual 685 graph/input fixed, change animation loop only. Default-loop
Cable is an intentional negative control: a correct free ODE is not evidence
that a Lagrange actuator is processed. Never promote this coupon into B3.
"""
import argparse
import csv
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from analyse import BASE, sha
from native_bending_coupon import guarded

SDK = Path('/home/ubuntu/SOFA/v26.06.00')


def reference(ode, dt, count):
    z, v, acceleration = 0., 0., 1000.
    states = []
    for _ in range(count):
        if ode == 'NewmarkImplicitSolver':
            anew = (1. - 1000. * (z + dt*v + dt*dt*acceleration/4)) / (.001 + dt*dt*1000./4)
            z, v = z + dt*v + dt*dt*(acceleration+anew)/4, v + dt*(acceleration+anew)/2
            acceleration = anew
        else:
            v = (.001*v + dt*(1.-1000.*z)) / (.001 + dt*dt*1000.)
            z += dt*v
        states.append((z, v))
    return np.asarray(states)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tag', required=True)
    a = p.parse_args()
    out = BASE/'results'/a.tag
    out.mkdir(exist_ok=False)
    physical = BASE/'cad/build_default_control332/libReGripProductSequence.so'
    probe = BASE/'cad/build_b3_native_plane_force682/libReGripPenaltyProbe.so'
    expected = {physical: '3eb202b1e2a25f3ec6cded69e92a9d02bc48c304be14f6ca7123b4d758e5d0e0',
                probe: '11d942a190d96ef3b80b47a31f279308b4a17a09ae8ca5d9b15e90d23028d1d9'}
    for path, digest in expected.items():
        if sha(path) != digest:
            raise ValueError('frozen observer mismatch: '+str(path))
    h, count = .00025, 80
    records = []
    # ConstraintAnimationLoop is deprecated in installed26.06; diagnostic only.
    configurations = [('DefaultAnimationLoop', ode, channel)
                      for ode in ('EulerImplicitSolver', 'NewmarkImplicitSolver')
                      for channel in ('external_force', 'cable')]
    configurations += [('ConstraintAnimationLoop', 'NewmarkImplicitSolver', 'external_force')]
    for loop, ode, channel in configurations:
        d = out/(loop+'_'+ode+'_'+channel)
        d.mkdir()
        root = ET.parse(BASE/'results/native_force_units330/scene.scn').getroot()
        root.set('dt', str(h))
        root.find('FreeMotionAnimationLoop').tag = loop
        node = root.find("./Node[@name='coupon']")
        solver = node.find('EulerImplicitSolver')
        solver.tag = ode
        solver.attrib.update(rayleighMass='0', rayleighStiffness='0')
        if ode == 'NewmarkImplicitSolver':
            solver.attrib.update(gamma='.5', beta='.25', vdamping='0')
        root.insert(0, ET.Element('RequiredPlugin', pluginName='Sofa.Component.MechanicalLoad'))
        root.insert(0, ET.Element('RequiredPlugin', pluginName=str(probe)))
        for item in root.iter():
            if item.get('filename'):
                item.set('filename', str(d/Path(item.get('filename')).name))
            if item.tag == 'RequiredPlugin' and 'libReGripProductSequence.so' in item.get('pluginName', ''):
                item.set('pluginName', str(physical))
            if item.tag == 'CableConstraint':
                item.set('value', format(h if channel == 'cable' else 0., '.17g'))
        if channel == 'external_force':
            ET.SubElement(node, 'ConstantForceField', indices='0 1', forces='0 0 1 0 0 1')
        ET.SubElement(root, 'NativePenaltyJournal', point='@coupon/dofs', filename=str(d/'probe.csv'))
        ET.ElementTree(root).write(d/'scene.scn')
        proc = guarded([SDK/'bin/runSofa-26.06.00', '--noautoload', '--tmp', '-g', 'batch', '-a', '-n', str(count), '--hideProgressBar', d/'scene.scn'], d/'process', 480)
        logs = ''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log', 'stderr.log'))
        r = dict(loop=loop, ode=ode, channel=channel, process=proc,
                 sofa_errors=logs.count('[ERROR]'), scene_sha256=sha(d/'scene.scn'),
                 status='FAIL_NATIVE_EXECUTION', frames=None)
        if proc['exit_code'] == 0 and not r['sofa_errors']:
            rows = list(csv.DictReader((d/'states.csv').open()))
            if len(rows) != count:
                raise ValueError('incomplete Native states')
            actual = np.asarray([[np.fromstring(s['q'], sep=' ').reshape(-1,3)[0,2],
                                  np.fromstring(s['v'], sep=' ').reshape(-1,3)[0,2]] for s in rows])
            ref = reference(ode, h, count)
            errors = np.max(abs(actual-ref), axis=0)
            r.update(frames=actual.tolist(), maximum_position_reference_error_m=float(errors[0]),
                     maximum_velocity_reference_error_m_s=float(errors[1]),
                     status='PASS_DISCRETE_STATE_SCOPE' if max(errors) <= 1e-12 else 'FAIL_DISCRETE_STATE')
        records.append(r)
    deps = [SDK/'lib/libSofa.Component.AnimationLoop.so', SDK/'lib/libSofa.Component.ODESolver.Backward.so']
    result = dict(status='LOOP_INTERVENTION_DIAGNOSTIC_NOT_B3_QUALIFICATION',
                  scope='Same6851g/1000N/m/1N straight coupon;loop intervention atfixed250us. No contact/FEM/mesh/timeGate/Holding qualification. Default Cable is negative control,not proposed production loop.',
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=BASE.parent,text=True).strip(),
                  producer_sha256=sha(Path(__file__)), binary_hashes={str(k):sha(k) for k in expected},
                  SDK_dependency_hashes={str(k):sha(k) for k in deps}, dt_s=h, steps=count,
                  state_gate=1e-12, mass_per_point_kg=.001, spring_N_m=1000., force_per_point_N=1.,
                  RSS_bytes=None, records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({**result, 'records':[{k:v for k,v in r.items() if k != 'frames'} for r in records]}, indent=2))


if __name__ == '__main__':
    main()
