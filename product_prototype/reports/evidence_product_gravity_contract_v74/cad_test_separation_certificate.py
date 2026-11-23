"""One-sided certificate regressions;never promote unresolved to collision."""
import unittest
import numpy as np
from fractions import Fraction
from swept_separation_certificate import certificate,rational_gap
from separation_certificate_audit import verify

class SeparationTests(unittest.TestCase):
 def setUp(self):self.tri=np.array([[0.,0,0],[1,0,0],[0,1,0]])
 def test_coplanar_translation_clear(self):
  target=self.tri+[0,3,0];c=certificate(self.tri,[4,0,0],target)
  self.assertIsNotNone(c);self.assertGreater(Fraction(*map(int,c['exact_projection_gap'])),0)
 def test_middle_only_contact_is_unresolved_not_clear(self):
  self.assertIsNone(certificate(self.tri,[4,0,0],self.tri+[2,0,0]))
 def test_tangent_not_strict_separation(self):
  self.assertIsNone(certificate(self.tri,[0,0,0],self.tri+[1,0,0]))
 def test_sub_ulp_translation_is_not_rounded_to_zero(self):
  base=np.array([[1e16,0,0],[1e16,1,0],[1e16,0,1]])
  self.assertEqual(rational_gap(base,[1.,0,0],base+[2,0,0],[1,0,0]),1)
 def test_exact_axis_gap_matches_reference(self):
  self.assertEqual(rational_gap(self.tri,[4,0,0],self.tri+[0,3,0],[0,1,0]),2)
 def test_rigid_rotation_keeps_clear_case(self):
  Q=np.array([[0,-1,0],[1,0,0],[0,0,1]])
  self.assertIsNotNone(certificate(self.tri@Q.T,Q@np.array([4.,0,0]),(self.tri+[0,3,0])@Q.T))
 def test_invalid_input_rejected(self):
  with self.assertRaises(ValueError):certificate(self.tri,[np.nan,0,0],self.tri)
 def test_replay_rejects_missing_duplicate_and_corrupt_proofs(self):
  target=self.tri+[0,3,0];proof=dict(source_triangle=0,part='target',target_triangle=0,**certificate(self.tri,[4,0,0],target));expected={(0,'target',0)}
  def check(proofs):return verify(proofs,[self.tri],[4,0,0],{'target':[target]},expected)
  self.assertEqual(check([proof])['verified_pairs'],1)
  for bad in ([],[proof,proof],[dict(proof,exact_projection_gap=['0','1'])]):
   with self.assertRaises(ValueError):check(bad)
if __name__=='__main__':unittest.main()
