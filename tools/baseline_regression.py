"""Run an unmodified-mechanics XML V109 adapter and compare all 600 golden rows."""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from native_scene import generate
from verification_common import BUILD, provenance, sha,assert_build_current
from trial_validation import read_states

ROOT = Path(__file__).resolve().parents[1]
SOFA = Path(os.environ.get('SOFA_ROOT', '/home/ubuntu/SOFA/v26.06.00'))


def states(path):
    return read_states(path)


def metrics(rigid, points):
    initial = rigid[0]['X']
    result = []
    if len(rigid) != len(points):
        raise ValueError('state counts differ')
    for body, iface in zip(rigid[1:], points[1:]):
        x, v, p = body['X'], body['V'], iface['X']
        if len(x) != 154 or len(v) != 132 or len(p) != 66:
            raise ValueError('unexpected DOF counts')
        if abs(body['time'] - iface['time']) > 1e-12:
            raise ValueError('state times differ')
        if not all(math.isfinite(a) for a in x+v+p):
            raise ValueError('nonfinite state')
        tip = -0.5*((x[10*7+2]-initial[10*7+2])+(x[21*7+2]-initial[21*7+2]))
        row = dict(time_s=body['time'], tip_deflection_mm=tip,
                   tip_velocity_z_mm_s=0.5*(v[10*6+2]+v[21*6+2]))
        initial_points=points[0]['X']
        row['max_mapped_movement_mm']=max(math.sqrt(sum((p[3*i+j]-initial_points[3*i+j])**2 for j in range(3))) for i in range(22))
        row['max_rigid_movement_mm']=max(math.sqrt(sum((x[7*i+j]-initial[7*i+j])**2 for j in range(3))) for i in range(22))
        row['mean_abs_rotation_quat_xyz']=sum(math.sqrt(sum(x[7*i+j]**2 for j in (3,4,5))) for i in range(22))/22
        for axis, name in enumerate(('max_x_slip_mm', 'max_y_rel_mm', 'max_z_rel_mm')):
            row[name] = max(abs(p[(11+i)*3+axis]-p[i*3+axis]) for i in range(1, 11))
        result.append(row)
    return result


def run(out):
    assert_build_current()
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError('use a new run directory to avoid stale artifacts: ' + str(out))
    generate(out/'scene.scn')
    diag = BUILD/'diagnostics/libReGripDiagnostics.so'
    command = [str(SOFA/'bin/runSofa-26.06.00'), '--noautoload', '--tmp',
               '-l', str(diag), '-g', 'batch', '-a', '-n', '600', '--hideProgressBar', str(out/'scene.scn')]
    (out/'command.json').write_text(json.dumps(command, indent=2))
    start = time.monotonic()
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=30)
    (out/'sofa.log').write_text(run.stdout)
    if run.returncode != 0 or '[ERROR]' in run.stdout or '600 iterations done' not in run.stdout:
        raise RuntimeError('SOFA failed; inspect ' + str(out/'sofa.log'))
    actual = metrics(states(out/'rigid.txt'), states(out/'interface.txt'))
    with (ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv').open(encoding='utf-8-sig') as stream:
        golden = list(csv.DictReader(stream))
    if len(actual) != 600 or len(golden) != 600:
        raise ValueError('expected 600 golden and actual samples')
    fields = list(actual[0])
    with (out/'baseline_free.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(actual)
    errors = {}
    # Strict regression tolerance; accommodates cross-platform floating point noise.
    # This is not the timestep convergence or static-equilibrium tolerance.
    rtol, atol = 1e-6, 1e-10
    passed = True
    for key in fields:
        pairs = [(a[key], float(g[key])) for a, g in zip(actual, golden)]
        error = max(abs(a-g) for a, g in pairs)
        ok = all(abs(a-g) <= atol+rtol*abs(g) for a, g in pairs)
        errors[key] = dict(max_abs_error=error, final_actual=pairs[-1][0],
                           final_golden=pairs[-1][1], passed=ok)
        passed &= ok
    report = dict(passed=passed, adapter='XML of V109 combined FREE, native full-precision recorder',
                  original_python_scene_executed=False, samples=600, dt=0.0005,
                  rtol=rtol, atol=atol, errors=errors, runtime_s=time.monotonic()-start,
                  diagnostics_sha256=hashlib.sha256(diag.read_bytes()).hexdigest(),
                  equilibrium_validated=False)
    report['provenance']=provenance()
    report['artifact_sha256']={name:sha(out/name) for name in ('scene.scn','rigid.txt','interface.txt','sofa.log','baseline_free.csv','command.json')}
    (out/'comparison.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return passed


if __name__ == '__main__':
    sys.exit(0 if run(sys.argv[1]) else 1)
