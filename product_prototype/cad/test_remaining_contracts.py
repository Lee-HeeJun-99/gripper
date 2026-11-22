import unittest
import json
import numpy as np
from manufacturing_assembly import BASE,sha
from remaining_palm_certificate import exclusion,positive_operands
from drum_interface_contract import winding,inspect

class RemainingContractTests(unittest.TestCase):
 def test_placed_f2_scope_and_wire_provenance(self):
  d=json.loads((BASE/'results/product_remaining_lead964/summary.json').read_text())
  self.assertEqual(d['target_finger'],2);self.assertEqual(len(d['records']),9);self.assertFalse(d['solid_intersections'])
  self.assertEqual(d['full_part_count'],279);self.assertFalse(d['fabrication_ready'])
  wire=json.loads((BASE/'results/product_remaining_fullwire965/summary.json').read_text())
  self.assertEqual(wire['probe_count'],705);self.assertTrue(wire['full_lead'])
  self.assertFalse(any(r['classification']=='UNRESOLVED_OBSTACLE' for r in wire['intersections']))
  self.assertEqual(wire['input_hashes']['results/product_remaining_lead964/full_assembly_recipe.json'],sha(BASE/'results/product_remaining_lead964/full_assembly_recipe.json'))
 def test_boundary_is_not_positive_penetration(self):
  self.assertTrue(exclusion([[0,0,13],[1,1,18]])['excludes_open_palm'])
  self.assertTrue(exclusion([[0,0,-2],[1,1,5]])['excludes_open_palm'])
  self.assertFalse(exclusion([[0,0,12],[1,1,18]])['excludes_open_palm'])
  self.assertFalse(exclusion([[64,0,6],[65,1,7]])['excludes_open_palm'])
 def test_invalid_bounds(self):
  with self.assertRaises(ValueError):exclusion([[0,0,float('nan')],[1,1,2]])
 def test_subtraction_cannot_enlarge_positive(self):
  box={'op':'box','lo':[0,0,0],'hi':[1,1,1]}
  self.assertEqual(list(positive_operands({'op':'difference','items':[box,{'op':'unknown'}]})),[box])
 def test_actual_radius_changes_with_wire(self):
  a=winding(7.75,.45,3,1.5);b=winding(7.75,.5,3,1.5)
  self.assertAlmostEqual(a['effective_radius_mm'],7.975);self.assertEqual(b['effective_radius_mm'],8)
  self.assertAlmostEqual(a['ideal_torque_Nm'],.023925)
  self.assertAlmostEqual(a['ideal_torque_Nm']*a['angle_rad'],a['ideal_work_J'])
 def test_reject_invalid_winding(self):
  for v in (0,-1,np.inf,np.nan):
   with self.assertRaises(ValueError):winding(7.75,.45,v,1.5)
  with self.assertRaises(ValueError):inspect({'op':'union'})
