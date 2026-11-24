"""Frozen route intervention contract; not a grasp or numerical PASS."""
import json,unittest,xml.etree.ElementTree as ET
from analyse import BASE
class RouteContract(unittest.TestCase):
 def test_only_configuration_margin_changes(self):
  old=json.loads((BASE/'results/paired_mesh_hold1001534/config.json').read_text());new=json.loads((BASE/'results/unbraced_fixed1543/config.json').read_text());old['tendon']['sector_margin_mm']=new['tendon']['sector_margin_mm'];self.assertEqual(old,new)
 def test_all_collisions_and_parent_frames_retained(self):
  a=ET.parse(BASE/'results/paired_mesh_hold1001534/scene.scn').getroot();b=ET.parse(BASE/'results/unbraced_fixed1543/scene.scn').getroot()
  # Single pilot intentionally removes two fingers and fixes the sphere.
  for path in ("Node[@name='finger0']/MechanicalObject","Node[@name='guides0']/MechanicalObject","Node[@name='free0']/MechanicalObject"):
   self.assertEqual(a.find(path).attrib,b.find(path).attrib)
  for j in (0,1):
   path=f"Node[@name='guides0']/Node[@name='cable{j}']"
   for component in ('SphereCollisionModel','RigidMapping'):
    self.assertEqual(a.find(path+'/'+component).attrib,b.find(path+'/'+component).attrib)
   self.assertNotEqual(a.find(path+'/MechanicalObject').get('position'),b.find(path+'/MechanicalObject').get('position'))
 def test_replay_not_dynamic_qualification(self):
  x=json.loads((BASE/'results/unbraced_route1542/summary.json').read_text());self.assertEqual(x['status'],'READY_STATIC_ROUTE_INTERVENTION_ONLY');self.assertGreaterEqual(x['candidate_replay']['minimum_replayed_interfinger_guide_gap_mm'],1.)
if __name__=='__main__':unittest.main()
