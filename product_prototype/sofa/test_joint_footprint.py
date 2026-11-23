"""Saved Native candidate scope and single-variable construction regressions."""
import json,unittest
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE

class FootprintTests(unittest.TestCase):
    def test_ownership_and_physical_inputs(self):
        for name,original in [('b3_footprint_force1153','b3_rail_back_hold1129'),('b3_footprint_half1154','b3_rail_back_half1130')]:
            folder=BASE/'results'/name
            pre=json.loads((folder/'preflight.json').read_text())
            self.assertEqual([c['guide'] for c in pre['changes']],[3,9])
            self.assertGreater(min(pre['twice_triangle_areas_m2']),0)
            root=ET.parse(folder/'scene.scn').getroot(); old=ET.parse(BASE/'results'/original/'scene.scn').getroot()
            pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2)
            self.assertEqual(len(set(pairs[pairs[:,0]==1,1])),36)
            for kind in ('TetrahedronFEMForceField','UniformMass','DiagonalMass','NativeCableSequence'):
                # Only the journal destination differs between immutable cases.
                attrs=lambda r:[{k:v for k,v in e.attrib.items() if k!='filename'} for e in r.iter(kind)]
                self.assertEqual(attrs(root),attrs(old))
    def test_no_qualification_upgrade(self):
        s=json.loads((BASE/'results/b3_footprint_assess1155/summary.json').read_text())
        self.assertEqual(s['status'],'FAIL_TIME_PAIR_GATE')
        self.assertEqual(s['physical_validation'],'NOT QUALIFIED')
        self.assertIsNone(s['energy_work'])
        self.assertEqual(s['holding'],'NOT RUN')
        for key in s['comparisons']:self.assertEqual(s['comparisons'][key]['gate'],.001)

if __name__=='__main__':unittest.main()
