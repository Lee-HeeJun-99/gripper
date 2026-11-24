import unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
from partitioned_eyelet_wire import partition
from wire_units_contract import transform
class ContactRepresentation(unittest.TestCase):
 def tree(self):return ET.parse(BASE/'results/wire_contact_policy1616/scene.scn').getroot()
 def test_partition_does_not_erase_surface_or_other_features(self):
  r=self.tree();old=r.find("Node[@name='finiteEyelet']");v=np.fromstring(old.find('MeshTopology').get('position'),sep=' ');f=old.find('MeshTopology').get('triangles');line=dict(old.find('LineCollisionModel').attrib);point=dict(old.find('PointCollisionModel').attrib);partition(r);new=r.find("Node[@name='finiteEyelet']");self.assertEqual(new.find('MeshTopology').get('triangles'),f);self.assertEqual(new.find('LineCollisionModel').attrib,line);self.assertEqual(new.find('PointCollisionModel').attrib,point);actual=[]
  for c in new.findall('Node'):
   np.testing.assert_array_equal(np.fromstring(c.find('MechanicalObject').get('position'),sep=' '),v);actual.extend(np.fromstring(c.find('MeshTopology').get('triangles'),sep=' ',dtype=int));self.assertEqual(len(c.findall('TriangleCollisionModel')),1);self.assertIsNone(c.find('LineCollisionModel'));self.assertIsNone(c.find('PointCollisionModel'))
  np.testing.assert_array_equal(actual,np.fromstring(f,sep=' ',dtype=int))
 def test_units_preserve_physical_mass_and_bending_rigidity(self):
  r=self.tree();E=float(r.find('.//BeamInterpolation').get('defaultYoungModulus'));radius=float(r.find('.//BeamInterpolation').get('radius'));rho=float(r.find('.//AdaptiveBeamForceFieldAndMass').get('massDensity'));points=np.fromstring(r.find('.//AdaptiveBeamMapping').get('points'),sep=' ').reshape(-1,3);transform(r);b=r.find('.//BeamInterpolation');newE=float(b.get('defaultYoungModulus'));newR=float(b.get('radius'));newrho=float(r.find('.//AdaptiveBeamForceFieldAndMass').get('massDensity'));self.assertAlmostEqual(newrho*newR**2*20,rho*radius**2*.02,places=20);self.assertAlmostEqual(newE*newR**4/1000**3,E*radius**4,places=20);p=np.fromstring(r.find('.//AdaptiveBeamMapping').get('points'),sep=' ').reshape(-1,3);np.testing.assert_array_equal(points[:,0],p[:,0]);np.testing.assert_allclose(p[:,1:]/1000,points[:,1:],atol=1e-19,rtol=0)
if __name__=='__main__':unittest.main()
