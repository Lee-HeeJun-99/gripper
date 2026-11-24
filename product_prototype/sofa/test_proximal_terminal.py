import json,unittest,xml.etree.ElementTree as ET
from analyse import BASE

class TerminalTests(unittest.TestCase):
 def test_only_topology_changed(self):
  src=BASE/'results/b3_railback_grasp1001298';out=BASE/'results/b3_proximal_terminal1326';r=ET.parse(out/'scene.scn').getroot()
  cables=list(r.iter('CableConstraint'));self.assertEqual(len(cables),6)
  for n in r.iter():
   if n.tag=='CableConstraint':self.assertEqual(n.get('indices'),'0 1 2 3 4');n.set('indices','0 1 2 3 4 5')
   for k,v in list(n.attrib.items()):n.set(k,v.replace(str(out),str(src)))
  self.assertEqual(ET.tostring(r),ET.tostring(ET.parse(src/'scene.scn').getroot()))
 def test_positive_not_holding(self):
  d=json.loads((BASE/'results/b3_proximal_terminal1326/summary.json').read_text())
  self.assertEqual(d['status'],'BOUNDED_EXECUTION_ONLY');self.assertEqual(d['holding'],'NOT MEASURED')
  self.assertTrue(all(x['minimum_volume_ratio']>0 for x in d['quality']))
 def test_actual_matched_time(self):
  d=json.loads((BASE/'results/b3_proximal_terminal_assess1327/summary.json').read_text())
  a,b=d['records'];self.assertEqual(a['actual_time_s'],b['actual_time_s'])
  self.assertLess(b['skin_Fz_N'],a['skin_Fz_N']);self.assertEqual(d['physical_validation'],'NOT QUALIFIED')
 def test_later_not_improvement(self):
  d=json.loads((BASE/'results/b3_proximal_terminal_late1330/summary.json').read_text());a,b=d['records']
  self.assertEqual(a['actual_time_s'],b['actual_time_s']);self.assertLess(b['skin_Fz_N'],a['skin_Fz_N']);self.assertLess(b['skin_Fz_N'],.981)
 def test_virtual_work(self):
  d=json.loads((BASE/'results/b3_terminal_virtual_work1329/summary.json').read_text())
  for r in d['records']:
   self.assertLess(r['gradient_FD_max_abs_error'],1e-7)
   self.assertAlmostEqual(r['last_98mm_guide_force_norm_N'],0 if '1326'in r['case'] else 1.5,places=12)
if __name__=='__main__':unittest.main()
