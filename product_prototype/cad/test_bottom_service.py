"""Bottom nut / cartridge maintenance geometry;not physical assembly approval."""
import json,unittest
from manufacturing_assembly import BASE

def result(name):return json.loads((BASE/'results'/name/'summary.json').read_text())

class BottomServiceTests(unittest.TestCase):
 def test_bottom_port_not_side_slot_or_captive_claim(self):
  cfg=json.loads((BASE/'config/distal_keeper_v54.json').read_text())
  self.assertFalse(cfg['design']['nut_side_entry_enabled'])
  self.assertLess(cfg['design']['nut_pocket_Z_mm'][0],cfg['design']['base_bottom_Z_mm'])
  self.assertIsNone(cfg['actual_retention_N']);self.assertFalse(cfg['fabrication_ready'])
  d=result('product_distal_bottom1018');self.assertEqual(d['candidate_part_count'],294)
  self.assertEqual(len(d['solid_intersections']),3);self.assertFalse(d['nut_antirotation_qualified'])
 def test_two_bottom_envelopes_and_actual_positions_clear_only(self):
  d=result('product_distal_bottom_service1019');rows=d['service_records']
  nuts=[r for r in rows if r['operation']=='NUT_CONTINUOUS_CONVEX_ENVELOPE_SCREWS_REMOVED']
  self.assertEqual(len(nuts),2);self.assertTrue(all(r['translation_local_mm']==[0,0,-4] and not r['intersections'] for r in nuts))
  actual=[r for r in rows if r['operation']=='ACTUAL_NUT_TRANSLATION_SAMPLED_ONLY']
  self.assertEqual(len(actual),14);self.assertFalse(any(r['intersections'] for r in actual))
  self.assertEqual(d['status'],'DISTAL_KEEPER_SERVICE_REVIEW')
 def test_cartridge_cut_explicit_and_all_neighbors_kept(self):
  d=result('product_distal_cartridge1020');sets=[set(d[n]) for n in ('moving_names','removed_names','fixed_names')]
  self.assertEqual(sum(map(len,sets)),d['assembly_part_count']);self.assertEqual(len(set.union(*sets)),d['assembly_part_count'])
  self.assertEqual(len(sets[1]),2);self.assertIn('f0_c0_root_mounted_bridge',sets[2]);self.assertIn('f1_c1_distal_NI000001_MAX_ENVELOPE',sets[2])
  self.assertEqual(len(d['records']),8);self.assertFalse(any(r['intersections'] for r in d['records']))
  self.assertFalse(d['actual_joint_cut_qualified']);self.assertFalse(d['physical_service_qualified'])
 def test_hull_warning_and_conditional_bench_samples_remain_separate(self):
  d=result('product_distal_cartridge_sweep1022');self.assertEqual(d['status'],'CARTRIDGE_CONVEX_SWEEP_REVIEW')
  self.assertEqual(len(d['records'][0]['intersections']),2)
  d=result('product_distal_bench_cover1023');self.assertTrue(d['records'][0]['intersections'])
  self.assertFalse(any(r['intersections'] for r in d['records'][1:]));self.assertFalse(d['physical_service_qualified'])
 def test_pack_uses_new_actual_config_not_old_v52_label(self):
  d=result('product_distal_bottom_pack1021');self.assertEqual(d['source_case'],'product_distal_bottom1018')
  self.assertEqual(d['configuration'],'config/distal_keeper_v54.json');self.assertEqual(d['saved_STL_count'],6)
  self.assertFalse(d['STEP_generated']);self.assertFalse(d['fabrication_ready'])
 def test_refinement_does_not_erase_degenerate_prism_questions(self):
  d=result('product_distal_cartridge_surface1024');self.assertEqual(d['status'],'CARTRIDGE_SURFACE_SWEEP_REVIEW')
  self.assertEqual(d['prior_hit_pairs'],2)
  self.assertEqual(sum(len(r['detail']['unresolved_prisms']) for r in d['records']),185)
  self.assertFalse(any(r['detail']['intersections'] or r['detail']['initial_intersections'] for r in d['records']))
 def test_hex_obstruction_is_not_torque_capacity(self):
  d=result('product_distal_nut_capture1026');self.assertEqual(len(d['rotation_samples']),24)
  self.assertFalse(any(r['intersections'] for r in d['rotation_samples'] if r['rotation_deg']==0))
  self.assertTrue(all(r['intersections'] for r in d['rotation_samples'] if r['rotation_deg']==30))
  self.assertIsNone(d['actual_preload_N']);self.assertFalse(d['actual_locking_or_torque_qualified'])
  self.assertAlmostEqual(d['bearing_reference']['unloaded_roof_gap_mm'],.05)
 def test_finite_loader_and_nut_actual_insertion_not_hidden_hardware(self):
  d=result('product_distal_nut_loader1028');rows=[r for r in d['records'] if 'translation_local_Z_mm' in r]
  self.assertEqual(len(rows),16);self.assertFalse(any(r['tool_intersections'] for r in rows))
  self.assertFalse(any(r['nut_intersections'] for r in rows if r['translation_local_Z_mm']<=0))
  self.assertTrue(all(r['nut_intersections'] for r in rows if r['translation_local_Z_mm']>0))
 def test_two_loaders_not_silently_assumed_simultaneously_usable(self):
  d=result('product_distal_nut_loader1028');self.assertEqual(d['required_operation'],'ONE_LOADER_AT_A_TIME')
  self.assertGreater(d['simultaneous_tool_intersections'][0]['signed_volume_mm3'],24)
  self.assertFalse(d['physical_service_qualified']);self.assertIsNone(d['actual_hand_force_N'])
 def test_loader_bore_allows_nominal_screw_not_preload_capacity(self):
  d=result('product_distal_nut_loader1028');rows=[r for r in d['records'] if r.get('operation')=='NOMINAL_FINAL_SCREW_VS_LOADER']
  self.assertEqual(len(rows),2);self.assertFalse(any(r['intersections'] for r in rows))
  self.assertEqual(len(d['saved_tool_positions']),2);self.assertIsNone(d['actual_strength_N'])
