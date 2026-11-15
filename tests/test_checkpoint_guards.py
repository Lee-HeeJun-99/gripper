import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from curve_checkpoint_common import physics_hash, validate_scope, merge_states


def scene():
    return ET.ElementTree(ET.fromstring('''<Node dt=".0005">
      <EulerImplicitSolver/><Node name="Multilayer"><MechanicalObject/>
      <DiagonalMass vertexMass="1 2 3"/><CurvedMaterialContact filename="a.csv"/>
      <FrameLayerNetwork filename="l.csv"/><IntegratedRecorder filename="s.txt"/>
      </Node></Node>'''))


class CheckpointGuards(unittest.TestCase):
    def test_output_rename_is_not_a_physics_change(self):
        a, b = scene(), scene()
        b.getroot().find('.//CurvedMaterialContact').set('filename', 'different.csv')
        self.assertEqual(physics_hash(a), physics_hash(b))

    def test_mass_and_dt_are_physics(self):
        a, b = scene(), scene()
        b.getroot().find('.//DiagonalMass').set('vertexMass', '2 2 3')
        self.assertNotEqual(physics_hash(a), physics_hash(b))
        b = scene(); b.getroot().set('dt', '.00025')
        self.assertNotEqual(physics_hash(a), physics_hash(b))

    def test_unknown_history_owner_refused(self):
        a = scene(); ET.SubElement(a.getroot(), 'UnknownController')
        with self.assertRaises(ValueError):
            validate_scope(a)

    def test_unsupported_integrator_state_refused(self):
        a = scene(); a.getroot().find('EulerImplicitSolver').set('trapezoidalScheme', 'true')
        with self.assertRaises(ValueError):
            validate_scope(a)

    def test_physical_filename_not_silently_stripped(self):
        a = scene(); a.getroot().find('.//MechanicalObject').set('filename', 'rest.mesh')
        with self.assertRaises(ValueError):
            physics_hash(a)

    def test_only_restored_startup_frame_removed(self):
        with tempfile.TemporaryDirectory(prefix='regrip_cp_guard_') as temporary:
            root = Path(temporary); paths = [root / 'a', root / 'b']
            for i, p in enumerate(paths):
                p.mkdir()
                (p / 'state.txt').write_text('T= 0\nX= startup\nT= ' + str(i+1) + '\nX= advanced\n')
            merge_states(paths, root / 'merged')
            self.assertEqual((root / 'merged').read_text().count('X= startup'), 1)
            self.assertEqual((root / 'merged').read_text().count('X= advanced'), 2)
            with self.assertRaises(FileExistsError):
                merge_states(paths, root / 'merged')


if __name__ == '__main__':
    unittest.main()
