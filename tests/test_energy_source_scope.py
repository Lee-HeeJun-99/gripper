import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from curve_compensation_energy import compiled_only


class EnergySourceScope(unittest.TestCase):
    def test_documentation_snapshot_is_not_compiler_input(self):
        a={'Driver.cpp':'same','CMakeLists.txt':'same','README.md':'old'}
        b=dict(a,**{'README.md':'new'})
        self.assertEqual(compiled_only(a),compiled_only(b))

    def test_all_compiled_dependencies_remain_strict(self):
        for path in('Driver.cpp','Audit.h','FrameLayerBase.inc','CMakeLists.txt'):
            a={path:'old','README.md':'old'};b={path:'new','README.md':'old'}
            self.assertNotEqual(compiled_only(a),compiled_only(b))


if __name__=='__main__':unittest.main()
