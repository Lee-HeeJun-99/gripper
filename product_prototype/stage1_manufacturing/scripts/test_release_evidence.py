import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EvidenceTests(unittest.TestCase):
 def data(self,p):return json.loads((ROOT/p).read_text())
 def test_release_is_closed(self):
  d=self.data('validation/release_revH/summary.json');self.assertEqual(d['status'],'STAGE1_DESIGN_RELEASE_FAIL');self.assertFalse(all(d['criteria'].values()))
 def test_part_files_and_topology(self):
  d=self.data('cad/exports/revH/audit.json');self.assertEqual(len(d['parts']),157);self.assertFalse(d['collisions'])
  for p in d['parts']:
   self.assertEqual(p['solid_count'],1)
   for ext in ('step','stl'):self.assertTrue((ROOT/f'cad/exports/revH/{p["id"]}.{ext}').is_file())
 def test_independent_wire_and_cutset(self):
  d=self.data('validation/service_revH_completed/summary.json');self.assertEqual(len(d['straight_REST_wire_spans']),6);self.assertFalse(any(p['hits'] for p in d['straight_REST_wire_spans']));self.assertFalse(d['cartridge']['collision_samples']);self.assertTrue(d['cartridge']['cutset']);self.assertFalse(any(p['staged_hits'] for p in d['motor_tools']))
 def test_motion_does_not_hide_collision(self):
  d=self.data('validation/motion_revH_rootdatum_v2/summary.json');self.assertTrue(d['all_meshes_watertight']);self.assertFalse(d['foreign_rotor_hits']);self.assertEqual(min(p['angle_deg'] for p in d['prescribed_finger_hits']),58);self.assertFalse(d['continuous_CCD'])
 def test_old_failure_is_retained(self):
  for rev,n in [('revA',21),('revC',12),('revD',6),('revE',3)]:self.assertEqual(len(self.data(f'cad/exports/{rev}/audit.json')['collisions']),n)
if __name__=='__main__':unittest.main()
