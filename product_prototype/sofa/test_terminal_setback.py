"""Generated candidate contract checks, not performance or hardware tests."""
import unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE

class Setback(unittest.TestCase):
 def setUp(self):
  self.old=ET.parse(BASE/'results/dispatch_finite_holding1586/scene.scn').getroot()
  self.new=ET.parse(BASE/'results/terminal_setback1683/candidate_scene_NOT_RUN.scn').getroot()
 def test_unchanged_parent_mass_and_fem(self):
  for i in range(3):
   a=self.old.find(f"Node[@name='guides{i}']");b=self.new.find(f"Node[@name='guides{i}']")
   for tag in ('MechanicalObject','UniformMass'):self.assertEqual(a.find(tag).attrib,b.find(tag).attrib)
   a=self.old.find(f"Node[@name='finger{i}']");b=self.new.find(f"Node[@name='finger{i}']")
   self.assertEqual(a.find('MechanicalObject').attrib,b.find('MechanicalObject').attrib)
 def test_whole_ring_translation_and_cable(self):
  for i in range(3):
   for j in range(2):
    path=f"Node[@name='guides{i}']/Node[@name='cable{j}']";a=self.old.find(path);b=self.new.find(path)
    ar=a.find("Node[@name='eyelet5']");br=b.find("Node[@name='eyelet5']")
    va=np.fromstring(ar.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);vb=np.fromstring(br.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);delta=vb-va
    np.testing.assert_allclose(delta,np.repeat(delta[:1],len(delta),axis=0),atol=1e-17,rtol=0)
    self.assertAlmostEqual(float(np.linalg.norm(delta[0])),.002,places=14)
    self.assertEqual(ar.find('MeshTopology').get('triangles'),br.find('MeshTopology').get('triangles'))
    cable=np.fromstring(b.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
    np.testing.assert_allclose(cable[5],vb.mean(0),atol=1e-15,rtol=0)
 def test_all_hardware_collision_features_retained(self):
  old=[x for x in self.old.iter() if x.tag.endswith('CollisionModel')];new=[x for x in self.new.iter() if x.tag.endswith('CollisionModel')]
  self.assertEqual([(x.tag,x.attrib) for x in old],[(x.tag,x.attrib) for x in new])

if __name__=='__main__':unittest.main()
