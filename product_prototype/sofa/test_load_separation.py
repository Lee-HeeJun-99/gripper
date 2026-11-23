import json,unittest
import xml.etree.ElementTree as ET
from analyse import BASE

class LoadSeparationTests(unittest.TestCase):
    def test_only_dt_input_and_journal_destination_change(self):
        cases=['b3_rail_back_hold1129','b3_rail_back_half1130','b3_rail_back_zero1127','b3_rail_back_zero_half1157'];normalized=[]
        for case in cases:
            folder=BASE/'results'/case;root=ET.parse(folder/'scene.scn').getroot();root.set('dt','DT')
            for n in root.iter():
                if n.tag=='NativeCableSequence':n.set('maximumForceN','INPUT')
                for k,v in list(n.attrib.items()):n.set(k,v.replace(str(folder),'CASE'))
            normalized.append(ET.tostring(root))
        for scene in normalized[1:]:self.assertEqual(scene,normalized[0])
    def test_no_causal_or_physical_upgrade(self):
        d=json.loads((BASE/'results/b3_load_separation1158/summary.json').read_text());f=d['first_common_output']
        self.assertGreater(f['gravity_only_pair_difference_m'],1e-5)
        self.assertLess(f['difference_of_input_responses_m'],2e-8)
        self.assertEqual(d['physical_validation'],'NOT QUALIFIED');self.assertIsNone(d['energy_work'])

if __name__=='__main__':unittest.main()
