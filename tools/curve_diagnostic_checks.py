"""Persist tests for the newly added diagnostic paths; never overwrite raw."""
import sys
from curve_common import ROOT, write_json, sha
from closure_validation_suite import logged


def main():
    out = ROOT / 'results/autonomous_20261116_diagnostics_checks_a08'
    out.mkdir(exist_ok=False)
    sources = [ROOT / 'tests/test_checkpoint_guards.py', ROOT / 'tests/test_curved_guards.py',
               ROOT / 'tests/test_return_energy.cpp', ROOT / 'models/contact_energy/ReturnAudit.h',
               ROOT / 'tests/test_return_time.cpp', ROOT / 'models/integrated/Kernels.h',
               ROOT / 'tests/test_pressure_return_energy.cpp',
               ROOT / 'tests/test_beam_translation_compensation.cpp',
               ROOT / 'models/stabilization/Compensated.h',
               ROOT / 'tests/test_energy_source_scope.py',
               ROOT / 'tests/test_contact_rayleigh.cpp',ROOT/'tests/test_fixed_clock.cpp',
               ROOT / 'models/fixed_step_clock/Clock.h',
               ROOT / 'models/event_step_clock/Schedule.h',ROOT/'tests/test_event_clock.cpp',
               ROOT / 'tests/test_damping_inference.py',ROOT/'tests/test_contact_work_remainder.cpp',
               ROOT / 'tests/test_contact_work_grouping.cpp',ROOT/'tests/test_phase_grid.py',
               ROOT / 'tests/test_phase_assessment_guards.py',ROOT/'tests/test_slip_band.cpp',
               ROOT / 'models/contact_energy/SlipBandReference.h']
    write_json(out / 'sources.json', {str(p.relative_to(ROOT)): sha(p) for p in sources})
    results = {}
    commands = [
        ('checkpoint_guards', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                               '-p', 'test_checkpoint_guards.py', '-v']),
        ('curved_guards', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                           '-p', 'test_curved_guards.py', '-v']),
        ('energy_source_guards', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                                  '-p', 'test_energy_source_scope.py', '-v']),
        ('return_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                          'tests/test_return_energy.cpp', '-o', out / 'return_unit.bin']),
        ('return_unit', [out / 'return_unit.bin']),
        ('return_time_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                               'tests/test_return_time.cpp', '-o', out / 'return_time.bin']),
        ('return_time_unit', [out / 'return_time.bin']),
        ('pressure_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                            'tests/test_pressure_return_energy.cpp', '-o', out / 'pressure.bin']),
        ('pressure_unit', [out / 'pressure.bin']),
        ('compensation_build', ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-pedantic',
                                'tests/test_beam_translation_compensation.cpp', '-o', out / 'compensation.bin']),
        ('compensation_unit', [out / 'compensation.bin']),
        ('rayleigh_build', ['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                           'tests/test_contact_rayleigh.cpp','-o',out/'rayleigh.bin']),
        ('rayleigh_counterexamples',[out/'rayleigh.bin']),
        ('clock_build', ['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                        'tests/test_fixed_clock.cpp','-o',out/'clock.bin']),
        ('clock_unit',[out/'clock.bin']),
        ('event_clock_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                              'tests/test_event_clock.cpp','-o',out/'event_clock.bin']),
        ('event_clock_unit',[out/'event_clock.bin']),
        ('mapped_work_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                              'tests/test_contact_work_remainder.cpp','-o',out/'mapped_work.bin']),
        ('mapped_work_unit',[out/'mapped_work.bin']),
        ('damping_inference',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_damping_inference.py','-v']),
        ('work_group_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                             'tests/test_contact_work_grouping.cpp','-o',out/'work_group.bin']),
        ('work_group_unit',[out/'work_group.bin']),
        ('phase_grid_scope',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_phase_grid.py','-v']),
        ('phase_assessment_guards',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_phase_assessment_guards.py','-v']),
        ('slip_band_build',['g++','-std=c++17','-O2','-Wall','-Wextra','-pedantic',
                           'tests/test_slip_band.cpp','-o',out/'slip_band.bin']),
        ('slip_band_reference',[out/'slip_band.bin']),
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
