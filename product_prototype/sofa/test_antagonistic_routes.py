import json,unittest
from analyse import BASE
def result(case):return json.loads((BASE/'results'/case/'summary.json').read_text())
class FourRouteTests(unittest.TestCase):
 def test_support_obstruction_is_actual_witness(self):
  d=result('four_route_support1409')['previous_collision_witness'];self.assertLess(d['sampled_axis_distance_mm'],.5);self.assertLess(d['actual_sample_capsule_gap_mm'],0)
 def test_rear_support_scope_only(self):
  d=result('four_route_support1409');self.assertEqual(d['status'],'PASS_REAR_SUPPORT_WIRE_SKIN_PROXY_ONLY');self.assertGreater(d['rear_support_wire_witness']['lower_bound_mm'],0);self.assertGreater(d['rear_support_skin_lower_bound_mm'],0);self.assertGreater(d['nominal_added_cylinder_volume_mm3'],0)
 def test_bore_failure_not_relaxed(self):
  d=result('four_route_gate1408');self.assertEqual(d['status'],'REJECT_INITIAL_FOUR_ROUTE_GATE');self.assertLess(d['minimum_straight_bore_wire_margin_mm'],0);self.assertEqual(d['Native_four_cable'],'NOT RUN')
 def test_no_whole_assembly_pass_from_one_fix(self):
  d=result('four_route_support1409');self.assertEqual(d['four_route_overall'],'REJECTED_UNRESOLVED_STRAIGHT_BORE_AND_BEND_RADIUS');self.assertEqual(d['Native_four_cable'],'NOT RUN');self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
if __name__=='__main__':unittest.main()
