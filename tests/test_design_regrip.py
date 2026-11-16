import json,math,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from design_regrip import baseline,compliance
class DesignGeometry(unittest.TestCase):
 def test_extracted_baseline(self):
  b=baseline();self.assertAlmostEqual(b['root_radius_mm'],95.14800589082253)
  for line in b['centerlines']:
   length=sum(math.dist(line[i],line[i+1])for i in range(10));self.assertAlmostEqual(length,100)
  self.assertIsNone(b['contact_surface_area_mm2'])
 def test_obj_matches_actual_xml(self):
  for name in ('film_contact','selective_jamming'):
   folder=ROOT/'designs'/name/'concept_v2';v=[];f=[]
   for line in(folder/'rest.obj').read_text().splitlines():
    s=line.split()
    if s and s[0]=='v':v.extend(map(float,s[1:]))
    if s and s[0]=='f':f.extend(int(i)-1 for i in s[1:])
   xml=ET.parse(folder/'geometry.scn').getroot();pos=list(map(float,xml.find('MechanicalObject').attrib['position'].split()))
   self.assertEqual(len(pos),len(v));self.assertLess(max(abs(a-b)for a,b in zip(pos,v)),1e-9)
   self.assertEqual(list(map(int,xml.find('MeshTopology').attrib['triangles'].split())),f)
 def test_material_and_actuator_constraints(self):
  folder=ROOT/'designs/selective_jamming/concept_v2';c=json.loads((folder/'parameters.json').read_text())
  self.assertEqual(sum(b-a for a,b in c['vacuum_zones_mm']),90)
  self.assertEqual(c['vacuum_circuits'],3);self.assertFalse(c['independent_finger_zone_control'])
  comparison=json.loads((ROOT/'designs/visualizations/concept_v2/comparison.json').read_text())
  self.assertGreater(comparison['candidates'][0]['material_volume_ratio'],5)
  self.assertIsNone(comparison['candidates'][0]['actual_contact_area_mm2'])
 def test_drawings_and_analytic_limits(self):
  for name in ('assembly_views.svg','mechanism_section.svg','sequence.svg'):ET.parse(ROOT/'designs/visualizations/concept_v2'/name)
  off=compliance([[0,100,1]]);self.assertAlmostEqual(off/compliance([[0,100,16]]),16)
  self.assertLess(off/compliance([[0,30,16],[30,100,1]]),16)
if __name__=='__main__':unittest.main()
