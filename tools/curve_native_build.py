"""Strict-FP ISA optimization contrast; no fast-math/reassociation."""
import curve_build
from closure_validation_suite import logged
def native_logged(command,directory,timeout=120):
    command=list(command)
    if str(command[0])=='cmake'and'-S'in command:command.append('-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -march=native -ffp-contract=off')
    return logged(command,directory,timeout)
if __name__=='__main__':
    curve_build.logged=native_logged;curve_build.main()
