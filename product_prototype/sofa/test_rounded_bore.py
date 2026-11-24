import unittest,numpy as np
from rounded_bore_wire import geometry,inside
class RoundedBore(unittest.TestCase):
 def test_closed_mesh_volume(self):
  m,p=geometry();n=32;factor=n*np.sin(2*np.pi/n)/2;inner=sum((b[0]-a[0])*(a[1]**2+a[1]*b[1]+b[1]**2)/3 for a,b in zip(p[:-1],p[1:]));expected=factor*(2*1.5**2-inner);self.assertTrue(m.is_watertight);self.assertTrue(m.is_winding_consistent);self.assertAlmostEqual(m.volume,expected,places=12)
 def test_membership_against_independent_rays(self):
  m,p=geometry();q=np.random.default_rng(1633).uniform([-1.2,-1.7,-1.7],[1.2,1.7,1.7],(1000,3));np.testing.assert_array_equal(inside(q,p),m.contains(q))
 def test_real_bore_not_removed(self):
  m,p=geometry();q=np.array([[0,.7,0],[0,.5,0],[-.99,.7,0],[1.1,1,0],[0,1.6,0]]);np.testing.assert_array_equal(inside(q,p),[True,False,False,False,False]);self.assertEqual(len(m.faces),768)
if __name__=='__main__':unittest.main()
