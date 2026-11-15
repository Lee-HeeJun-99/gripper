"""Persist tests for the newly added diagnostic paths; never overwrite raw."""
import sys
from curve_common import ROOT, write_json, sha
from closure_validation_suite import logged


def main():
    out = ROOT / 'results/autonomous_20261116_diagnostics_checks_a03'
    out.mkdir(exist_ok=False)
    sources = [ROOT / 'tests/test_checkpoint_guards.py', ROOT / 'tests/test_curved_guards.py',
               ROOT / 'tests/test_return_energy.cpp', ROOT / 'models/contact_energy/ReturnAudit.h',
               ROOT / 'tests/test_return_time.cpp', ROOT / 'models/integrated/Kernels.h']
    write_json(out / 'sources.json', {str(p.relative_to(ROOT)): sha(p) for p in sources})
    results = {}
    commands = [
        ('checkpoint_guards', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                               '-p', 'test_checkpoint_guards.py', '-v']),
        ('curved_guards', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                           '-p', 'test_curved_guards.py', '-v']),
        ('return_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                          'tests/test_return_energy.cpp', '-o', out / 'return_unit.bin']),
        ('return_unit', [out / 'return_unit.bin']),
        ('return_time_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                               'tests/test_return_time.cpp', '-o', out / 'return_time.bin']),
        ('return_time_unit', [out / 'return_time.bin']),
        ('python_compile', [sys.executable, '-m', 'py_compile'] +
         sorted((ROOT / 'tools').glob('curve_*.py')))]
    for name, command in commands:
        results[name] = logged(command, out / name, 180)
    write_json(out / 'summary.json', dict(
        status='PASS' if all(not r['exit_code'] for r in results.values()) else 'FAIL',
        checks=results, scope='diagnostic guards,2000return states and syntax;not full physics gates'))
    print({n: r['exit_code'] for n, r in results.items()})


if __name__ == '__main__':
    main()
