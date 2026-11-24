"""Geometry/input and failure-preservation tests,not numerical certification."""
import json,unittest,xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE
def data(case,name='summary.json'):
 return json.loads((BASE/'results'/case/name).read_text())
class ConformalTests(unittest.TestCase):
 def test_actual_manufactured_circle(self):
  case='conformal_dorsal1473';geo=data(case,'geometry.json');c=data(case,'config.json');m=data(case,'mesh.json');root=ET.parse(BASE/'results'/case/'scene.scn').getroot();q=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;local=np.array(m['local_positions_mm']);stations=[q[(local[:,0]==x)&(local[:,2]==.1)].mean(0) for x in np.unique(local[:,0]) if x>=70]
  self.assertGreater(len(stations),1);r=np.linalg.norm(np.array(stations)-c['simulation']['sphere_center_mm'],axis=1);self.assertLess(abs(r-30.5).max(),1e-10);self.assertTrue(geo['dorsal_terminal']);self.assertGreater(geo['minimum_interfinger_guide_sphere_gap_mm'],.2)
 def test_hardware_not_disabled_or_shrunk(self):
  before=ET.parse(BASE/'results/b3_railback_grasp1001298/scene.scn').getroot();after=ET.parse(BASE/'results/conformal_hybrid_fixed1477/scene.scn').getroot()
  for j in range(2):
   path=f"Node[@name='guides0']/Node[@name='cable{j}']/SphereCollisionModel";a,b=before.find(path),after.find(path);self.assertEqual(a.attrib,b.attrib)
  self.assertEqual(after.find("Node[@name='guides0']/MechanicalObject").get('template'),before.find("Node[@name='guides0']/MechanicalObject").get('template'))
 def test_hybrid_not_another_force_increment(self):
  p=data('conformal_hybrid_fixed1477','preflight.json');self.assertEqual(p['force_N_per_cable'],data('grasp_load_budget1465')['proposed_force_N_per_cable']);self.assertTrue(p['load_sized_hybrid']);self.assertEqual(data('conformal_hybrid_fixed1477')['outputs'],[100]);self.assertIsNone(data('conformal_hybrid_fixed1477')['first_inversion'])
 def test_old_load_sizing_failure_not_promoted(self):
  d=data('load_budget_assess1469');self.assertEqual(d['status'],'FAIL_EXPLORATORY_FUNCTIONAL_GRASP');self.assertGreater(d['slip_mm'],200);self.assertGreater(d['force_partition']['guide']['maximum_resultant_N'],.1)
if __name__=='__main__':unittest.main()
