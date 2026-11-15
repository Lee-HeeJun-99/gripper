import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from curve_phase_assess import relative,physical_xml


class PhaseEvidenceGuards(unittest.TestCase):
    def test_no_small_denominator_relaxation(self):
        self.assertEqual(relative(0,0,.001)['status'],'PASS')
        self.assertEqual(relative(1e-30,0,.001)['status'],'FAIL')
        r=relative(1.01e-30,1e-30,.001)
        self.assertEqual(r['status'],'FAIL')
        self.assertAlmostEqual(r['relative'],.01)

    def test_time_and_output_paths_not_material_parameters(self):
        with tempfile.TemporaryDirectory()as d:
            paths=[Path(d)/n for n in('a','b','c')]
            for p in paths:p.mkdir()
            template='<Node dt="{}"><RequiredPlugin name="runtime"/><EventStepClockAnimationLoop/><Node><MechanicalObject position="0 0 0 0 0 0 1"/><CurvedMaterialContact mu="{}" filename="{}"/><FixedProjectiveConstraint indices="0"/></Node></Node>'
            (paths[0]/'scene.scn').write_text(template.format('.0005','.3','first'))
            (paths[1]/'scene.scn').write_text(template.format('.00025','.3','second'))
            (paths[2]/'scene.scn').write_text(template.format('.00025','.4','second'))
            self.assertEqual(physical_xml(paths[0]),physical_xml(paths[1]))
            self.assertNotEqual(physical_xml(paths[0]),physical_xml(paths[2]))


if __name__=='__main__':unittest.main()
