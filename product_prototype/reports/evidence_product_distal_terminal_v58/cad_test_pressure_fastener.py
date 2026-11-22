"""Catalog/conditional geometry regressions,not physical joint acceptance."""
import copy,json,unittest
from manufacturing_assembly import BASE,evaluate
from pressure_fastener_contract import interval_gap,contract
from pressure_captive_nut import adjuster
from pressure_service_interval import travel_window

class PressureFastenerTests(unittest.TestCase):
 def setUp(self):self.cfg=json.loads((BASE/'config/pressure_shoe_fastener_v47.json').read_text())
 def test_interval_extremes_not_nominal_only(self):
  self.assertEqual(interval_gap([3,4],[2,2.5]),[.5,2])
  for bad in ([4,3],[float('nan'),4]):
   with self.assertRaises(ValueError):interval_gap(bad,[2,3])
 def test_catalog_clearance_is_conditional_not_preload(self):
  d=contract(self.cfg);self.assertAlmostEqual(d['nut_AF_total_clearance_interval_mm'][0],.07);self.assertAlmostEqual(d['conditional_tip_to_pad_width_edge_margin_mm'],.04)
  self.assertAlmostEqual(d['nominal_free_stack_angle_deg'],72);self.assertIsNone(d['actual_preload_N']);self.assertFalse(d['actual_thread_fit_qualified'])
 def test_incompatible_pitch_is_rejected(self):
  cfg=copy.deepcopy(self.cfg);cfg['nut_candidate']['pitch_mm']=.4
  with self.assertRaises(ValueError):contract(cfg)
 def test_oversize_axis_error_is_not_hidden(self):
  cfg=copy.deepcopy(self.cfg);cfg['design_targets_NOT_PROCESS_CAPABILITY']['axis_position_plus_minus_mm']=.2
  self.assertLess(contract(cfg)['conditional_tip_to_pad_width_edge_margin_mm'],0)
 def test_adjuster_actual_envelope_closed_at_length_extremes(self):
  for length in (2.8,3,3.2):
   body=evaluate(adjuster(length));self.assertTrue(body.is_volume);self.assertAlmostEqual(body.bounds[0,2],.42,places=6);self.assertAlmostEqual(body.bounds[1,2],.42+length,places=6)
 def test_adjuster_outside_catalog_interval_rejected(self):
  with self.assertRaises(ValueError):adjuster(2.7)
  with self.assertRaises(ValueError):adjuster(3,.9)
 def test_service_window_bounds_and_json_scalar(self):
  d=travel_window([10.15248,13.84752],5,9.4);self.assertAlmostEqual(d['midpoint_travel_mm'],4.8);self.assertTrue(d['nominal_window_exists']);json.dumps(d)
  self.assertFalse(travel_window([9,11],8,9.4)['nominal_window_exists'])
if __name__=='__main__':unittest.main()
