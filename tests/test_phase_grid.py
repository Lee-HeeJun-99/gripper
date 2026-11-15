import sys
import inspect
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import history_trial
from curve_phase_grid import count,EVENTS,DIVISORS


class GridScope(unittest.TestCase):
    def test_all_steps_refine_by_two(self):
        self.assertEqual(count(4,.0005),13000)
        self.assertEqual(count(24,.0005),74000)
        self.assertEqual(count(4,.00025),26000)
        self.assertEqual(count(24,.00025),148000)
        self.assertEqual(EVENTS,[0,.5,2,3,4,6,7,14,16,16.5])
        self.assertEqual(DIVISORS,[1,2,1,2,1,2,1,2,16,1])

    def test_assessment_changes_count_not_any_physical_limit(self):
        source=inspect.getsource(history_trial.analyze);needle="steps=round(duration/config['dt'])"
        self.assertEqual(source.count(needle),1)
        generated=source.replace(needle,"steps=config['actual_steps']")
        self.assertEqual(generated.replace("steps=config['actual_steps']",needle),source)
        for threshold in('fr<1e-3','mr<1e-3','globalforce<1e-3','globalmoment<1e-3','disp<.05','ang<.01','rest<1e-4'):
            self.assertIn(threshold,generated)


if __name__=='__main__':unittest.main()
