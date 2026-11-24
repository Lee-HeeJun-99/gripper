import json,unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
from new_projection_audit import acute_faces,projection
class ProjectionContract(unittest.TestCase):
 def test_actual_new_separated_failure_is_not_promoted(self):
  d=json.loads((BASE/'results/separated_rigid_sphere1570/summary.json').read_text());r={x['policy']:x for x in d['records']};self.assertGreater(d['actual_minimum_triangle_sphere_gap_mm'],.2);self.assertEqual(r['Min']['nonzero_actual_response_rows'],0);self.assertGreater(r['New']['nonzero_actual_response_rows'],0)
 def test_saved_point_outside_surface_and_branch_match(self):
  d=json.loads((BASE/'results/new_projection_audit1571/summary.json').read_text());r=max(d['actual_contacts'],key=lambda x:x['minimum_point_distance_to_actual_surface_mm']);self.assertGreater(r['minimum_point_distance_to_actual_surface_mm'],30);self.assertLessEqual(r['minimum_reconstruction_error_m'],1e-12);self.assertTrue(any(min(x)<-1 for x in r['candidate_barycentrics']))
 def test_native_cyclic_separated_and_loaded_both_required(self):
  d=json.loads((BASE/'results/cyclic_projection_contract1572/summary.json').read_text());self.assertEqual(d['status'],'PASS_SEPARATED_AND_LOADED_NATIVE_CYCLIC_COUPONS_ONLY');r={x['case']:x for x in d['records']};self.assertEqual(r['separated']['actual_nonzero_response_rows'],0);self.assertEqual(r['separated']['maximum_actual_velocity_component'],0);self.assertGreater(r['loaded']['actual_nonzero_response_rows'],0);self.assertGreater(r['loaded']['maximum_direct_angular_J_component'],0)
 def test_cyclic_is_orientation_preserving_same_facets(self):
  root=ET.parse(BASE/'results/separated_rigid_sphere1570/New/scene.scn').getroot();node=root.find("Node[@name='guide0']/Node[@name='collision']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);f=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);new=acute_faces(v,f);self.assertTrue(np.array_equal(np.sort(f,axis=1),np.sort(new,axis=1)))
  for a,b in zip(f,new):self.assertTrue(any(np.array_equal(np.roll(a,k),b) for k in range(3)))
if __name__=='__main__':unittest.main()
