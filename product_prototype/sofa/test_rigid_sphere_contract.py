import json,unittest,xml.etree.ElementTree as ET
from analyse import BASE
class RigidSphereContract(unittest.TestCase):
 def test_actual_template_distinction_and_no_vec3_torque_shortcut(self):
  d=json.loads((BASE/'results/rigid_sphere_contract1567/summary.json').read_text());r={(x['policy'],x['sphere_representation']):x for x in d['records']}
  self.assertEqual(r['Local','Rigid3']['nonzero_response_rows'],0)
  self.assertGreater(r['Local','Vec3']['nonzero_response_rows'],0)
  self.assertEqual(r['Min','Vec3']['maximum_direct_angular_J_component'],0)
  self.assertGreater(r['Min','Rigid3']['maximum_direct_angular_J_component'],0)
 def test_actual_new_rigid_response_retains_angular_coupling(self):
  r=next(x for x in json.loads((BASE/'results/new_rigid_sphere_contract1568/summary.json').read_text())['records'] if x['sphere_representation']=='Rigid3');self.assertGreater(r['nonzero_response_rows'],0);self.assertGreater(r['maximum_direct_angular_J_component'],0);self.assertGreater(r['maximum_sphere_angular_impulse_Nms'],0)
 def test_geometry_mass_and_input_fixed_across_template_controls(self):
  roots=[ET.parse(BASE/'results/rigid_sphere_contract1567'/x/'scene.scn').getroot() for x in ('MinVec3','MinRigid3','LocalVec3','LocalRigid3')];p="Node[@name='guide1']"
  for r in roots[1:]:
   self.assertEqual(roots[0].find(p+'/MechanicalObject').attrib,r.find(p+'/MechanicalObject').attrib);self.assertEqual(roots[0].find(p+'/UniformMass').attrib,r.find(p+'/UniformMass').attrib);self.assertEqual(roots[0].find(p+"/Node[@name='collision']/SphereCollisionModel").get('radius'),r.find(p+"/Node[@name='collision']/SphereCollisionModel").get('radius'))
if __name__=='__main__':unittest.main()
